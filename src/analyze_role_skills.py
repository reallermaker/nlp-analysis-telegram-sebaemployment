from __future__ import annotations

from pathlib import Path
import argparse
import re
import html as htmllib
import math
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
    s = re.sub(r"\s+", " ", s).strip()
    return s


TARGET_ROLES = [
    "معامله‌گر اوراق بهادار",
    "معامله‌گر بورس کالا",
    "حسابدار/کارشناس حسابداری",
    "کارشناس حسابداری صندوق/NAV/صدور و ابطال",
    "کارشناس سبدگردانی/مدیریت پرتفوی",
    "معامله‌گر بورس انرژی",
    "کارشناس صندوق‌های سرمایه‌گذاری",
    "کارشناس پذیرش مشتری/سجام",
    "معامله‌گر مشتقه/آتی/اختیار",
    "دیجیتال مارکتینگ/محتوا/سئو",
    "سایر",
    "کارشناس ارزش‌گذاری",
    "کارشناس حسابداری مالیاتی",
    "پشتیبان نرم‌افزار/شبکه",
    "کارشناس مدل‌سازی/پیش‌بینی مالی",
    "کارشناس فروش/توسعه بازار",
    "کارشناس تسویه و پایاپای/پس از معامله",
    "مدیر/سرپرست",
    "کارشناس حقوق و دستمزد",
    "مدیر سبد/مدیر پرتفوی",
    "تحلیل‌گر تکنیکال",
    "تحلیل‌گر داده/هوش تجاری",
    "تحلیل‌گر بازار سرمایه",
    "خزانه‌دار/کارشناس دریافت و پرداخت",
    "برنامه‌نویس/توسعه‌دهنده نرم‌افزار",
    "کارشناس امور سهام/سپرده‌گذاری",
    "تحصیلدار/کارپرداز",
    "کارشناس عملیات معاملات/ایستگاه معاملاتی",
    "حسابرس داخلی/کنترل داخلی",
    "کارشناس حسابداری مالی/تهیه صورت‌های مالی",
    "کارشناس مدیریت ریسک",
    "کارشناس انطباق/مبارزه با پولشویی",
    "مسئول دفتر/منشی",
]

ROLE_COL_CANDIDATES = [
    "عنوان_شغل_استاندارد",
    "job_role_fa",
    "job_role",
    "job_title_std",
    "role_std",
]

SKILLS_COL_CANDIDATES = [
    "skills_extracted_fine",
    "skills_extracted",
    "skills_extracted_parents",
]

CORE_GROUPS = {"hard", "tool", "certificate"}


def pick_existing_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def build_ad_id(df: pd.DataFrame) -> pd.Series:
    # Prefer stable keys if available; otherwise fallback to row index.
    if "source_file" in df.columns and "date_title" in df.columns:
        return df["source_file"].astype(str) + "|" + df["date_title"].astype(str)
    return df.index.astype(str)


def try_merge_roles(df_skills: pd.DataFrame, root: Path) -> pd.DataFrame:
    # If role column exists in the skills file, no merge is needed.
    if pick_existing_col(df_skills, ROLE_COL_CANDIDATES):
        return df_skills

    # Try common outputs that may contain role labels per ad.
    candidates = [
        root / "outputs" / "ads_with_job_titles.csv",
        root / "outputs" / "ads_with_job_roles.csv",
        root / "outputs" / "ads_job_titles.csv",
        root / "outputs" / "ads_with_titles.csv",
    ]
    job_path = next((p for p in candidates if p.exists()), None)
    if job_path is None:
        raise ValueError(
            "Role column not found in outputs/ads_with_skills.csv and no job-title file found in outputs/. "
            "Expected a column like 'عنوان_شغل_استاندارد' or a file like outputs/ads_with_job_titles.csv"
        )

    jobs = pd.read_csv(job_path, encoding="utf-8-sig")

    # Try merging on stable keys if present.
    join_keys = []
    for k in ["source_file", "date_title"]:
        if k in df_skills.columns and k in jobs.columns:
            join_keys.append(k)

    if join_keys:
        out = df_skills.merge(jobs, on=join_keys, how="left", suffixes=("", "_job"))
        return out

    # Last resort: align by row index if sizes match (not recommended, but better than failing).
    if len(df_skills) == len(jobs):
        role_col = pick_existing_col(jobs, ROLE_COL_CANDIDATES)
        if role_col is None:
            raise ValueError("Job-title file found but role column not found inside it.")
        df_skills[role_col] = jobs[role_col].values
        return df_skills

    raise ValueError(
        "Could not merge roles: no common join keys and row counts differ. "
        "Make sure both files share (source_file, date_title)."
    )


def explode_skills(df: pd.DataFrame, skills_col: str) -> pd.DataFrame:
    s = df[skills_col].fillna("").astype(str)
    lst = s.map(lambda x: [t.strip() for t in x.split("|") if t.strip()])
    out = df.copy()
    out["_skill_list"] = lst
    out = out.explode("_skill_list")
    out = out.rename(columns={"_skill_list": "skill"})
    out = out[out["skill"].notna() & (out["skill"].astype(str).str.len() > 0)].copy()
    return out


def safe_div(a: float, b: float, eps: float = 1e-12) -> float:
    return a / (b if abs(b) > eps else eps)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze skill requirements by standardized job role.")
    p.add_argument(
        "--min-role-ads",
        type=int,
        default=30,
        help="Minimum number of unique ads per role to include in outputs.",
    )
    p.add_argument(
        "--min-skill-ads-global",
        type=int,
        default=20,
        help="Minimum number of unique ads mentioning a skill to include in outputs.",
    )
    p.add_argument(
        "--min-pair-ads",
        type=int,
        default=5,
        help="Minimum number of unique ads for a (role, skill) pair to include in outputs.",
    )
    return p.parse_args()


def main():
    configure_stdout()
    args = parse_args()
    root = Path(__file__).resolve().parents[1]

    in_skills = root / "outputs" / "ads_with_skills.csv"
    if not in_skills.exists():
        raise FileNotFoundError(f"Missing input: {in_skills}")

    df = pd.read_csv(in_skills, encoding="utf-8-sig")
    df = try_merge_roles(df, root)

    role_col = pick_existing_col(df, ROLE_COL_CANDIDATES)
    if role_col is None:
        raise ValueError("Role column not found even after merge attempts.")

    skills_col = pick_existing_col(df, SKILLS_COL_CANDIDATES)
    if skills_col is None:
        raise ValueError("No skills column found. Expected skills_extracted(_fine/_parents).")

    # Normalize role strings for reliable matching
    df[role_col] = df[role_col].fillna("").map(normalize_text)
    df["_ad_id"] = build_ad_id(df)

    # Drop empty roles
    df = df[df[role_col].astype(str).str.len() > 0].copy()

    # Filter to roles with enough data (avoid noisy associations)
    role_totals_all = (
        df.drop_duplicates(subset=["_ad_id", role_col])
        .groupby(role_col, as_index=False)
        .size()
        .rename(columns={"size": "n_ads_role"})
    )

    if args.min_role_ads and args.min_role_ads > 1:
        keep_roles = set(role_totals_all[role_totals_all["n_ads_role"] >= args.min_role_ads][role_col].tolist())
        df = df[df[role_col].isin(keep_roles)].copy()

    if df.empty:
        raise ValueError("No rows after filtering by min-role-ads. Lower --min-role-ads to include more roles.")

    # Explode skills to long format
    long_df = explode_skills(df, skills_col)
    long_df["skill"] = long_df["skill"].astype(str)

    # Prevent double counting: count each (ad_id, role, skill) once
    long_df = long_df.drop_duplicates(subset=["_ad_id", role_col, "skill"])

    # Role totals (unique ads per role)
    role_totals = (
        df.drop_duplicates(subset=["_ad_id", role_col])
        .groupby(role_col, as_index=False)
        .size()
        .rename(columns={"size": "n_ads_role"})
    )

    # Global totals (unique ads overall)
    total_ads = df.drop_duplicates(subset=["_ad_id"]).shape[0]

    # Global skill prevalence (unique ads containing each skill)
    global_skill = (
        long_df.drop_duplicates(subset=["_ad_id", "skill"])
        .groupby("skill", as_index=False)
        .size()
        .rename(columns={"size": "n_ads_global"})
    )

    if args.min_skill_ads_global and args.min_skill_ads_global > 1:
        keep_skills = set(global_skill[global_skill["n_ads_global"] >= args.min_skill_ads_global]["skill"].tolist())
        long_df = long_df[long_df["skill"].isin(keep_skills)].copy()
        global_skill = global_skill[global_skill["skill"].isin(keep_skills)].copy()

    global_skill["p_skill"] = global_skill["n_ads_global"].map(lambda x: safe_div(float(x), float(total_ads)))

    # Role-skill counts
    role_skill = (
        long_df.groupby([role_col, "skill"], as_index=False)
        .size()
        .rename(columns={"size": "n_ads"})
        .merge(role_totals, on=role_col, how="left")
        .merge(global_skill, on="skill", how="left")
    )

    if args.min_pair_ads and args.min_pair_ads > 1:
        role_skill = role_skill[role_skill["n_ads"] >= args.min_pair_ads].copy()

    if role_skill.empty:
        raise ValueError("No rows after filtering by min-skill-ads-global/min-pair-ads. Relax thresholds and rerun.")

    role_skill["pct_of_role"] = (role_skill["n_ads"] / role_skill["n_ads_role"].clip(lower=1)).round(4)

    # Lift: distinctiveness of skill within a role
    # lift = p(skill|role) / p(skill)
    role_skill["p_skill_given_role"] = role_skill["n_ads"] / role_skill["n_ads_role"].clip(lower=1)
    role_skill["lift"] = (
        role_skill.apply(lambda r: safe_div(float(r["p_skill_given_role"]), float(r["p_skill"])), axis=1)
    ).round(4)
    role_skill["lift_log"] = role_skill["lift"].map(lambda x: round(math.log(x), 4) if x and x > 0 else 0.0)

    # Attach skill metadata (group/category/parent) if present
    meta_path = root / "outputs" / "skills_counts.csv"
    if meta_path.exists():
        meta = pd.read_csv(meta_path, encoding="utf-8-sig").drop_duplicates(subset=["skill"])
        keep_cols = [c for c in ["skill", "category", "group", "parent"] if c in meta.columns]
        role_skill = role_skill.merge(meta[keep_cols], on="skill", how="left")
    else:
        # Ensure columns exist to avoid KeyError later
        role_skill["group"] = pd.NA
        role_skill["category"] = pd.NA
        role_skill["parent"] = pd.NA

    # Outputs
    out_counts = root / "outputs" / "role_skill_counts.csv"
    out_lift_all = root / "outputs" / "role_skill_lift_all.csv"
    out_lift_core = root / "outputs" / "role_skill_lift_core.csv"
    out_top_pct = root / "outputs" / "role_top_skills.csv"
    out_top_lift = root / "outputs" / "role_top_skills_lift.csv"

    out_counts.parent.mkdir(parents=True, exist_ok=True)

    role_skill_sorted_pct = role_skill.sort_values(
        [role_col, "pct_of_role", "n_ads"], ascending=[True, False, False]
    )
    role_skill_sorted_pct.to_csv(out_counts, index=False, encoding="utf-8-sig")

    
    role_skill_sorted_lift_all = role_skill.sort_values(
        [role_col, "lift", "pct_of_role", "n_ads"], ascending=[True, False, False, False]
    )
    role_skill_sorted_lift_all.to_csv(out_lift_all, index=False, encoding="utf-8-sig")

   
    role_skill_core = role_skill_sorted_lift_all.copy()
    role_skill_core = role_skill_core[role_skill_core["group"].isin(list(CORE_GROUPS))].copy()
    role_skill_core.to_csv(out_lift_core, index=False, encoding="utf-8-sig")

    
    TOP_N = 15

    
    rows = []
    for role, g in role_skill_sorted_pct.groupby(role_col):
        g2 = g.head(TOP_N)
        row = {"عنوان_شغل_استاندارد": role, "تعداد_آگهی_نقش": int(g2["n_ads_role"].iloc[0]) if len(g2) else 0}
        for i, (_, r) in enumerate(g2.iterrows(), start=1):
            row[f"skill_{i}"] = r["skill"]
            row[f"pct_{i}"] = float(r["pct_of_role"])
            row[f"n_{i}"] = int(r["n_ads"])
        rows.append(row)

    top_pct_df = pd.DataFrame(rows).sort_values("تعداد_آگهی_نقش", ascending=False)
    top_pct_df.to_csv(out_top_pct, index=False, encoding="utf-8-sig")

    
    rows = []
    for role, g in role_skill_core.groupby(role_col):
        g2 = g.head(TOP_N)
        row = {"عنوان_شغل_استاندارد": role, "تعداد_آگهی_نقش": int(g2["n_ads_role"].iloc[0]) if len(g2) else 0}
        for i, (_, r) in enumerate(g2.iterrows(), start=1):
            row[f"skill_{i}"] = r["skill"]
            row[f"lift_{i}"] = float(r["lift"])
            row[f"pct_{i}"] = float(r["pct_of_role"])
            row[f"n_{i}"] = int(r["n_ads"])
        rows.append(row)

    top_lift_df = pd.DataFrame(rows).sort_values("تعداد_آگهی_نقش", ascending=False)
    top_lift_df.to_csv(out_top_lift, index=False, encoding="utf-8-sig")

    print(" Saved:", out_counts)
    print(" Saved:", out_lift_all)
    print(" Saved:", out_lift_core)
    print(" Saved:", out_top_pct)
    print(" Saved:", out_top_lift)

    preview_roles = list(top_lift_df["عنوان_شغل_استاندارد"].head(5).values)
    for role in preview_roles:
        print("\n---", role, "(core lift top 8) ---")
        g = role_skill_core[role_skill_core[role_col] == role].head(8)
        cols = ["skill", "n_ads", "pct_of_role", "lift"]
        extra = [c for c in ["group", "category", "parent"] if c in g.columns]
        print(g[cols + extra].to_string(index=False))


if __name__ == "__main__":
    main()
