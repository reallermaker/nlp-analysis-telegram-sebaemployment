from __future__ import annotations

from pathlib import Path
import argparse
import sys
import pandas as pd

from job_family_catalog import JOB_FAMILY_CATALOG
from job_taxonomy import JOB_TITLE_PATTERNS


def configure_stdout():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=str, default="outputs")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    
    fam_df = pd.DataFrame(JOB_FAMILY_CATALOG)
    fam_path = out_dir / "job_family_catalog.csv"
    fam_df.to_csv(fam_path, index=False, encoding="utf-8-sig")

    
    role_df = pd.DataFrame(JOB_TITLE_PATTERNS)
    role_path = out_dir / "job_role_catalog.csv"
    role_df.to_csv(role_path, index=False, encoding="utf-8-sig")

    print("Saved:", fam_path)
    print("Saved:", role_path)


if __name__ == "__main__":
    main()

