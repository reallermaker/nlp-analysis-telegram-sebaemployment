from __future__ import annotations

from pathlib import Path
import re
import html as htmllib
import pandas as pd
import sys

from job_taxonomy import JOB_TITLE_PATTERNS


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


QUOTE_RE = re.compile(r"[«\"]([^«»\"]{2,80})[»\"]")
TITLE_HINT_RE = re.compile(r"(کارشناس|مدیر|مسئول|کارمند|تحلیل(?:گر)?|حسابدار|معامله(?:\s*گر|گر)|سرپرست|کارآموز|مشاور)")


def extract_title_from_text(text_raw: str) -> str | None:
    t = normalize_text(text_raw or "")
    candidates = [normalize_text(x) for x in QUOTE_RE.findall(t)]
    if not candidates:
        return None

    
    for c in candidates:
        if TITLE_HINT_RE.search(c):
            return c

    return candidates[0]


def compile_patterns():
    compiled = []
    for it in JOB_TITLE_PATTERNS:
        compiled.append({
            "code": it["code"],
            "family_fa": it["family_fa"],
            "role_fa": it["role_fa"],
            "regex": re.compile(it["pattern"], flags=re.IGNORECASE),
        })
    return compiled


def classify_job(text: str, compiled) -> tuple[str, str, str]:
    t = normalize_text(text or "")
    for it in compiled:
        if it["regex"].search(t):
            return it["code"], it["family_fa"], it["role_fa"]
    return "other", "سایر", "سایر"


def main():
    configure_stdout()
    root = Path(__file__).resolve().parents[1]
    in_csv = root / "outputs" / "ads_parsed_all.csv"
    if not in_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_csv}")

    df = pd.read_csv(in_csv, encoding="utf-8-sig")

    if "text_raw" not in df.columns:
        df["text_raw"] = ""

    if "job_title" not in df.columns:
        df["job_title"] = ""

    
    jt = df["job_title"].fillna("").astype(str)
    raw = df["text_raw"].fillna("").astype(str)

    def fix_title(row_job, row_text):
        j = normalize_text(row_job)
        if len(j) < 3 or j in {"الف", "ا", "ب"}:
            q = extract_title_from_text(row_text)
            return q if q else j
        return j

    df["job_title_clean"] = [fix_title(j, t) for j, t in zip(jt.tolist(), raw.tolist())]

    compiled = compile_patterns()

    
    source_text = (df["job_title_clean"].fillna("") + " " + df["text_raw"].fillna("")).astype(str)

    out = source_text.map(lambda x: classify_job(x, compiled))
    df["job_code"] = out.map(lambda x: x[0])
    df["خانواده_شغلی"] = out.map(lambda x: x[1])
    df["عنوان_شغل_استاندارد"] = out.map(lambda x: x[2])

    
    role_counts = (
        df["عنوان_شغل_استاندارد"]
        .fillna("سایر")
        .value_counts()
        .reset_index()
    )
    role_counts.columns = ["عنوان_شغل_استاندارد", "تعداد_آگهی"]

    
    family_counts = (
        df["خانواده_شغلی"]
        .fillna("سایر")
        .value_counts()
        .reset_index()
    )
    family_counts.columns = ["خانواده_شغلی", "تعداد_آگهی"]

    
    unknown_samples = (
        df[df["عنوان_شغل_استاندارد"].eq("سایر")]["job_title_clean"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .head(300)
        .reset_index()
    )
    unknown_samples.columns = ["job_title_clean", "n_ads"]

    
    out_ads = root / "outputs" / "ads_with_job_titles.csv"
    out_roles = root / "outputs" / "job_role_counts_fa.csv"
    out_fams = root / "outputs" / "job_family_counts_fa.csv"
    out_unknown = root / "outputs" / "job_title_unknown_samples.csv"

    out_ads.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_ads, index=False, encoding="utf-8-sig")
    role_counts.to_csv(out_roles, index=False, encoding="utf-8-sig")
    family_counts.to_csv(out_fams, index=False, encoding="utf-8-sig")
    unknown_samples.to_csv(out_unknown, index=False, encoding="utf-8-sig")

    print(f" Saved: {out_ads}")
    print(f" Saved: {out_roles}")
    print(f" Saved: {out_fams}")
    print(f" Saved: {out_unknown}")

    print("\nTop 25 roles:")
    print(role_counts.head(25).to_string(index=False))

    print("\nTop 15 families:")
    print(family_counts.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
