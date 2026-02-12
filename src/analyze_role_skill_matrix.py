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


def split_skill_list(s: str) -> list[str]:
    if s is None:
        return []
    t = str(s).strip()
    if t == "" or t.lower() in {"nan", "none"}:
        return []
    parts = [p.strip() for p in t.split("|")]
    return [p for p in parts if p]


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=str, default="outputs/ads_enriched.csv", help="Enriched ads CSV")
    parser.add_argument("--skills-meta", type=str, default="outputs/skills_counts.csv", help="Skill meta (group/category/parent)")
    parser.add_argument("--skills-col", type=str, default="skills_extracted", help="Which extracted skills column to use")
    parser.add_argument("--role-col", type=str, default="job_role_fa", help="Role column name")
    parser.add_argument("--out", type=str, default="outputs/role_skill_all.csv", help="Output CSV (long)")
    parser.add_argument("--pivot-out", type=str, default="outputs/role_skill_all_pivot.csv", help="Wide pivot (pct_of_role)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    in_path = (root / args.inputs).resolve()
    meta_path = (root / args.skills_meta).resolve()
    out_path = (root / args.out).resolve()
    pivot_path = (root / args.pivot_out).resolve()

    if not in_path.exists():
        raise FileNotFoundError(f"Missing input: {in_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing skills meta: {meta_path}")

    ads = pd.read_csv(in_path, encoding="utf-8-sig")
    meta = pd.read_csv(meta_path, encoding="utf-8-sig").drop_duplicates(subset=["skill"])

    if "_ad_key" in ads.columns:
        ads = ads.drop_duplicates(subset=["_ad_key"], keep="first").copy()
        ad_id_col = "_ad_key"
    else:
        ads = ads.copy()
        ads["_ad_id"] = ads.index.astype(str)
        ad_id_col = "_ad_id"

    if args.role_col not in ads.columns:
        raise ValueError(f"Missing role column: {args.role_col}. Available: {ads.columns.tolist()}")
    if args.skills_col not in ads.columns:
        raise ValueError(f"Missing skills column: {args.skills_col}. Available: {ads.columns.tolist()}")

    d = ads[[ad_id_col, args.role_col, args.skills_col]].copy()
    d[args.role_col] = d[args.role_col].fillna("نامشخص").astype(str).map(normalize_text)
    d["_skills"] = d[args.skills_col].fillna("").map(split_skill_list)
    long = d[[ad_id_col, args.role_col, "_skills"]].explode("_skills").rename(columns={"_skills": "skill"})
    long["skill"] = long["skill"].fillna("").astype(str).map(lambda x: x.strip())
    long = long[long["skill"].ne("")].copy()

    if long.empty:
        raise RuntimeError("No extracted skills found to analyze.")

  
    rs = (
        long.drop_duplicates(subset=[ad_id_col, args.role_col, "skill"])
        .groupby([args.role_col, "skill"], as_index=False)
        .size()
        .rename(columns={"size": "n_ads"})
    )

    role_tot = (
        long.drop_duplicates(subset=[ad_id_col, args.role_col])
        .groupby(args.role_col, as_index=False)
        .size()
        .rename(columns={"size": "n_ads_role"})
    )
    rs = rs.merge(role_tot, on=args.role_col, how="left")
    rs["pct_of_role"] = (rs["n_ads"] / rs["n_ads_role"].clip(lower=1)).round(4)

    global_tot = (
        long.drop_duplicates(subset=[ad_id_col, "skill"])
        .groupby("skill", as_index=False)
        .size()
        .rename(columns={"size": "n_ads_global"})
    )
    rs = rs.merge(global_tot, on="skill", how="left")

    
    keep_meta = [c for c in ["skill", "group", "category", "parent"] if c in meta.columns]
    rs = rs.merge(meta[keep_meta], on="skill", how="left")

    rs = rs.sort_values([args.role_col, "pct_of_role", "n_ads"], ascending=[True, False, False])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rs.to_csv(out_path, index=False, encoding="utf-8-sig")

   
    pv = rs.pivot_table(index=args.role_col, columns="skill", values="pct_of_role", aggfunc="max", fill_value=0.0)
    pv = pv.sort_index()
    pv.to_csv(pivot_path, encoding="utf-8-sig")

    print(" Saved:", out_path)
    print(" Saved:", pivot_path)
    print("Roles:", rs[args.role_col].nunique(), "Skills:", rs["skill"].nunique())


if __name__ == "__main__":
    main()

