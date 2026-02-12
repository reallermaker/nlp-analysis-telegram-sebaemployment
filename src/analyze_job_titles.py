from __future__ import annotations

from pathlib import Path
import argparse
import sys

import pandas as pd


def configure_stdout():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="outputs/ads_with_job_titles.csv")
    parser.add_argument("--out", type=str, default="outputs/job_title_clean_counts.csv")
    parser.add_argument("--top", type=int, default=500)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    in_path = (root / args.input).resolve()
    out_path = (root / args.out).resolve()

    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    df = pd.read_csv(in_path, encoding="utf-8-sig")

    if "job_title_clean" not in df.columns:
        raise ValueError("Expected column 'job_title_clean' in the input file.")

    counts = (
        df["job_title_clean"]
        .replace("", pd.NA)
        .dropna()
        .astype(str)
        .value_counts()
        .head(int(args.top))
        .reset_index()
    )
    counts.columns = ["job_title_clean", "n_ads"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(out_path, index=False, encoding="utf-8-sig")

    print("Saved:", out_path)
    print("Rows:", len(counts))


if __name__ == "__main__":
    main()

