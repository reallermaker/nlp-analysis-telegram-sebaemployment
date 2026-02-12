from __future__ import annotations

from pathlib import Path
import re
import html as htmllib
import pandas as pd

from skills_catalog import SKILL_PATTERNS
from labels_fa import skill_label_fa


PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
ARABIC_LETTERS = str.maketrans({"ي": "ی", "ك": "ک", "ة": "ه", "ۀ": "ه", "ؤ": "و", "إ": "ا", "أ": "ا"})


def normalize_text(s: str) -> str:
    s = htmllib.unescape(s or "")
    s = s.translate(ARABIC_LETTERS).translate(PERSIAN_DIGITS).translate(ARABIC_DIGITS)
    s = s.replace("\u200c", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s



EXP_RANGE_RE = re.compile(r"(?P<a>\d{1,2})\s*(?:تا|الی|—|–|-)\s*(?P<b>\d{1,2})\s*سال")
EXP_MIN_RE = re.compile(r"(?:حداقل|min)\s*(?P<a>\d{1,2})\s*سال", re.IGNORECASE)
EXP_SINGLE_RE = re.compile(r"(?P<a>\d{1,2})\s*سال(?:\s*سابقه)?")
EXP_ZERO_RE = re.compile(r"بدون\s*سابقه|junior|intern|کارآموز", re.IGNORECASE)


def parse_experience_years(text: str) -> tuple[float | None, float | None]:
   
    t = normalize_text(text or "")

    if EXP_ZERO_RE.search(t):
        return 0.0, 0.0

    m = EXP_RANGE_RE.search(t)
    if m:
        return float(m.group("a")), float(m.group("b"))

    m = EXP_MIN_RE.search(t)
    if m:
        return float(m.group("a")), None

    m = EXP_SINGLE_RE.search(t)
    if m:
        return float(m.group("a")), None

    return None, None


def compile_patterns():
    compiled = []
    for item in SKILL_PATTERNS:
        compiled.append(
            {
                "skill": item["skill"],
                "category": item.get("category", "unknown"),
                "group": item.get("group", "hard"),
                "parent": item.get("parent", None),
                "regex": re.compile(item["pattern"], flags=re.IGNORECASE),
                "pattern": item["pattern"],
            }
        )
    return compiled


def main():
    root = Path(__file__).resolve().parents[1]
    in_csv = root / "outputs" / "ads_parsed_all.csv"

    out_ads = root / "outputs" / "ads_with_skills.csv"
    out_counts = root / "outputs" / "skills_counts.csv"
    out_job_counts = root / "outputs" / "job_skill_counts.csv"

    df = pd.read_csv(in_csv, encoding="utf-8-sig")

    if "text_norm" not in df.columns:
        df["text_norm"] = df["text_raw"].fillna("").map(normalize_text)

    if "job_title_norm" not in df.columns:
        df["job_title_norm"] = df["job_title"].fillna("").map(normalize_text)

    
    exp_col = df["experience"].fillna("").astype(str) if "experience" in df.columns else pd.Series([""] * len(df))
    exp_source = (exp_col + " " + df["text_norm"].fillna("")).astype(str)

    exp_parsed = exp_source.map(parse_experience_years)
    df["exp_min_years"] = exp_parsed.map(lambda x: x[0])
    df["exp_max_years"] = exp_parsed.map(lambda x: x[1])

    compiled = compile_patterns()

    
    skill_matrix = pd.DataFrame(index=df.index)
    text_series = df["text_norm"].fillna("")

    for c in compiled:
        skill_matrix[c["skill"]] = text_series.str.contains(c["regex"], na=False)

    
    children_by_parent: dict[str, list[str]] = {}
    for c in compiled:
        p = c.get("parent")
        if p:
            children_by_parent.setdefault(p, []).append(c["skill"])

    for p, kids in children_by_parent.items():
        if p in skill_matrix.columns:
            skill_matrix[p] = skill_matrix[p] & (~skill_matrix[kids].any(axis=1))

    
    df["skills_extracted"] = skill_matrix.apply(
        lambda row: "|".join([s for s, v in row.items() if bool(v)]),
        axis=1,
    )

    
    fine_skills = [c["skill"] for c in compiled if c.get("parent")]
    if fine_skills:
        df["skills_extracted_fine"] = skill_matrix[fine_skills].apply(
            lambda row: "|".join([s for s, v in row.items() if bool(v)]),
            axis=1,
        )
    else:
        df["skills_extracted_fine"] = ""

    
    if children_by_parent:
        parent_hits = {}
        for p, kids in children_by_parent.items():
            base = skill_matrix[p] if p in skill_matrix.columns else False
            kid_any = skill_matrix[kids].any(axis=1)
            parent_hits[p] = (base | kid_any)

        df["skills_extracted_parents"] = pd.DataFrame(parent_hits).apply(
            lambda row: "|".join([s for s, v in row.items() if bool(v)]),
            axis=1,
        )
    else:
        df["skills_extracted_parents"] = ""

    
    overall_counts = (
        skill_matrix.sum(axis=0)
        .rename("n_ads")
        .reset_index()
        .rename(columns={"index": "skill"})
        .sort_values("n_ads", ascending=False)
    )

    
    cat_map = {c["skill"]: c["category"] for c in compiled}
    group_map = {c["skill"]: c["group"] for c in compiled}
    parent_map = {c["skill"]: c.get("parent") for c in compiled}

    overall_counts["category"] = overall_counts["skill"].map(cat_map)
    overall_counts["group"] = overall_counts["skill"].map(group_map)
    overall_counts["parent"] = overall_counts["skill"].map(parent_map)
    overall_counts_with_fa = overall_counts.copy()
    overall_counts_with_fa["skill_fa"] = overall_counts_with_fa["skill"].map(skill_label_fa)

    
    long_df = (
        skill_matrix.assign(job_title_norm=df["job_title_norm"])
        .melt(id_vars=["job_title_norm"], var_name="skill", value_name="has_skill")
    )

    job_skill_counts = (
        long_df[long_df["has_skill"]]
        .groupby(["job_title_norm", "skill"], as_index=False)
        .size()
        .rename(columns={"size": "n_ads"})
        .sort_values(["job_title_norm", "n_ads"], ascending=[True, False])
    )
    job_skill_counts_with_fa = job_skill_counts.copy()
    job_skill_counts_with_fa["skill_fa"] = job_skill_counts_with_fa["skill"].map(skill_label_fa)


    out_ads.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_ads, index=False, encoding="utf-8-sig")
    overall_counts.to_csv(out_counts, index=False, encoding="utf-8-sig")
    overall_counts_with_fa.to_csv(out_counts.with_name("skills_counts_with_fa.csv"), index=False, encoding="utf-8-sig")
    job_skill_counts.to_csv(out_job_counts, index=False, encoding="utf-8-sig")
    job_skill_counts_with_fa.to_csv(out_job_counts.with_name("job_skill_counts_with_fa.csv"), index=False, encoding="utf-8-sig")

    print(f" ads_with_skills saved: {out_ads}")
    print(f" skills_counts saved: {out_counts}")
    print(f" job_skill_counts saved: {out_job_counts}")

    print("\nTop 20 skills:")
    print(overall_counts.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
