from __future__ import annotations

from pathlib import Path
import argparse
import re
import html as htmllib
import sys

import pandas as pd


PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
ARABIC_LETTERS = str.maketrans({"ي": "ی", "ك": "ک", "ة": "ه", "ۀ": "ه", "ؤ": "و", "إ": "ا", "أ": "ا"})


def configure_stdout():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def normalize_text(s: str) -> str:
    s = htmllib.unescape(s or "")
    s = s.translate(ARABIC_LETTERS).translate(PERSIAN_DIGITS).translate(ARABIC_DIGITS)
    s = s.replace("\u200c", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_ad_id(df: pd.DataFrame) -> pd.Series:
    if "source_file" in df.columns and "date_title" in df.columns:
        return df["source_file"].astype(str) + "|" + df["date_title"].astype(str)
    return df.index.astype(str)


def split_skill_list(s: str) -> list[str]:
    if s is None:
        return []
    t = str(s).strip()
    if t == "" or t.lower() in {"nan", "none"}:
        return []
    parts = [p.strip() for p in t.split("|")]
    return [p for p in parts if p]


def counts_unique(df: pd.DataFrame, keys: list[str], out_cols: list[str]):
    d = df.drop_duplicates(subset=keys).copy()
    g = d.groupby(out_cols, as_index=False).size().rename(columns={"size": "n_ads"})
    return g.sort_values("n_ads", ascending=False)


def attach_totals_and_pct(df_long: pd.DataFrame, group_cols: list[str], count_col: str = "n_ads") -> pd.DataFrame:
    if df_long is None or df_long.empty:
        return df_long
    totals = df_long.groupby(group_cols, as_index=False)[count_col].sum().rename(columns={count_col: f"{count_col}_total"})
    out = df_long.merge(totals, on=group_cols, how="left")
    out["pct_of_total"] = (out[count_col] / out[f"{count_col}_total"].clip(lower=1)).round(4)
    return out


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=str, default="outputs/ads_enriched.csv", help="Enriched ads CSV (includes skills)")
    parser.add_argument("--skills-meta", type=str, default="outputs/skills_counts.csv", help="Skill metadata with group/category")
    parser.add_argument("--skills-col", type=str, default="skills_extracted", help="Which skills column to use")
    parser.add_argument("--out-dir", type=str, default="outputs", help="Output directory")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    in_path = (root / args.inputs).resolve()
    meta_path = (root / args.skills_meta).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(f"Missing input: {in_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing skills meta: {meta_path}")

    ads = pd.read_csv(in_path, encoding="utf-8-sig")
    meta = pd.read_csv(meta_path, encoding="utf-8-sig")
    meta = meta.drop_duplicates(subset=["skill"])

    if args.skills_col not in ads.columns:
        raise ValueError(f"Missing skills column: {args.skills_col}. Available: {ads.columns.tolist()}")

    # Normalize role/family fields if present
    role_col = "job_role_fa" if "job_role_fa" in ads.columns else ("عنوان_شغل_استاندارد" if "عنوان_شغل_استاندارد" in ads.columns else None)
    fam_col = "job_family_fa" if "job_family_fa" in ads.columns else ("خانواده_شغلی" if "خانواده_شغلی" in ads.columns else None)

    ads["_ad_id"] = build_ad_id(ads)
    ads["_skills_list"] = ads[args.skills_col].fillna("").map(split_skill_list)

    long = ads[["_ad_id"] + ([role_col] if role_col else []) + ([fam_col] if fam_col else []) + ["province", "city", "tehran_district", "tehran_neighborhood", "_skills_list"]].copy()
    long = long.explode("_skills_list").rename(columns={"_skills_list": "skill"})
    long["skill"] = long["skill"].fillna("").astype(str).map(lambda x: x.strip())
    long = long[long["skill"].astype(str).ne("")].copy()

    if long.empty:
        raise RuntimeError("No skills found to analyze. Check extracted skills columns in ads_enriched.")

    keep_meta_cols = [c for c in ["skill", "group", "category", "parent"] if c in meta.columns]
    long = long.merge(meta[keep_meta_cols], on="skill", how="left")
    long["group"] = long["group"].fillna("unknown").astype(str)
    long["category"] = long["category"].fillna("unknown").astype(str)

    group_counts = counts_unique(long, ["_ad_id", "group"], ["group"])
    group_counts.to_csv(out_dir / "skill_group_counts.csv", index=False, encoding="utf-8-sig")

    cat_counts = counts_unique(long, ["_ad_id", "category"], ["category"])
    cat_counts.to_csv(out_dir / "skill_category_counts.csv", index=False, encoding="utf-8-sig")

    
    if role_col:
        rg = counts_unique(long, ["_ad_id", role_col, "group"], [role_col, "group"])
        role_tot = counts_unique(long, ["_ad_id", role_col], [role_col]).rename(columns={"n_ads": "n_ads_role"})
        rg = rg.merge(role_tot, on=role_col, how="left")
        rg["pct_of_role"] = (rg["n_ads"] / rg["n_ads_role"].clip(lower=1)).round(4)
        rg = rg.sort_values([role_col, "n_ads"], ascending=[True, False])
        rg.to_csv(out_dir / "role_skill_group_counts.csv", index=False, encoding="utf-8-sig")

        rc = counts_unique(long, ["_ad_id", role_col, "category"], [role_col, "category"])
        rc = rc.merge(role_tot, on=role_col, how="left")
        rc["pct_of_role"] = (rc["n_ads"] / rc["n_ads_role"].clip(lower=1)).round(4)
        rc = rc.sort_values([role_col, "n_ads"], ascending=[True, False])
        rc.to_csv(out_dir / "role_skill_category_counts.csv", index=False, encoding="utf-8-sig")

    if fam_col:
        fg = counts_unique(long, ["_ad_id", fam_col, "group"], [fam_col, "group"])
        fam_tot = counts_unique(long, ["_ad_id", fam_col], [fam_col]).rename(columns={"n_ads": "n_ads_family"})
        fg = fg.merge(fam_tot, on=fam_col, how="left")
        fg["pct_of_family"] = (fg["n_ads"] / fg["n_ads_family"].clip(lower=1)).round(4)
        fg = fg.sort_values([fam_col, "n_ads"], ascending=[True, False])
        fg.to_csv(out_dir / "family_skill_group_counts.csv", index=False, encoding="utf-8-sig")

        fc = counts_unique(long, ["_ad_id", fam_col, "category"], [fam_col, "category"])
        fc = fc.merge(fam_tot, on=fam_col, how="left")
        fc["pct_of_family"] = (fc["n_ads"] / fc["n_ads_family"].clip(lower=1)).round(4)
        fc = fc.sort_values([fam_col, "n_ads"], ascending=[True, False])
        fc.to_csv(out_dir / "family_skill_category_counts.csv", index=False, encoding="utf-8-sig")

   
    cert = long[long["group"].astype(str).eq("certificate") & long["category"].astype(str).eq("capital_market")].copy()
    if not cert.empty:
        cert_counts = counts_unique(cert, ["_ad_id", "skill"], ["skill"])
        cert_counts.to_csv(out_dir / "certificates_counts.csv", index=False, encoding="utf-8-sig")

        if role_col:
            cr = counts_unique(cert, ["_ad_id", role_col, "skill"], [role_col, "skill"])
            role_tot = counts_unique(long, ["_ad_id", role_col], [role_col]).rename(columns={"n_ads": "n_ads_role"})
            cr = cr.merge(role_tot, on=role_col, how="left")
            cr["pct_of_role"] = (cr["n_ads"] / cr["n_ads_role"].clip(lower=1)).round(4)
            cr = cr.sort_values([role_col, "n_ads"], ascending=[True, False])
            cr.to_csv(out_dir / "certificates_by_role.csv", index=False, encoding="utf-8-sig")

            cc = counts_unique(cert, ["_ad_id", role_col, "skill"], ["skill", role_col])
            cert_tot = counts_unique(cert, ["_ad_id", "skill"], ["skill"]).rename(columns={"n_ads": "n_ads_cert"})
            cc = cc.merge(cert_tot, on="skill", how="left")
            cc["pct_of_cert"] = (cc["n_ads"] / cc["n_ads_cert"].clip(lower=1)).round(4)
            cc = cc.sort_values(["skill", "n_ads"], ascending=[True, False])
            cc.to_csv(out_dir / "certificates_top_roles.csv", index=False, encoding="utf-8-sig")

    print("✅ Saved:")
    for name in [
        "skill_group_counts.csv",
        "skill_category_counts.csv",
        "role_skill_group_counts.csv",
        "role_skill_category_counts.csv",
        "family_skill_group_counts.csv",
        "family_skill_category_counts.csv",
        "certificates_counts.csv",
        "certificates_by_role.csv",
        "certificates_top_roles.csv",
    ]:
        p = out_dir / name
        if p.exists():
            print("-", p)


if __name__ == "__main__":
    main()
