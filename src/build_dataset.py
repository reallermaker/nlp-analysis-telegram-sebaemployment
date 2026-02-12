from __future__ import annotations

from pathlib import Path
import argparse
import sys

import pandas as pd


KEY_COLS = ["source_file", "message_ids", "group_index", "date_title"]


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


def dedupe_on_key(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    if key_col not in df.columns:
        raise ValueError(f"Key column not found: {key_col}")
    return df.drop_duplicates(subset=[key_col], keep="first")


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--skills", type=str, default="outputs/ads_with_skills.csv")
    parser.add_argument("--jobs", type=str, default="outputs/ads_with_job_titles.csv")
    parser.add_argument("--locs", type=str, default="outputs/ads_with_locations.csv")
    parser.add_argument("--out", type=str, default="outputs/ads_enriched.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    skills_path = (root / args.skills).resolve()
    jobs_path = (root / args.jobs).resolve()
    locs_path = (root / args.locs).resolve()
    out_path = (root / args.out).resolve()

    if not skills_path.exists():
        raise FileNotFoundError(f"Skills file not found: {skills_path}")
    if not jobs_path.exists():
        raise FileNotFoundError(f"Jobs file not found: {jobs_path}")
    if not locs_path.exists():
        raise FileNotFoundError(f"Locations file not found: {locs_path}")

    df = pd.read_csv(skills_path, encoding="utf-8-sig")
    df["_ad_key"] = build_ad_key(df)

    jobs = pd.read_csv(jobs_path, encoding="utf-8-sig")
    jobs["_ad_key"] = build_ad_key(jobs)
    jobs = dedupe_on_key(jobs, "_ad_key")

    locs = pd.read_csv(locs_path, encoding="utf-8-sig")
    locs["_ad_key"] = build_ad_key(locs)
    locs = dedupe_on_key(locs, "_ad_key")

    # Select only additional columns to avoid duplication.
    base_cols = set(df.columns)

    job_extra_cols = [c for c in jobs.columns if c not in base_cols and c != "_ad_key"]
    loc_extra_cols = [c for c in locs.columns if c not in base_cols and c != "_ad_key"]

    out = df.merge(jobs[["_ad_key"] + job_extra_cols], on="_ad_key", how="left")
    out = out.merge(locs[["_ad_key"] + loc_extra_cols], on="_ad_key", how="left")

    rename_map = {
        "خانواده_شغلی": "job_family_fa",
        "عنوان_شغل_استاندارد": "job_role_fa",
    }
    for old, new in rename_map.items():
        if old in out.columns and new not in out.columns:
            out = out.rename(columns={old: new})

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("Saved:", out_path)
    print("Rows:", len(out))
    print("Columns:", len(out.columns))
    print("Sample columns:", ", ".join(safe_cols(list(out.columns)[:25])) + (" ..." if len(out.columns) > 25 else ""))


if __name__ == "__main__":
    main()

