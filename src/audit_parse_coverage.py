from __future__ import annotations

from pathlib import Path
import argparse
import sys

import pandas as pd
from bs4 import BeautifulSoup

from parse_telegram import group_joined_messages


def configure_stdout():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def count_messages(soup: BeautifulSoup) -> tuple[int, int]:
   
    n_default = len(soup.select("div.message.default"))
    n_joined = len(soup.select("div.message.joined"))
    return n_default, n_joined


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=str, default="data/raw", help="Telegram export directory (messages*.html)")
    parser.add_argument("--parsed", type=str, default="outputs/ads_parsed_all.csv", help="Parsed groups CSV")
    parser.add_argument("--out", type=str, default="outputs/parse_coverage.csv", help="Output CSV path")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    raw_dir = (root / args.raw_dir).resolve()
    parsed_path = (root / args.parsed).resolve()
    out_path = (root / args.out).resolve()

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw dir not found: {raw_dir}")
    if not parsed_path.exists():
        raise FileNotFoundError(f"Parsed CSV not found: {parsed_path}")

    files = sorted(list(raw_dir.glob("messages*.html")) + list(raw_dir.glob("messages*.htm")), key=lambda p: p.name)
    if not files:
        raise FileNotFoundError(f"No messages*.html found in: {raw_dir}")

    parsed = pd.read_csv(parsed_path, encoding="utf-8-sig")
    groups_by_file = parsed.groupby("source_file", as_index=False).size().rename(columns={"size": "parsed_groups"})

    rows = []
    for f in files:
        html_text = f.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html_text, "html.parser")

        n_default, n_joined = count_messages(soup)
        groups = group_joined_messages(soup)
        n_groups = len(groups)

        rows.append(
            {
                "file": f.name,
                "html_default_messages": int(n_default),
                "html_joined_messages": int(n_joined),
                "groups_from_html": int(n_groups),
            }
        )

    rep = pd.DataFrame(rows).merge(groups_by_file, left_on="file", right_on="source_file", how="left")
    rep = rep.drop(columns=["source_file"])
    rep["parsed_groups"] = rep["parsed_groups"].fillna(0).astype(int)
    rep["default_per_group"] = (rep["html_default_messages"] / rep["groups_from_html"].clip(lower=1)).round(3)
    rep["parsed_minus_html_groups"] = rep["parsed_groups"] - rep["groups_from_html"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    rep.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(" Saved:", out_path)
    print("Files:", len(rep))
    print("Total default messages:", int(rep["html_default_messages"].sum()))
    print("Total groups from html:", int(rep["groups_from_html"].sum()))
    print("Total parsed groups:", int(rep["parsed_groups"].sum()))


if __name__ == "__main__":
    main()

