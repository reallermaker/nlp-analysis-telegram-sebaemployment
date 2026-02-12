from __future__ import annotations

from pathlib import Path
import argparse
import sys

import pandas as pd


KEY_COLS = ["source_file", "message_ids", "group_index", "date_title"]

ROLE_COL_CANDIDATES = [
    "عنوان_شغل_استاندارد",
    "job_role_fa",
    "job_role",
    "job_title_std",
    "role_std",
]


def configure_stdout():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_cols(cols: list[str]) -> list[str]:
    return [str(c).encode("unicode_escape").decode("ascii") for c in cols]


def build_ad_key(df: pd.DataFrame) -> pd.Series:
    missing = [c for c in KEY_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required key columns: {missing}")

    key = df[KEY_COLS[0]].fillna("").astype(str)
    for c in KEY_COLS[1:]:
        key = key + "|" + df[c].fillna("").astype(str)
    return key


def pick_existing_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def group_counts(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    return (
        df.groupby(by, as_index=False)
        .size()
        .rename(columns={"size": "n_ads"})
        .sort_values("n_ads", ascending=False)
    )


def top_roles_wide(df_counts: pd.DataFrame, group_col: str, role_col: str, top_n: int) -> pd.DataFrame:
    d = df_counts.copy()
    totals = d.groupby(group_col, as_index=False)["n_ads"].sum().rename(columns={"n_ads": "n_ads_total"})
    d = d.merge(totals, on=group_col, how="left")
    d = d.sort_values([group_col, "n_ads"], ascending=[True, False])
    d["rank"] = d.groupby(group_col).cumcount() + 1
    d = d[d["rank"] <= top_n].copy()
    d["pct"] = (d["n_ads"] / d["n_ads_total"].clip(lower=1)).round(4)

    rows = []
    for grp, g in d.groupby(group_col):
        row = {group_col: grp, "n_ads_total": int(g["n_ads_total"].iloc[0])}
        for i, (_, r) in enumerate(g.iterrows(), start=1):
            row[f"role_{i}"] = r[role_col]
            row[f"n_{i}"] = int(r["n_ads"])
            row[f"pct_{i}"] = float(r["pct"])
        rows.append(row)

    out = pd.DataFrame(rows).sort_values("n_ads_total", ascending=False)
    return out


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--locs", type=str, default="outputs/ads_with_locations.csv")
    parser.add_argument("--jobs", type=str, default="outputs/ads_with_job_titles.csv")
    parser.add_argument("--out-dir", type=str, default="outputs")
    parser.add_argument("--top-n", type=int, default=5, help="Top roles to keep in *_top_roles.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    locs_path = (root / args.locs).resolve()
    jobs_path = (root / args.jobs).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not locs_path.exists():
        raise FileNotFoundError(f"Locations file not found: {locs_path}")
    if not jobs_path.exists():
        raise FileNotFoundError(f"Jobs file not found: {jobs_path}")

    locs = pd.read_csv(locs_path, encoding="utf-8-sig")
    jobs = pd.read_csv(jobs_path, encoding="utf-8-sig")

    role_col = pick_existing_col(jobs, ROLE_COL_CANDIDATES)
    if role_col is None:
        raise ValueError(f"Role column not found. Candidates: {ROLE_COL_CANDIDATES}. Seen: {safe_cols(list(jobs.columns))}")

    # Minimal merge for geo-role counts.
    locs["_ad_key"] = build_ad_key(locs)
    jobs["_ad_key"] = build_ad_key(jobs)

    geo_cols = ["_ad_key", "province", "city", "tehran_district", "tehran_neighborhood"]
    geo_cols = [c for c in geo_cols if c in locs.columns]
    locs_m = locs[geo_cols].drop_duplicates(subset=["_ad_key"], keep="first")

    jobs_m = jobs[["_ad_key", role_col]].drop_duplicates(subset=["_ad_key"], keep="first")
    df = locs_m.merge(jobs_m, on="_ad_key", how="left")

    df = df.rename(columns={role_col: "job_role"})

    # Province x role
    if "province" in df.columns:
        prov_role = group_counts(df.dropna(subset=["province", "job_role"]), ["province", "job_role"])
        prov_role.to_csv(out_dir / "province_role_counts.csv", index=False, encoding="utf-8-sig")
        top_prov = top_roles_wide(prov_role, "province", "job_role", args.top_n)
        top_prov.to_csv(out_dir / "province_top_roles.csv", index=False, encoding="utf-8-sig")

    # City x role
    if "city" in df.columns:
        city_role = group_counts(df.dropna(subset=["city", "job_role"]), ["city", "job_role"])
        city_role.to_csv(out_dir / "city_role_counts.csv", index=False, encoding="utf-8-sig")

    # Tehran district / neighborhood x role
    if "city" in df.columns:
        tehran = df[df["city"].astype(str).eq("تهران")].copy()
        if not tehran.empty:
            if "tehran_district" in tehran.columns:
                dist_role = group_counts(
                    tehran.dropna(subset=["tehran_district", "job_role"]),
                    ["tehran_district", "job_role"],
                )
                dist_role.to_csv(out_dir / "tehran_district_role_counts.csv", index=False, encoding="utf-8-sig")
                top_dist = top_roles_wide(dist_role, "tehran_district", "job_role", args.top_n)
                top_dist.to_csv(out_dir / "tehran_district_top_roles.csv", index=False, encoding="utf-8-sig")

            if "tehran_neighborhood" in tehran.columns:
                nei_role = group_counts(
                    tehran.dropna(subset=["tehran_neighborhood", "job_role"]),
                    ["tehran_neighborhood", "job_role"],
                )
                nei_role.to_csv(out_dir / "tehran_neighborhood_role_counts.csv", index=False, encoding="utf-8-sig")
                top_nei = top_roles_wide(nei_role, "tehran_neighborhood", "job_role", args.top_n)
                top_nei.to_csv(out_dir / "tehran_neighborhood_top_roles.csv", index=False, encoding="utf-8-sig")

    print("Saved geo-role outputs to:", out_dir)


if __name__ == "__main__":
    main()

