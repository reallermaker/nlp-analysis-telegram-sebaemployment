from __future__ import annotations

from pathlib import Path
import re
import html as htmllib
import argparse
import pandas as pd
import sys
from bs4 import BeautifulSoup


TITLE_RE = re.compile(r"[«\"]\s*([^»\"]+?)\s*[»\"]")

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


def clean_html_text(el) -> str:
    if el is None:
        return ""
    for br in el.find_all("br"):
        br.replace_with("\n")
    txt = el.get_text("\n", strip=True)
    txt = htmllib.unescape(txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()


def group_joined_messages(soup: BeautifulSoup) -> list[dict]:
    msgs = [m for m in soup.select("div.message") if "default" in (m.get("class") or [])]
    groups: list[dict] = []

    i = 0
    while i < len(msgs):
        m = msgs[i]
        texts = [clean_html_text(m.select_one("div.text"))]
        ids = [m.get("id")]

        dt = m.select_one("div.pull_right.date.details")
        dt_title = dt.get("title") if dt else None

        frm_el = m.select_one("div.from_name")
        from_name = clean_html_text(frm_el) if frm_el else None

        j = i + 1
        while j < len(msgs) and "joined" in (msgs[j].get("class") or []):
            texts.append(clean_html_text(msgs[j].select_one("div.text")))
            ids.append(msgs[j].get("id"))
            j += 1

        groups.append(
            {
                "group_index": len(groups),
                "message_ids": ",".join([x for x in ids if x]),
                "dt_title": dt_title,
                "from_name": from_name,
                "text": "\n\n".join([t for t in texts if t]).strip(),
            }
        )
        i = j

    return groups


def extract_field_anykey(text: str, keys: list[str]) -> str | None:
    for k in keys:
        m = re.search(rf"{re.escape(k)}\s*[:：]?\s*(.+)", text)
        if m:
            val = m.group(1).strip().split("\n")[0].strip()
            return val
    return None


def parse_ads_from_html(html_path: Path) -> pd.DataFrame:
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html_text, "html.parser")

    groups = group_joined_messages(soup)

    company_keys = ["نام شرکت", "شرکت", "نام‌شرکت", "فعالیت"]
    location_keys = ["شهرستان و محدوده مکانی", "شهرستان", "شهر", "محل فعالیت"]
    education_keys = ["مدرک تحصیلی", "تحصیلات"]
    experience_keys = ["سابقه فعالیت", "سابقه کار", "سابقه کاری", "سابقه"]

    rows = []
    for g in groups:
        raw = g["text"]
        raw_norm = normalize_text(raw)

        title_m = TITLE_RE.search(raw)
        job_title = title_m.group(1).strip() if title_m else None

        rows.append(
            {
                "source_file": html_path.name,
                "group_index": g["group_index"],
                "message_ids": g["message_ids"],
                "date_title": g["dt_title"],
                "job_title": job_title,
                "company": extract_field_anykey(raw, company_keys),
                "location": extract_field_anykey(raw, location_keys),
                "education": extract_field_anykey(raw, education_keys),
                "experience": extract_field_anykey(raw, experience_keys),
                "text_raw": raw,
                "text_norm": raw_norm,
            }
        )

    df = pd.DataFrame(rows)

    df["job_title_norm"] = df["job_title"].fillna("").map(normalize_text)
    df["job_title_norm"] = df["job_title_norm"].str.replace(r"[-_–—]+", " ", regex=True).str.strip()

    return df


def find_message_files(raw_dir: Path) -> list[Path]:
    
    candidates = []

    
    candidates += list(raw_dir.glob("messages*.html"))
    candidates += list(raw_dir.glob("messages*.htm"))


    for p in raw_dir.glob("messages*"):
        if p.is_file() and p.suffix == "":
            
            head = p.read_text(encoding="utf-8", errors="ignore")[:2000].lower()
            if "<html" in head or "telegram" in head:
                candidates.append(p)

    
    unique = sorted({c.resolve() for c in candidates}, key=lambda x: x.name)
    return unique


def main():
    configure_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=str, default="data/raw", help="Directory containing Telegram export HTML files")
    parser.add_argument("--output", type=str, default="outputs/ads_parsed_all.csv", help="Output CSV path")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    raw_dir = (root / args.input_dir).resolve()
    out_csv = (root / args.output).resolve()

    if not raw_dir.exists():
        raise FileNotFoundError(f"Input dir not found: {raw_dir}")

    files = find_message_files(raw_dir)
    if not files:
        raise FileNotFoundError(f"No telegram message html files found in: {raw_dir}")

    all_dfs = []
    for f in files:
        df = parse_ads_from_html(f)
        all_dfs.append(df)
        print(f" {f.name}: {len(df)} groups")

    out = pd.concat(all_dfs, ignore_index=True)

    
    out = out.drop_duplicates(subset=["message_ids", "date_title", "job_title", "company"], keep="first")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False, encoding="utf-8-sig")

    print("\n====================")
    print(f" Total rows: {len(out)}")
    print(f" Saved: {out_csv}")
    print(out[["source_file", "date_title", "job_title", "company", "location"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
