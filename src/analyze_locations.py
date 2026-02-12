from __future__ import annotations

from pathlib import Path
import re
import html as htmllib
import argparse
import pandas as pd
import sys


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
    
    s = s.replace('"', " ").replace("«", " ").replace("»", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s



CITY_PATTERNS = [
    (r"\btehran\b|تهران", "تهران", "تهران"),
    (r"\bkaraj\b|کرج", "البرز", "کرج"),
    (r"\bmashhad\b|مشهد", "خراسان رضوی", "مشهد"),
    (r"\bisfahan\b|اصفهان", "اصفهان", "اصفهان"),
    (r"\bshiraz\b|شیراز", "فارس", "شیراز"),
    (r"\btabriz\b|تبریز", "آذربایجان شرقی", "تبریز"),
    (r"\bahvaz\b|اهواز", "خوزستان", "اهواز"),
    (r"\brasht\b|رشت", "گیلان", "رشت"),
    (r"\bsari\b|ساری", "مازندران", "ساری"),
    (r"\bqom\b|قم", "قم", "قم"),
    (r"\bqazvin\b|قزوین", "قزوین", "قزوین"),
    (r"\byazd\b|یزد", "یزد", "یزد"),
    (r"\bkerman\b|کرمان", "کرمان", "کرمان"),
    (r"\bbandar\s*abbas\b|بندر\s*عباس", "هرمزگان", "بندرعباس"),
    (r"\bkermanshah\b|کرمانشاه", "کرمانشاه", "کرمانشاه"),
    (r"\bhamadan\b|همدان", "همدان", "همدان"),
    (r"\barak\b|اراک", "مرکزی", "اراک"),
    (r"\burmia\b|ارومیه|اورمیه", "آذربایجان غربی", "ارومیه"),
    (r"\bgorgan\b|گرگان", "گلستان", "گرگان"),
    (r"\bzahedan\b|زاهدان", "سیستان و بلوچستان", "زاهدان"),
    (r"\bsanandaj\b|سنندج", "کردستان", "سنندج"),
    (r"\bardabil\b|اردبیل", "اردبیل", "اردبیل"),
    (r"\bzanjan\b|زنجان", "زنجان", "زنجان"),
    (r"\bkhorramabad\b|خرم\s*آباد|خرماباد", "لرستان", "خرم‌آباد"),
    (r"\bbushehr\b|بوشهر", "بوشهر", "بوشهر"),
    (r"\bshahrekord\b|شهرکرد", "چهارمحال و بختیاری", "شهرکرد"),
    (r"\byasuj\b|یاسوج", "کهگیلویه و بویراحمد", "یاسوج"),
    (r"\bilam\b|ایلام", "ایلام", "ایلام"),
    (r"\bsemnan\b|سمنان", "سمنان", "سمنان"),
    (r"\bbirjand\b|بیرجند", "خراسان جنوبی", "بیرجند"),
    (r"\bbojnurd\b|بجنورد", "خراسان شمالی", "بجنورد"),
]

PROVINCES = [
    "تهران","البرز","اصفهان","فارس","خراسان رضوی","خوزستان","آذربایجان شرقی","آذربایجان غربی",
    "کرمان","گیلان","مازندران","قم","قزوین","یزد","کرمانشاه","گلستان","هرمزگان","مرکزی","همدان",
    "سیستان و بلوچستان","کردستان","زنجان","لرستان","بوشهر","چهارمحال و بختیاری","کهگیلویه و بویراحمد",
    "ایلام","اردبیل","خراسان جنوبی","خراسان شمالی","سمنان"
]

CITY_REGEX = [(re.compile(pat, flags=re.IGNORECASE), prov, city) for pat, prov, city in CITY_PATTERNS]

TEHRAN_DISTRICT_RE = re.compile(r"(?:منطقه|ناحیه)\s*([0-9]{1,2})", flags=re.IGNORECASE)

TEHRAN_DISTRICT_WORDS: dict[str, int] = {
    "یک": 1,
    "يک": 1,
    "اول": 1,
    "دو": 2,
    "دوم": 2,
    "سه": 3,
    "سوم": 3,
    "چهار": 4,
    "چهارم": 4,
    "پنج": 5,
    "پنجم": 5,
    "شش": 6,
    "ششم": 6,
    "هفت": 7,
    "هفتم": 7,
    "هشت": 8,
    "هشتم": 8,
    "نه": 9,
    "نهم": 9,
    "ده": 10,
    "دهم": 10,
    "یازده": 11,
    "يازده": 11,
    "یازدهم": 11,
    "دوازده": 12,
    "دوازدهم": 12,
    "سیزده": 13,
    "سیزدهم": 13,
    "چهارده": 14,
    "چهاردهم": 14,
    "پانزده": 15,
    "پانزدهم": 15,
    "شانزده": 16,
    "شانزدهم": 16,
    "هفده": 17,
    "هفدهم": 17,
    "هجده": 18,
    "هجدهم": 18,
    "نوزده": 19,
    "نوزدهم": 19,
    "بیست": 20,
    "بیستم": 20,
    "بیست و یک": 21,
    "بیست‌ویک": 21,
    "بیست و دو": 22,
    "بیست‌ودو": 22,
}

TEHRAN_DISTRICT_WORD_RE = re.compile(
    r"(?:منطقه|ناحیه)\s*(?:شماره\s*)?("
    r"بیست\s*[\u200c ]*\s*دو|بیست\s*[\u200c ]*\s*یک|"
    r"یازده|يازده|دوازده|سیزده|چهارده|پانزده|شانزده|هفده|هجده|نوزده|"
    r"ده|نه|هشت|هفت|شش|پنج|چهار|سه|دو|یک|يک|"
    r"بیست|"
    r"اول|دوم|سوم|چهارم|پنجم|ششم|هفتم|هشتم|نهم|دهم|"
    r"یازدهم|دوازدهم|سیزدهم|چهاردهم|پانزدهم|شانزدهم|هفدهم|هجدهم|نوزدهم|بیستم"
    r")",
    flags=re.IGNORECASE,
)

TEHRAN_ZONE_PATTERNS = [
    (re.compile(r"شمال\s*تهران", re.IGNORECASE), "تهران-شمال"),
    (re.compile(r"غرب\s*تهران", re.IGNORECASE), "تهران-غرب"),
    (re.compile(r"شرق\s*تهران", re.IGNORECASE), "تهران-شرق"),
    (re.compile(r"جنوب\s*تهران", re.IGNORECASE), "تهران-جنوب"),
    (re.compile(r"(?:مرکز\s*تهران|تهران\s*مرکز)", re.IGNORECASE), "تهران-مرکز"),
]


TEHRAN_NEIGHBORHOODS = [
    
    (re.compile(r"تجریش|tajrish", re.IGNORECASE), "تجریش"),
    (re.compile(r"زعفرانیه|zaferanieh", re.IGNORECASE), "زعفرانیه"),
    (re.compile(r"ولنجک|velenjak", re.IGNORECASE), "ولنجک"),
    (re.compile(r"نیاوران|niavaran", re.IGNORECASE), "نیاوران"),
    (re.compile(r"فرمانیه|farmanieh", re.IGNORECASE), "فرمانیه"),
    (re.compile(r"قیطریه|qeytarieh", re.IGNORECASE), "قیطریه"),
    (re.compile(r"الهیه|elahiyeh", re.IGNORECASE), "الهیه"),
    (re.compile(r"اقدسیه|aghdasieh", re.IGNORECASE), "اقدسیه"),
    (re.compile(r"کامرانیه|kamaraniyeh", re.IGNORECASE), "کامرانیه"),
    (re.compile(r"اوین|evin", re.IGNORECASE), "اوین"),
    (re.compile(r"جماران|jamaran", re.IGNORECASE), "جماران"),
    (re.compile(r"دربند|darband", re.IGNORECASE), "دربند"),
    (re.compile(r"درکه|darkeh", re.IGNORECASE), "درکه"),
    (re.compile(r"پاسداران|pasdaran", re.IGNORECASE), "پاسداران"),
    (re.compile(r"هروی|heravi", re.IGNORECASE), "هروی"),

    
    (re.compile(r"ونک|vanak|میدان\s*ونک", re.IGNORECASE), "ونک"),
    (re.compile(r"میرداماد|mirdamad", re.IGNORECASE), "میرداماد"),
    (re.compile(r"سهروردی|sohravardi", re.IGNORECASE), "سهروردی"),
    (re.compile(r"عباس\s*آباد|abbas\s*abad", re.IGNORECASE), "عباس‌آباد"),
    (re.compile(r"بهشتی|beheshti|خیابان\s*بهشتی", re.IGNORECASE), "بهشتی"),
    (re.compile(r"مطهری|motahari|خیابان\s*مطهری", re.IGNORECASE), "مطهری"),
    (re.compile(r"شریعتی|shariati", re.IGNORECASE), "شریعتی"),
    (re.compile(r"یوسف\s*آباد|yousef\s*abad", re.IGNORECASE), "یوسف‌آباد"),
    (re.compile(r"امیر\s*آباد|amir\s*abad", re.IGNORECASE), "امیرآباد"),
    (re.compile(r"گیشا|kuy\s*nasr|کوی\s*نصر", re.IGNORECASE), "گیشا/کوی نصر"),
    (re.compile(r"فاطمی|fatemi|میدان\s*فاطمی", re.IGNORECASE), "فاطمی"),
    (re.compile(r"آرژانتین|argentina|میدان\s*آرژانتین", re.IGNORECASE), "آرژانتین"),
    (re.compile(r"جردن|نلسون\s*ماندلا|jordan", re.IGNORECASE), "جردن/نلسون ماندلا"),

    
    (re.compile(r"ولیعصر|valiasr|ولی\s*عصر", re.IGNORECASE), "ولیعصر"),
    (re.compile(r"انقلاب|enghelab|میدان\s*انقلاب", re.IGNORECASE), "انقلاب"),
    (re.compile(r"هفت\s*تیر|haft\s*tir|میدان\s*هفت\s*تیر", re.IGNORECASE), "هفت‌تیر"),
    (re.compile(r"فردوسی|ferdowsi|میدان\s*فردوسی", re.IGNORECASE), "فردوسی"),
    (re.compile(r"جمهوری|jomhouri", re.IGNORECASE), "جمهوری"),
    (re.compile(r"توحید|tوحید|tوحيد", re.IGNORECASE), "توحید"),


    (re.compile(r"سعادت\s*آباد|saadat\s*abad|saadatabad", re.IGNORECASE), "سعادت‌آباد"),
    (re.compile(r"شهرک\s*غرب|shahrak\s*gharb|shahrake\s*gharb", re.IGNORECASE), "شهرک غرب"),
    (re.compile(r"مرزداران|marzdaran", re.IGNORECASE), "مرزداران"),
    (re.compile(r"پونک|punak|ponak", re.IGNORECASE), "پونک"),
    (re.compile(r"صادقیه|sadeghieh|sadeghiyeh", re.IGNORECASE), "صادقیه"),
    (re.compile(r"آریاشهر|aria\s*shahr", re.IGNORECASE), "آریاشهر"),
    (re.compile(r"ستارخان|setareh\s*khan", re.IGNORECASE), "ستارخان"),
    (re.compile(r"جنت\s*آباد|janat\s*abad|jannat\s*abad", re.IGNORECASE), "جنت‌آباد"),
    (re.compile(r"چیتگر|chitgar", re.IGNORECASE), "چیتگر"),
    (re.compile(r"اکباتان|ekbatan", re.IGNORECASE), "اکباتان"),
    (re.compile(r"تهرانسر|tehran\s*sar", re.IGNORECASE), "تهرانسر"),

    
    (re.compile(r"تهران\s*پارس|tehran\s*pars|tehranpars", re.IGNORECASE), "تهرانپارس"),
    (re.compile(r"نارمک|narmak", re.IGNORECASE), "نارمک"),
    (re.compile(r"مجیدیه|majidieh", re.IGNORECASE), "مجیدیه"),
    (re.compile(r"رسالت|resalat", re.IGNORECASE), "رسالت"),
    (re.compile(r"حکیمیه|hakimiyeh", re.IGNORECASE), "حکیمیه"),
    (re.compile(r"پیروزی|pirouzi", re.IGNORECASE), "پیروزی"),

    
    # City Rey: keep strict to avoid false positives.
    # Key pitfall: do NOT match across words like "گذاری شهرستان" -> "...ری شهر..." (false Rey).
    (re.compile(
        r"(?:^|[\s,،/\-()\[\]{}:؛;])(?:شهر\s*ری|شهرری|شهرستان\s*ری|shahr\s*rey)(?=$|[\s,،/\-()\[\]{}:؛;])",
        re.IGNORECASE,
    ), "شهرری"),
    (re.compile(r"نازی\s*آباد|nazi\s*abad", re.IGNORECASE), "نازی‌آباد"),
    (re.compile(r"شوش|shoosh", re.IGNORECASE), "شوش"),
    (re.compile(r"راه\s*آهن|railway", re.IGNORECASE), "راه‌آهن"),
]


def detect_city_province(text: str) -> tuple[str | None, str | None]:
    t = normalize_text(text)
    for rx, prov, city in CITY_REGEX:
        if rx.search(t):
            return prov, city
    
    for p in PROVINCES:
        if p in t:
            return p, None
    return None, None


def detect_all_city_province(text: str) -> list[tuple[str, str]]:
    # Multi-label detection: return all matched (province, city) pairs from CITY_REGEX.
    t = normalize_text(text)
    hits: list[tuple[str, str]] = []
    for rx, prov, city in CITY_REGEX:
        if rx.search(t):
            hits.append((prov, city))
    # De-dup while preserving order
    seen = set()
    out = []
    for prov, city in hits:
        key = (prov, city)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def detect_tehran_district(text: str) -> int | None:
    t = normalize_text(text)
    m = TEHRAN_DISTRICT_RE.search(t)
    if m:
        try:
            d = int(m.group(1))
            if 1 <= d <= 22:
                return d
        except Exception:
            pass

    mw = TEHRAN_DISTRICT_WORD_RE.search(t)
    if mw:
        w = mw.group(1)
        w = w.replace("\u200c", " ")
        w = re.sub(r"\s+", " ", w).strip()
        d = TEHRAN_DISTRICT_WORDS.get(w)
        if d and 1 <= int(d) <= 22:
            return int(d)

    return None


def detect_tehran_neighborhood(text: str) -> str | None:
    t = normalize_text(text)

    
    for rx, name in TEHRAN_NEIGHBORHOODS:
        if rx.search(t):
            return name

    
    for rx, zone in TEHRAN_ZONE_PATTERNS:
        if rx.search(t):
            return zone

    
    d = detect_tehran_district(t)
    if d is not None:
        return f"تهران-منطقه-{d}"

    return None


def main():
    configure_stdout()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="outputs/ads_parsed_all.csv")
    parser.add_argument("--out-dir", type=str, default="outputs")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    in_csv = (root / args.input).resolve()
    if not in_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_csv}")

    out_dir = (root / args.out_dir).resolve()
    out_ads = out_dir / "ads_with_locations.csv"
    out_city = out_dir / "city_counts.csv"
    out_prov = out_dir / "province_counts.csv"
    out_city_mentions = out_dir / "city_mentions_counts.csv"
    out_prov_mentions = out_dir / "province_mentions_counts.csv"
    out_city_mentions_any = out_dir / "city_mentions_any_counts.csv"
    out_prov_mentions_any = out_dir / "province_mentions_any_counts.csv"
    out_teh_dist = out_dir / "tehran_district_counts.csv"
    out_teh_nei = out_dir / "tehran_neighborhood_counts.csv"
    out_unknown = out_dir / "location_unknown_samples.csv"
    out_teh_unknown = out_dir / "tehran_neighborhood_unknown_samples.csv"

    df = pd.read_csv(in_csv, encoding="utf-8-sig")

    loc_col = "location" if "location" in df.columns else None
    text_col = "text_raw" if "text_raw" in df.columns else None

    if loc_col is None and text_col is None:
        raise ValueError("No location or text_raw column found in input CSV")

    loc_source = df[loc_col].fillna("").astype(str) if loc_col else pd.Series([""] * len(df))
    loc_source_any = loc_source
    if text_col:
        loc_source_any = (loc_source + " " + df[text_col].fillna("").astype(str)).astype(str)

    # Primary detection is based on structured location only.
    df["loc_source_norm"] = loc_source.map(normalize_text)
    # Any-mentions detection includes full text (higher recall, more noise).
    df["loc_source_any_norm"] = loc_source_any.map(normalize_text)

    detected = df["loc_source_norm"].map(detect_city_province)
    df["province"] = detected.map(lambda x: x[0])
    df["city"] = detected.map(lambda x: x[1])

    # Mentions-based counts (multi-label) from location only
    all_hits = df["loc_source_norm"].map(detect_all_city_province)
    df["_city_mentions"] = all_hits.map(lambda lst: [c for _, c in lst] if isinstance(lst, list) else [])
    df["_prov_mentions"] = all_hits.map(lambda lst: [p for p, _ in lst] if isinstance(lst, list) else [])

    # Mentions-based counts (multi-label) from location + text
    all_hits_any = df["loc_source_any_norm"].map(detect_all_city_province)
    df["_city_mentions_any"] = all_hits_any.map(lambda lst: [c for _, c in lst] if isinstance(lst, list) else [])
    df["_prov_mentions_any"] = all_hits_any.map(lambda lst: [p for p, _ in lst] if isinstance(lst, list) else [])

    df["tehran_district"] = pd.NA
    df["tehran_neighborhood"] = None

    tehran_mask = df["city"].eq("تهران")
    if tehran_mask.any():
        dist_series = df.loc[tehran_mask, "loc_source_norm"].map(detect_tehran_district)
        df.loc[tehran_mask, "tehran_district"] = pd.to_numeric(dist_series, errors="coerce").astype("Int64")
        df.loc[tehran_mask, "tehran_neighborhood"] = df.loc[tehran_mask, "loc_source_norm"].map(detect_tehran_neighborhood)

    
    prov_counts = df["province"].fillna("نامشخص").value_counts().reset_index()
    prov_counts.columns = ["province", "n_ads"]

    city_counts = df["city"].fillna("نامشخص").value_counts().reset_index()
    city_counts.columns = ["city", "n_ads"]

    # Mentions counts: count unique ad per mentioned city/province
    def _count_mentions(col: str, name: str) -> pd.DataFrame:
        exploded = df[[col]].copy()
        exploded["_ad_idx"] = df.index.astype(str)
        exploded = exploded.explode(col)
        exploded[col] = exploded[col].fillna("").astype(str)
        exploded = exploded[exploded[col].str.strip().ne("")]
        if exploded.empty:
            return pd.DataFrame(columns=[name, "n_ads"])
        out = exploded.drop_duplicates(subset=["_ad_idx", col]).groupby(col, as_index=False).size()
        out = out.rename(columns={col: name, "size": "n_ads"}).sort_values("n_ads", ascending=False)
        return out

    city_mentions = _count_mentions("_city_mentions", "city")
    prov_mentions = _count_mentions("_prov_mentions", "province")
    city_mentions_any = _count_mentions("_city_mentions_any", "city")
    prov_mentions_any = _count_mentions("_prov_mentions_any", "province")

    tehran_df = df[tehran_mask].copy()
    dist_counts = tehran_df["tehran_district"].value_counts(dropna=False).reset_index()
    dist_counts.columns = ["tehran_district", "n_ads"]
    dist_counts["tehran_district"] = dist_counts["tehran_district"].map(
        lambda x: "نامشخص" if pd.isna(x) else f"منطقه {int(x)}"
    )

    nei_counts = tehran_df["tehran_neighborhood"].fillna("نامشخص").value_counts().reset_index()
    nei_counts.columns = ["tehran_neighborhood", "n_ads"]

    unknown = (
        df[df["city"].isna()]["loc_source_norm"]
        .replace("", pd.NA).dropna()
        .value_counts()
        .head(300)
        .reset_index()
        .rename(columns={"index": "loc_source_norm", "loc_source_norm": "n_ads"})
    )

    teh_unknown = (
        tehran_df[tehran_df["tehran_neighborhood"].isna()]["loc_source_norm"]
        .replace("", pd.NA).dropna()
        .value_counts()
        .head(300)
        .reset_index()
        .rename(columns={"index": "loc_source_norm", "loc_source_norm": "n_ads"})
    )

    out_ads.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_ads, index=False, encoding="utf-8-sig")
    prov_counts.to_csv(out_prov, index=False, encoding="utf-8-sig")
    city_counts.to_csv(out_city, index=False, encoding="utf-8-sig")
    city_mentions.to_csv(out_city_mentions, index=False, encoding="utf-8-sig")
    prov_mentions.to_csv(out_prov_mentions, index=False, encoding="utf-8-sig")
    city_mentions_any.to_csv(out_city_mentions_any, index=False, encoding="utf-8-sig")
    prov_mentions_any.to_csv(out_prov_mentions_any, index=False, encoding="utf-8-sig")
    dist_counts.to_csv(out_teh_dist, index=False, encoding="utf-8-sig")
    nei_counts.to_csv(out_teh_nei, index=False, encoding="utf-8-sig")
    unknown.to_csv(out_unknown, index=False, encoding="utf-8-sig")
    teh_unknown.to_csv(out_teh_unknown, index=False, encoding="utf-8-sig")

    print(" Saved:", out_city)
    print(" Saved:", out_teh_nei)
    print(" Saved:", out_unknown)
    print(" Saved:", out_teh_unknown)

    print("\nTop 15 cities:")
    print(city_counts.head(15).to_string(index=False))

    print("\nTehran neighborhoods (Top 15):")
    print(nei_counts.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
