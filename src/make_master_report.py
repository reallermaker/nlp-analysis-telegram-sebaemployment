from __future__ import annotations

from pathlib import Path
import argparse
import datetime as dt
import json
import sys

import pandas as pd


def configure_stdout():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def add_meta(rows: list[dict], key: str, value, note: str = ""):
    rows.append(
        {
            "section": "meta",
            "subsection": "",
            "item": key,
            "rank": 0,
            "n_ads": pd.NA,
            "pct": pd.NA,
            "lift": pd.NA,
            "value": value,
            "note": note,
        }
    )


def add_file_manifest(rows: list[dict], outputs_dir: Path, rel_paths: list[str]):
    for rel in rel_paths:
        p = (outputs_dir / rel).resolve()
        if not p.exists():
            rows.append(
                {
                    "section": "file_manifest",
                    "subsection": "",
                    "item": rel,
                    "rank": 0,
                    "n_ads": pd.NA,
                    "pct": pd.NA,
                    "lift": pd.NA,
                    "value": pd.NA,
                    "note": "missing",
                }
            )
            continue

        st = p.stat()
        rows.append(
            {
                "section": "file_manifest",
                "subsection": "",
                "item": rel,
                "rank": 0,
                "n_ads": pd.NA,
                "pct": pd.NA,
                "lift": pd.NA,
                "value": int(st.st_size),
                "note": f"mtime={dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')}",
            }
        )


def add_catalog_rows(df: pd.DataFrame, section: str) -> list[dict]:
    if df is None or df.empty:
        return []
    out = []
    for _, r in df.iterrows():
        row = {
            "section": section,
            "subsection": r.get("family_fa", "") if "family_fa" in df.columns else "",
            "item": r.get("role_fa", "") if "role_fa" in df.columns else r.get("family_fa", ""),
            "rank": pd.NA,
            "n_ads": pd.NA,
            "pct": pd.NA,
            "lift": pd.NA,
            "value": pd.NA,
            "note": "",
        }
        for c in df.columns:
            if c in {"family_fa", "role_fa"}:
                continue
            row[f"extra_{c}"] = r.get(c, pd.NA)
        out.append(row)
    return out


def ranked_counts(
    df: pd.DataFrame,
    section: str,
    item_col: str,
    n_col: str,
    total_ads: int | None,
    top_n: int | None = 30,
    subsection: str = "",
    extra_cols: list[str] | None = None,
) -> list[dict]:
    if df is None or df.empty or item_col not in df.columns or n_col not in df.columns:
        return []

    extra_cols = extra_cols or []
    d = df.copy()
    d[item_col] = d[item_col].astype(str)
    d[n_col] = pd.to_numeric(d[n_col], errors="coerce").fillna(0)
    d = d.sort_values(n_col, ascending=False)
    if top_n is not None:
        d = d.head(int(top_n))

    out = []
    for idx, (_, r) in enumerate(d.iterrows(), start=1):
        n = float(r[n_col])
        pct = (n / total_ads) if (total_ads and total_ads > 0) else pd.NA
        row = {
            "section": section,
            "subsection": subsection,
            "item": r[item_col],
            "rank": idx,
            "n_ads": int(n),
            "pct": round(float(pct), 6) if pct is not pd.NA else pd.NA,
            "lift": pd.NA,
            "value": pd.NA,
            "note": "",
        }
        for c in extra_cols:
            if c in r.index:
                row[f"extra_{c}"] = r[c]
        out.append(row)
    return out


def wide_top_list_to_long(
    df: pd.DataFrame,
    section: str,
    group_col: str,
    prefix: str,
    total_col: str | None = None,
    total_ads: int | None = None,
    max_k: int = 25,
) -> list[dict]:
    if df is None or df.empty or group_col not in df.columns:
        return []

    out: list[dict] = []
    for _, row in df.iterrows():
        group_val = str(row.get(group_col, ""))
        total = row.get(total_col) if (total_col and total_col in df.columns) else pd.NA
        for k in range(1, max_k + 1):
            item = row.get(f"{prefix}_{k}", pd.NA)
            if pd.isna(item) or str(item).strip() == "":
                continue
            n = row.get(f"n_{k}", pd.NA)
            pct = row.get(f"pct_{k}", pd.NA)
            lift = row.get(f"lift_{k}", pd.NA)

            if pd.isna(pct) and (total_ads and total_ads > 0) and not pd.isna(n):
                try:
                    pct = float(n) / float(total_ads)
                except Exception:
                    pct = pd.NA

            out.append(
                {
                    "section": section,
                    "subsection": group_val,
                    "item": str(item),
                    "rank": k,
                    "n_ads": int(n) if not pd.isna(n) else pd.NA,
                    "pct": float(pct) if not pd.isna(pct) else pd.NA,
                    "lift": float(lift) if not pd.isna(lift) else pd.NA,
                    "value": int(total) if not pd.isna(total) else pd.NA,
                    "note": "",
                }
            )
    return out


def role_skill_long(df: pd.DataFrame, total_ads: int | None, top_roles: int = 12, top_skills: int = 25) -> list[dict]:
    if df is None or df.empty:
        return []

    role_col = "عنوان_شغل_استاندارد" if "عنوان_شغل_استاندارد" in df.columns else None
    required = {role_col, "skill", "n_ads", "pct_of_role", "lift"} if role_col else set()
    if not role_col or not required.issubset(set(df.columns)):
        return []

    totals = df[[role_col, "n_ads_role"]].drop_duplicates().sort_values("n_ads_role", ascending=False).head(int(top_roles))
    top_role_vals = totals[role_col].astype(str).tolist()

    skills = (
        df[["skill", "n_ads_global"]]
        .drop_duplicates()
        .sort_values("n_ads_global", ascending=False)
        .head(int(top_skills))
    )
    top_skill_vals = skills["skill"].astype(str).tolist()

    d = df[df[role_col].astype(str).isin(top_role_vals) & df["skill"].astype(str).isin(top_skill_vals)].copy()
    if d.empty:
        return []

    d = d.sort_values([role_col, "pct_of_role", "n_ads"], ascending=[True, False, False])
    out: list[dict] = []
    for _, r in d.iterrows():
        out.append(
            {
                "section": "role_skill",
                "subsection": str(r[role_col]),
                "item": str(r["skill"]),
                "rank": pd.NA,
                "n_ads": int(r["n_ads"]) if not pd.isna(r["n_ads"]) else pd.NA,
                "pct": float(r["pct_of_role"]) if not pd.isna(r["pct_of_role"]) else pd.NA,
                "lift": float(r["lift"]) if not pd.isna(r["lift"]) else pd.NA,
                "value": int(r["n_ads_role"]) if not pd.isna(r["n_ads_role"]) else pd.NA,
                "note": json.dumps(
                    {
                        "group": r.get("group", None),
                        "category": r.get("category", None),
                        "parent": r.get("parent", None),
                        "n_ads_global": r.get("n_ads_global", None),
                    },
                    ensure_ascii=False,
                ),
            }
        )
    return out


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", type=str, default="outputs")
    parser.add_argument("--out", type=str, default="outputs/master_report.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_dir = (root / args.outputs_dir).resolve()
    out_path = (root / args.out).resolve()

    rows: list[dict] = []
    add_meta(rows, "generated_at", dt.datetime.now().isoformat(timespec="seconds"))

    # Prefer enriched dataset for totals.
    total_ads = None
    enriched_path = out_dir / "ads_enriched.csv"
    if enriched_path.exists():
        enriched = load_csv(enriched_path)
        total_ads = int(enriched.drop_duplicates(subset=["_ad_key"]).shape[0]) if "_ad_key" in enriched.columns else int(len(enriched))
        add_meta(rows, "total_ads", total_ads)
    else:
        add_meta(rows, "total_ads", pd.NA, note="Missing outputs/ads_enriched.csv")

    add_file_manifest(
        rows,
        out_dir,
        rel_paths=[
            "ads_parsed_all.csv",
            "ads_with_job_titles.csv",
            "ads_with_skills.csv",
            "ads_with_locations.csv",
            "ads_enriched.csv",
            "skills_counts.csv",
            "job_role_counts_fa.csv",
            "job_family_counts_fa.csv",
            "province_counts.csv",
            "city_counts.csv",
            "tehran_neighborhood_counts.csv",
            "tehran_district_counts.csv",
            "role_skill_counts.csv",
            "role_skill_lift_core.csv",
            "role_top_skills.csv",
            "role_top_skills_lift.csv",
            "skill_group_counts.csv",
            "skill_category_counts.csv",
            "role_skill_group_counts.csv",
            "family_skill_group_counts.csv",
            "certificates_counts.csv",
            "certificates_by_role.csv",
            "certificates_top_roles.csv",
            "province_top_roles.csv",
            "tehran_neighborhood_top_roles.csv",
            "tehran_district_top_roles.csv",
            "job_family_catalog.csv",
            "job_role_catalog.csv",
        ],
    )

    
    fam_catalog = out_dir / "job_family_catalog.csv"
    if fam_catalog.exists():
        rows += add_catalog_rows(load_csv(fam_catalog), "job_family_catalog")

    role_catalog = out_dir / "job_role_catalog.csv"
    if role_catalog.exists():
        rows += add_catalog_rows(load_csv(role_catalog), "job_role_catalog")

    
    skills_counts = out_dir / "skills_counts.csv"
    if skills_counts.exists():
        df = load_csv(skills_counts)
        rows += ranked_counts(df, "skills", "skill", "n_ads", total_ads, top_n=50, extra_cols=["category", "group", "parent"])

    skill_group_counts = out_dir / "skill_group_counts.csv"
    if skill_group_counts.exists():
        df = load_csv(skill_group_counts)
        rows += ranked_counts(df, "skill_groups", "group", "n_ads", total_ads, top_n=None)

    skill_category_counts = out_dir / "skill_category_counts.csv"
    if skill_category_counts.exists():
        df = load_csv(skill_category_counts)
        rows += ranked_counts(df, "skill_categories", "category", "n_ads", total_ads, top_n=None)

    certificates_counts = out_dir / "certificates_counts.csv"
    if certificates_counts.exists():
        df = load_csv(certificates_counts)
        rows += ranked_counts(df, "certificates", "skill", "n_ads", total_ads, top_n=30)

    role_counts = out_dir / "job_role_counts_fa.csv"
    if role_counts.exists():
        df = load_csv(role_counts)
        if df.shape[1] >= 2:
            rows += ranked_counts(df, "job_roles", df.columns[0], df.columns[1], total_ads, top_n=50)

    fam_counts = out_dir / "job_family_counts_fa.csv"
    if fam_counts.exists():
        df = load_csv(fam_counts)
        if df.shape[1] >= 2:
            rows += ranked_counts(df, "job_families", df.columns[0], df.columns[1], total_ads, top_n=30)

    prov_counts = out_dir / "province_counts.csv"
    if prov_counts.exists():
        df = load_csv(prov_counts)
        rows += ranked_counts(df, "provinces", "province", "n_ads", total_ads, top_n=40)

    city_counts = out_dir / "city_counts.csv"
    if city_counts.exists():
        df = load_csv(city_counts)
        rows += ranked_counts(df, "cities", "city", "n_ads", total_ads, top_n=60)

    tehran_nei_counts = out_dir / "tehran_neighborhood_counts.csv"
    if tehran_nei_counts.exists():
        df = load_csv(tehran_nei_counts)
        rows += ranked_counts(df, "tehran_neighborhoods", "tehran_neighborhood", "n_ads", total_ads, top_n=80)

    tehran_dist_counts = out_dir / "tehran_district_counts.csv"
    if tehran_dist_counts.exists():
        df = load_csv(tehran_dist_counts)
        rows += ranked_counts(df, "tehran_districts", "tehran_district", "n_ads", total_ads, top_n=40)

    
    jt_clean = out_dir / "job_title_clean_counts.csv"
    if jt_clean.exists():
        df = load_csv(jt_clean)
        rows += ranked_counts(df, "job_titles_raw", "job_title_clean", "n_ads", total_ads, top_n=200)

    
    prov_top_roles = out_dir / "province_top_roles.csv"
    if prov_top_roles.exists():
        df = load_csv(prov_top_roles)
        rows += wide_top_list_to_long(df, "province_top_roles", group_col="province", prefix="role", total_col="n_ads_total", total_ads=total_ads, max_k=10)

    teh_top_roles = out_dir / "tehran_neighborhood_top_roles.csv"
    if teh_top_roles.exists():
        df = load_csv(teh_top_roles)
        rows += wide_top_list_to_long(df, "tehran_neighborhood_top_roles", group_col="tehran_neighborhood", prefix="role", total_col="n_ads_total", total_ads=total_ads, max_k=10)

    dist_top_roles = out_dir / "tehran_district_top_roles.csv"
    if dist_top_roles.exists():
        df = load_csv(dist_top_roles)
        rows += wide_top_list_to_long(df, "tehran_district_top_roles", group_col="tehran_district", prefix="role", total_col="n_ads_total", total_ads=total_ads, max_k=10)

    
    role_top_skills = out_dir / "role_top_skills.csv"
    if role_top_skills.exists():
        df = load_csv(role_top_skills)
        if "عنوان_شغل_استاندارد" in df.columns:
            rows += wide_top_list_to_long(
                df,
                "role_top_skills",
                group_col="عنوان_شغل_استاندارد",
                prefix="skill",
                total_col="تعداد_آگهی_نقش",
                total_ads=total_ads,
                max_k=15,
            )

    role_top_skills_lift = out_dir / "role_top_skills_lift.csv"
    if role_top_skills_lift.exists():
        df = load_csv(role_top_skills_lift)
        if "عنوان_شغل_استاندارد" in df.columns:
            rows += wide_top_list_to_long(
                df,
                "role_top_skills_lift",
                group_col="عنوان_شغل_استاندارد",
                prefix="skill",
                total_col="تعداد_آگهی_نقش",
                total_ads=total_ads,
                max_k=15,
            )

    
    role_skill_path = out_dir / "role_skill_lift_core.csv"
    if not role_skill_path.exists():
        role_skill_path = out_dir / "role_skill_counts.csv"
    if role_skill_path.exists():
        df = load_csv(role_skill_path)
        rows += role_skill_long(df, total_ads, top_roles=12, top_skills=25)


    role_skill_group_counts = out_dir / "role_skill_group_counts.csv"
    if role_skill_group_counts.exists():
        df = load_csv(role_skill_group_counts)
        rows += ranked_counts(df, "role_skill_groups", "group", "n_ads", total_ads, top_n=None, extra_cols=["job_role_fa", "n_ads_role", "pct_of_role"])

    family_skill_group_counts = out_dir / "family_skill_group_counts.csv"
    if family_skill_group_counts.exists():
        df = load_csv(family_skill_group_counts)
        
        rows += ranked_counts(df, "family_skill_groups", "group", "n_ads", total_ads, top_n=None, extra_cols=["job_family_fa", "n_ads_family", "pct_of_family"])

    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("No report rows produced. Check outputs directory.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print("Saved:", out_path)
    print("Rows:", len(out))


if __name__ == "__main__":
    main()
