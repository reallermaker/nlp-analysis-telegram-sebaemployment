from __future__ import annotations

from pathlib import Path
import argparse
import math
import re
import sys
import urllib.request
import pandas as pd
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg

try:
    import geopandas as gpd
except Exception:
    gpd = None

from viz_theme import set_main_theme, add_footer, fa, pick_persian_font
from labels_fa import (
    METRIC_LABELS_FA as METRIC_LABELS_FA_STD,
    SKILL_GROUP_LABELS_FA as SKILL_GROUP_LABELS_FA_STD,
    SKILL_CATEGORY_LABELS_FA as SKILL_CATEGORY_LABELS_FA_STD,
    skill_label_fa,
    group_label_fa,
    category_label_fa,
    is_latin,
)


METRIC_LABELS_FA = {
    "n_ads": "تعداد آگهی",
    "n_ads_role": "تعداد آگهی نقش",
    "n_ads_global": "تعداد آگهی کل",
    "pct_of_role": "درصد داخل نقش",
}


SKILL_LABELS_FA = {
    "CM_Brokerage": "کارگزاری",
    "CM_Funds": "صندوق‌ها",
    "CM_Exchanges": "بورس‌ها",
    "CM_Regulations": "مقررات بازار سرمایه",
    "CM_Trading_Commodity": "معاملات بورس کالا",
    "CM_Trading_Securities": "معاملات اوراق بهادار",
    "CM_Trading_Energy": "معاملات بورس انرژی",
    "CM_Principles_Cert": "گواهی اصول بازار سرمایه",
    "CM_Trading_Cert": "گواهی معامله‌گری",
    "CM_Valuation_Cert": "گواهی ارزش‌گذاری",
    "Fund_Accounting_NAV": "حسابداری صندوق/NAV",
    "Accounting_Tax": "حسابداری مالیاتی",
    "Accounting": "حسابداری",
    "Trading": "معاملات/ترید",
    "Trading_Derivatives": "معاملات مشتقه",
    "Trading_Commodity": "معاملات کالا",
    "Trading_Equities": "معاملات سهام",
    "Trading_Energy": "معاملات انرژی",
    "Trading_Technical": "تحلیل تکنیکال",
    "Trading_FixedIncome": "درآمد ثابت",
    "Office": "آفیس",
    "Excel": "اکسل",
    "Communication": "ارتباطات",
    "Teamwork": "کار تیمی",
    "RayanHamAfza": "رایان هم‌افزا",
    "Accounting_Financial": "حسابداری مالی",
    "Accounting_Payroll": "حقوق و دستمزد",
    "Accounting_Tax": "حسابداری مالیاتی",
    "Accounting_Cost": "حسابداری بهای تمام‌شده",
    "Audit_Internal": "حسابرسی داخلی",
    "Audit_External": "حسابرسی مستقل",
    "CM_Codal_Disclosure": "افشای کدال",
    "CM_Custody_Settlement": "تسویه و سپرده‌گذاری",
    "Financial_Modeling": "مدل‌سازی مالی",
    "Financial_Reporting": "گزارشگری مالی",
    "Treasury": "خزانه‌داری",
    "Valuation_NAV": "ارزش‌گذاری ان‌ای‌وی",
    "Valuation_DCF": "ارزش‌گذاری تنزیل جریان نقدی",
    "Valuation_Relative": "ارزش‌گذاری نسبی",
    "Fund_Accounting_NAV": "حسابداری صندوق/ان‌ای‌وی",
    "Portfolio_RiskMetrics": "معیارهای ریسک پرتفوی",
    "Risk_Credit": "ریسک اعتباری",
    "Risk_Market": "ریسک بازار",
    "Risk_Operational": "ریسک عملیاتی",
    "Trading_FixedIncome": "درآمد ثابت",
    "Trading_Equities": "معاملات سهام",
    "Trading_Commodity": "معاملات کالا",
    "Trading_Energy": "معاملات انرژی",
    "Trading_Derivatives": "معاملات مشتقه",
    "Trading_Technical": "تحلیل تکنیکال",
    "Trading_Algo": "معاملات الگوریتمی",
    "Trading_Forex": "فارکس",
    "Trading_Crypto": "رمزارز",
    "CM_Trading_Securities": "معامله‌گری اوراق",
    "CM_Trading_Commodity": "معامله‌گری بورس کالا",
    "CM_Trading_Energy": "معامله‌گری بورس انرژی",
    "CM_Trading_Derivatives": "معامله‌گری مشتقه",
    "CM_Asset_Management": "مدیریت دارایی",
    "CM_Exchanges": "بورس‌ها",
    "CM_Regulations": "مقررات بازار سرمایه",
    "CM_Funds": "صندوق‌ها",
    "CM_Investment_Banking": "بانکداری سرمایه‌گذاری",
    "CM_Analysis_Cert": "گواهی تحلیلگری",
    "CM_Portfolio_Cert": "گواهی سبدگردانی",
    "CM_SupplyAdmission_Cert": "گواهی عرضه و پذیرش",
    "CM_Valuation_Cert": "گواهی ارزش‌گذاری",
    "CM_Trading_Cert": "گواهی معامله‌گری",
    "CM_InstitutionsMgmt_Cert": "گواهی مدیریت نهادها",
    "Capital_Market_Domain": "دانش بازار سرمایه",
    "Fund_Management": "مدیریت صندوق",
    "Financial_Analysis": "تحلیل مالی",
    "Portfolio": "پرتفوی",
    "Risk_Management": "مدیریت ریسک",
    "Audit": "حسابرسی",
    "Valuation": "ارزش‌گذاری",
    "Trading": "معاملات/ترید",
    "Sales": "فروش",
    "Negotiation": "مذاکره",
    "ICDL": "آی‌سی‌دی‌ال",
    "IFRS": "استانداردهای گزارشگری مالی بین‌المللی",
    "CRM": "سی‌آر‌ام",
    "Python": "پایتون",
    "SQL": "اس‌کیوال",
    "Tableau": "تابلو",
    "Pandas": "پانداس",
    "NumPy": "نام‌پای",
    "Excel": "اکسل",
    "Office": "آفیس",
    "SEO": "سئو",
    "MetaTrader": "متاتریدر",
    "TadbirPardaz": "تدبیرپرداز",
    "Rahavard365": "ره‌آورد ۳۶۵",
    "Sepidar": "سپیدار",
    "HamkaranSystems": "همکاران سیستم",
    "AML_KYC": "مبارزه با پولشویی/شناخت مشتری",
    "CM_Compliance": "انطباق",
    "Time Management": "مدیریت زمان",
    "Content Marketing": "بازاریابی محتوا",
    "Problem Solving": "حل مسئله",
    "Data Analysis": "تحلیل داده",
    "Digital Marketing": "بازاریابی دیجیتال",
    "Power BI": "پاور بی‌آی",
    "Machine Learning": "یادگیری ماشین",
    "Scikit-learn": "سایکت‌لرن",
    "Deep Learning": "یادگیری عمیق",
}

LABEL_MAP_FA = {
    "hard": "مهارت سخت",
    "soft": "مهارت نرم",
    "tool": "ابزار",
    "domain": "دانش دامنه",
    "certificate": "گواهی‌نامه",
    "data": "داده",
    "finance": "مالی",
    "capital_market": "بازار سرمایه",
    "marketing": "بازاریابی",
    "office_suite": "نرم‌افزار اداری",
    "accounting_software": "نرم‌افزار حسابداری",
    "erp_accounting": "ای‌آر‌پی حسابداری",
    "trading_platform": "پلتفرم معاملاتی",
    "computer_literacy": "سواد رایانه‌ای",
    "finance_software": "نرم‌افزار مالی",
    "soft": "مهارت نرم",
    "unknown": "نامشخص",
}


PROVINCE_CENTERS = {
    "تهران": (35.6892, 51.3890),
    "البرز": (35.8400, 50.9391),
    "اصفهان": (32.6546, 51.6680),
    "فارس": (29.5918, 52.5837),
    "خراسان رضوی": (36.2605, 59.6168),
    "خوزستان": (31.3183, 48.6706),
    "آذربایجان شرقی": (38.0962, 46.2738),
    "آذربایجان غربی": (37.5527, 45.0761),
    "کرمان": (30.2839, 57.0834),
    "گیلان": (37.2682, 49.5891),
    "مازندران": (36.5659, 53.0586),
    "قم": (34.6399, 50.8759),
    "قزوین": (36.2688, 50.0041),
    "یزد": (31.8974, 54.3569),
    "کرمانشاه": (34.3142, 47.0650),
    "گلستان": (36.8441, 54.4430),
    "هرمزگان": (27.1832, 56.2666),
    "مرکزی": (34.0917, 49.6892),
    "همدان": (34.7983, 48.5148),
    "سیستان و بلوچستان": (29.4963, 60.8629),
    "کردستان": (35.3147, 46.9988),
    "زنجان": (36.6765, 48.4963),
    "لرستان": (33.4878, 48.3558),
    "بوشهر": (28.9220, 50.8330),
    "چهارمحال و بختیاری": (32.3256, 50.8644),
    "کهگیلویه و بویراحمد": (30.6682, 51.5880),
    "ایلام": (33.6374, 46.4227),
    "اردبیل": (38.2498, 48.2933),
    "خراسان جنوبی": (32.8649, 59.2211),
    "خراسان شمالی": (37.4750, 57.3224),
    "سمنان": (35.5729, 53.3970),
}


CITY_CENTERS = {
    "تهران": (35.6892, 51.3890),
    "مشهد": (36.2605, 59.6168),
    "اصفهان": (32.6546, 51.6680),
    "کرج": (35.8400, 50.9391),
    "شیراز": (29.5918, 52.5837),
    "قم": (34.6399, 50.8759),
    "رشت": (37.2682, 49.5891),
    "کرمان": (30.2839, 57.0834),
    "تبریز": (38.0962, 46.2738),
    "زنجان": (36.6765, 48.4963),
    "ساری": (36.5659, 53.0586),
    "ارومیه": (37.5527, 45.0761),
    "یزد": (31.8974, 54.3569),
    "همدان": (34.7983, 48.5148),
    "اراک": (34.0917, 49.6892),
    "بندرعباس": (27.1832, 56.2666),
    "اهواز": (31.3183, 48.6706),
    "قزوین": (36.2688, 50.0041),
    "اردبیل": (38.2498, 48.2933),
    "گرگان": (36.8441, 54.4430),
    "سمنان": (35.5729, 53.3970),
    "بوشهر": (28.9220, 50.8330),
    "زاهدان": (29.4963, 60.8629),
    "بیرجند": (32.8649, 59.2211),
    "خرم‌آباد": (33.4878, 48.3558),
    "شهرکرد": (32.3256, 50.8644),
    "بجنورد": (37.4750, 57.3224),
    "ایلام": (33.6374, 46.4227),
    "سنندج": (35.3147, 46.9988),
}


CITY_LABEL_OFFSETS_POINTS: dict[str, tuple[int, int]] = {
    # Dense Tehran cluster
    "تهران": (12, 10),
    "کرج": (-18, 10),
    "قم": (10, -14),
    "قزوین": (-18, -12),
    "سمنان": (10, 10),

    # North
    "رشت": (-20, 10),
    "ساری": (10, 10),
    "گرگان": (10, 10),

    # East / NE
    "مشهد": (10, 10),
    "بجنورد": (10, 10),
    "بیرجند": (10, -14),
    "زاهدان": (10, -14),

    # West / NW
    "تبریز": (-18, 10),
    "ارومیه": (-18, 10),
    "زنجان": (-18, 10),
    "اردبیل": (10, 10),
    "سنندج": (-18, -12),
    "ایلام": (-18, -12),
    "همدان": (-18, -12),

    # Center / South
    "اصفهان": (-18, -12),
    "اراک": (-18, -12),
    "شهرکرد": (-18, -12),
    "خرم‌آباد": (-18, -12),
    "یزد": (10, -12),
    "کرمان": (10, -12),
    "شیراز": (-18, -12),
    "اهواز": (-18, -12),
    "بوشهر": (-18, -12),
    "بندرعباس": (10, -12),
}


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


_PERSIAN_RE = re.compile(r"[\u0600-\u06FF]")


def _apply_font_preferences(fig) -> None:
    # Matplotlib does not reliably fallback per-glyph when a font is missing glyphs.
    # We therefore force:
    # - Persian/Arabic-only texts -> preferred Persian font (B Nazanin if available)
    # - any Latin-containing text -> DejaVu Sans (ensures NAV/SQL/CRM/ICDL render)
    persian_font = pick_persian_font()
    latin_font = "DejaVu Sans"

    try:
        from matplotlib.text import Text

        for t in fig.findobj(Text):
            s = t.get_text()
            if not s:
                continue
            if is_latin(s):
                t.set_fontname(latin_font)
            elif _PERSIAN_RE.search(str(s)):
                t.set_fontname(persian_font)
    except Exception:
        pass


def save_fig(fig, out_path: Path) -> None:
    add_footer(fig)
    _apply_font_preferences(fig)
    # Some artists (ticks, offset texts) are only fully created after a draw.
    try:
        fig.canvas.draw()
    except Exception:
        pass
    fig.tight_layout()
    # tight_layout/draw may create/update Text objects; apply again to avoid ? glyphs.
    _apply_font_preferences(fig)
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def display_label(text: str) -> str:
    s = "" if text is None else str(text)
    if s in METRIC_LABELS_FA_STD:
        return METRIC_LABELS_FA_STD[s]
    if s in SKILL_GROUP_LABELS_FA_STD:
        return group_label_fa(s)
    if s in SKILL_CATEGORY_LABELS_FA_STD:
        return category_label_fa(s)
    return skill_label_fa(s)


def annotate_bars_h(ax, fmt="{:,.0f}"):
    xlim = ax.get_xlim()
    span = xlim[1] - xlim[0] if xlim[1] != xlim[0] else 1
    offset = span * 0.01
    for bar in ax.patches:
        width = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax.text(width + offset, y, fa(fmt.format(width)), va="center", ha="left", fontsize=8)


def annotate_bars_v(ax, fmt="{:,.0f}", fontsize: int = 8):
    ylim = ax.get_ylim()
    span = ylim[1] - ylim[0] if ylim[1] != ylim[0] else 1
    offset = span * 0.01
    for bar in ax.patches:
        height = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2
        ax.text(x, height + offset, fa(fmt.format(height)), va="bottom", ha="center", fontsize=int(fontsize), rotation=0)


def plot_barh(
    df,
    label_col,
    value_col,
    title,
    out_path,
    top_n=20,
    drop_labels=None,
    x_label: str | None = None,
    annotate: bool = True,
    fig_width: float = 10.0,
    height_per_item: float = 0.35,
    base_height: float = 1.0,
    annotate_fontsize: int = 8,
):
    d = df.copy()
    if drop_labels:
        d = d[~d[label_col].astype(str).isin(set(drop_labels))].copy()

    d[label_col] = d[label_col].astype(str)
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce").fillna(0)

    d = d.sort_values(value_col, ascending=False).head(top_n)
    d = d.sort_values(value_col, ascending=True)

    d["_label"] = d[label_col].map(display_label)
    fig_h = max(4.0, float(height_per_item) * len(d) + float(base_height))
    fig, ax = plt.subplots(figsize=(float(fig_width), fig_h))
    sns.barplot(data=d, x=value_col, y=d["_label"].map(fa), ax=ax, orient="h")
    ax.set_title(fa(title))
    metric_label = display_label(x_label) if x_label else display_label(value_col)
    ax.set_xlabel(fa(metric_label))
    ax.set_ylabel("")
    if annotate:
        # Add right-side room so value labels do not get clipped.
        x0, x1 = ax.get_xlim()
        span0 = x1 - x0 if x1 != x0 else 1
        ax.set_xlim(x0, x1 + span0 * 0.08)

        xlim = ax.get_xlim()
        span = xlim[1] - xlim[0] if xlim[1] != xlim[0] else 1
        offset = span * 0.01
        for bar in ax.patches:
            width = bar.get_width()
            y = bar.get_y() + bar.get_height() / 2
            ax.text(
                width + offset,
                y,
                fa("{:,.0f}".format(width)),
                va="center",
                ha="left",
                fontsize=int(annotate_fontsize),
            )
    save_fig(fig, out_path)
    return d


def plot_pareto(df, label_col, value_col, title, out_path, top_n=20, y_label: str | None = None):
    d = df.copy()
    d[label_col] = d[label_col].astype(str)
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce").fillna(0)
    d = d.sort_values(value_col, ascending=False).head(top_n).reset_index(drop=True)

    d["cum"] = d[value_col].cumsum()
    total = d[value_col].sum() if d[value_col].sum() else 1
    d["cum_pct"] = d["cum"] / total * 100

    d["_label"] = d[label_col].map(display_label)

    fig, ax1 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=d, x="_label", y=value_col, ax=ax1)
    ax1.set_title(fa(title))
    ax1.set_xlabel("")
    metric_label = display_label(y_label) if y_label else display_label(value_col)
    ax1.set_ylabel(fa(metric_label))
    ax1.tick_params(axis="x", rotation=35)
    ax1.set_xticks(list(range(len(d))))
    ax1.set_xticklabels([fa(x) for x in d["_label"].tolist()], rotation=35, ha="right")

    ax2 = ax1.twinx()
    ax2.plot(range(len(d)), d["cum_pct"], marker="o")
    ax2.set_ylabel(fa("درصد تجمعی"))
    ax2.set_ylim(0, 110)

    save_fig(fig, out_path)
    return d


def plot_donut(df, label_col, value_col, title, out_path, top_n=6):
    d = df.copy()
    d[label_col] = d[label_col].astype(str)
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce").fillna(0)
    d = d.sort_values(value_col, ascending=False)

    top = d.head(top_n).copy()
    other_sum = d.iloc[top_n:][value_col].sum()
    if other_sum > 0:
        top = pd.concat([top, pd.DataFrame([{label_col: "سایر", value_col: other_sum}])], ignore_index=True)

    top["_label"] = top[label_col].map(display_label)
    labels = top["_label"].map(fa).tolist()
    values = top[value_col].astype(float).tolist()
    total = float(sum(values)) if sum(values) else 1.0
    pct = [v / total * 100.0 for v in values]

    fig, ax = plt.subplots(figsize=(9.5, 8.0))
    colors = sns.color_palette("tab10", n_colors=len(values))
    wedges, _, autotexts = ax.pie(
        values,
        startangle=90,
        counterclock=False,
        colors=colors,
        wedgeprops={"width": 0.38, "edgecolor": "white"},
        autopct=lambda p: f"{p:.1f}%" if p >= 5 else "",
        pctdistance=0.85,
    )
    for t in autotexts:
        t.set_fontsize(8)
        t.set_color("#0f1f33")

    ax.set_title(fa(title))
    ax.text(0, 0, fa(f"مجموع\n{int(total):,}"), ha="center", va="center", fontsize=10, fontweight="bold")
    ax.set_aspect("equal")

    legend_labels = [
        fa(f"{lab} ({int(v):,} / {p:.1f}%)") for lab, v, p in zip(top["_label"].tolist(), values, pct)
    ]
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5), frameon=False)

    save_fig(fig, out_path)
    return top


def plot_share_barh(df, label_col, value_col, title, out_path, top_n=8, drop_labels=None):
    d = df.copy()
    if drop_labels:
        d = d[~d[label_col].astype(str).isin(set(drop_labels))].copy()

    d[label_col] = d[label_col].astype(str)
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce").fillna(0)
    d = d.sort_values(value_col, ascending=False)

    top = d.head(int(top_n)).copy()
    other_sum = d.iloc[int(top_n):][value_col].sum()
    if other_sum > 0:
        top = pd.concat([top, pd.DataFrame([{label_col: "سایر", value_col: other_sum}])], ignore_index=True)

    total = float(top[value_col].sum()) if float(top[value_col].sum()) else 1.0
    top["pct"] = top[value_col] / total * 100.0

    top["_label"] = top[label_col].map(display_label)
    top = top.sort_values(value_col, ascending=True)

    fig, ax = plt.subplots(figsize=(10, max(4, 0.38 * len(top) + 1)))
    sns.barplot(data=top, x=value_col, y=top["_label"].map(fa), ax=ax, orient="h")
    ax.set_title(fa(title))
    ax.set_xlabel(fa("تعداد آگهی"))
    ax.set_ylabel("")

    xlim = ax.get_xlim()
    span = xlim[1] - xlim[0] if xlim[1] != xlim[0] else 1
    offset = span * 0.01
    for bar, (_, r) in zip(ax.patches, top.iterrows()):
        width = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax.text(
            width + offset,
            y,
            fa(f"{int(r[value_col]):,}  -  {r['pct']:.1f}%"),
            va="center",
            ha="left",
            fontsize=8,
        )

    save_fig(fig, out_path)
    return top





def plot_summary_card(summary_lines: list[str], out_path: Path):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()
    title = fa("خلاصه مدیریتی خروجی‌ها")
    ax.text(0.02, 0.95, title, fontsize=14, fontweight="bold", ha="left", va="top")

    y = 0.88
    for line in summary_lines:
        ax.text(0.02, y, fa(line), fontsize=10, ha="left", va="top")
        y -= 0.07

    save_fig(fig, out_path)


def plot_experience_hist(df_ads: pd.DataFrame, out_path: Path):
    if "exp_min_years" not in df_ads.columns:
        return

    exp = pd.to_numeric(df_ads["exp_min_years"], errors="coerce").dropna()
    exp = exp[(exp >= 0) & (exp <= 30)]
    if exp.empty:
        return

    fig, ax = plt.subplots(figsize=(11, 4.5))
    sns.histplot(exp, bins=list(range(0, 31)), ax=ax)
    ax.set_title(fa("توزیع حداقل سابقه (سال)"))
    ax.set_xlabel(fa("سال سابقه"))
    ax.set_ylabel(fa("تعداد آگهی"))
    save_fig(fig, out_path)


def plot_experience_by_role(df_ads: pd.DataFrame, out_path: Path, top_roles: int = 8):
    role_col = "job_role_fa" if "job_role_fa" in df_ads.columns else None
    if role_col is None or "exp_min_years" not in df_ads.columns:
        return

    d = df_ads[[role_col, "exp_min_years"]].copy()
    d[role_col] = d[role_col].astype(str)
    d["exp_min_years"] = pd.to_numeric(d["exp_min_years"], errors="coerce")
    d = d.dropna(subset=["exp_min_years"])
    d = d[(d["exp_min_years"] >= 0) & (d["exp_min_years"] <= 30)]
    if d.empty:
        return

    top = d[role_col].value_counts().head(int(top_roles)).index.tolist()
    d = d[d[role_col].isin(top)].copy()
    d[role_col] = pd.Categorical(d[role_col], categories=top[::-1], ordered=True)

    fig, ax = plt.subplots(figsize=(12, max(4.5, 0.55 * len(top) + 2)))
    sns.boxplot(data=d, x="exp_min_years", y=d[role_col].map(fa), ax=ax, orient="h", showfliers=False)
    ax.set_title(fa("حداقل سابقه موردنیاز به تفکیک نقش شغلی"))
    ax.set_xlabel(fa("سال سابقه"))
    ax.set_ylabel(fa("نقش شغلی"))
    save_fig(fig, out_path)


def _download_wikimedia_png(url: str, out_path: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "telegram-job-mining/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        out_path.write_bytes(data)
        return True
    except Exception as e:
        print(f"WARN: Failed to download map image: {e}")
        return False


def _infer_map_extent_from_png(img: np.ndarray, lon_min: float, lon_max: float, lat_min: float, lat_max: float):

    try:
        if img.ndim == 3 and img.shape[2] >= 3:
            rgb = img[:, :, :3]
        else:
            return None

        if rgb.dtype != np.uint8:
            rgb_u8 = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
        else:
            rgb_u8 = rgb

        target = np.array([254, 254, 228], dtype=np.uint8)  # #FEFEE4
        diff = np.abs(rgb_u8.astype(np.int16) - target.astype(np.int16)).sum(axis=2)
        mask = diff <= 30  
        ys, xs = np.where(mask)
        if len(xs) < 5000:
            return None

        x0, x1 = int(xs.min()), int(xs.max())
        y0, y1 = int(ys.min()), int(ys.max())
        h, w = rgb_u8.shape[0], rgb_u8.shape[1]

        a, b = x0 / w, x1 / w
        if abs(b - a) < 1e-6:
            return None

       
        denom = (1 - a) * b - (1 - b) * a
        if abs(denom) < 1e-9:
            return None
        Xmin = (lon_min * b - lon_max * a) / denom
        Xmax = (lon_max * (1 - a) - lon_min * (1 - b)) / denom

        c, d = y0 / h, y1 / h
        if abs(d - c) < 1e-6:
            return None

        # For Y extents (top is Ymax, bottom is Ymin):
        # lat_max = (1-c)Ymax + cYmin
        # lat_min = (1-d)Ymax + dYmin
        denom_y = (1 - c) * d - (1 - d) * c
        if abs(denom_y) < 1e-9:
            return None
        Ymax = (lat_max * d - lat_min * c) / denom_y
        Ymin = (lat_min * (1 - c) - lat_max * (1 - d)) / denom_y

        return (float(Xmin), float(Xmax), float(Ymin), float(Ymax))
    except Exception:
        return None


def plot_iran_map_points(
    df_prov: pd.DataFrame,
    out_path: Path,
    df_ads_enriched: pd.DataFrame | None = None,
    offline: bool = False,
):
    if gpd is None:
        print("WARN: geopandas is not installed; plotting map without borders.")
       

    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "iran"
    assets_dir.mkdir(parents=True, exist_ok=True)
   
    map_png = assets_dir / "Iran_location_map_1200.png"
    if not map_png.exists() and not offline:
        url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Iran_location_map.svg/1200px-Iran_location_map.svg.png"
        _download_wikimedia_png(url, map_png)

    d = df_prov.copy()
    d["province"] = d["province"].astype(str)
    d["n_ads"] = pd.to_numeric(d["n_ads"], errors="coerce").fillna(0)

    d = d[d["province"].isin(PROVINCE_CENTERS.keys())].copy()
    if d.empty:
        print("⚠️ No provinces matched province centers for map.")
        return

    # Optional: color points by the most common job family in each province.
    prov_to_family: dict[str, str] = {}
    if isinstance(df_ads_enriched, pd.DataFrame) and {"province", "job_family_fa"}.issubset(set(df_ads_enriched.columns)):
        dd = df_ads_enriched[["province", "job_family_fa"]].copy()
        dd["province"] = dd["province"].astype(str)
        dd["job_family_fa"] = dd["job_family_fa"].astype(str)
        dd = dd.dropna(subset=["province", "job_family_fa"])
        dd = dd[~dd["province"].isin(["نامشخص", "Unknown", "other"])]
        if not dd.empty:
            top_fam = (
                dd.groupby(["province", "job_family_fa"], as_index=False)
                .size()
                .sort_values(["province", "size"], ascending=[True, False])
                .drop_duplicates(subset=["province"])
            )
            prov_to_family = dict(zip(top_fam["province"].astype(str), top_fam["job_family_fa"].astype(str)))

    lats, lons, sizes, colors, labels = [], [], [], [], []
    max_n = d["n_ads"].max() if d["n_ads"].max() else 1

    for _, r in d.iterrows():
        prov = r["province"]
        lat, lon = PROVINCE_CENTERS[prov]
        n = float(r["n_ads"])
        # Size scaling (sqrt) for visibility
        s = 40 + 900 * math.sqrt(n / max_n)

        lats.append(lat)
        lons.append(lon)
        sizes.append(s)
        labels.append(prov)
        colors.append(prov_to_family.get(prov, "نامشخص"))

    fam_palette = {}
    fam_values = [c for c in colors if c and c != "نامشخص"]
    if fam_values:
        fams = sorted(set(fam_values))
        pal = sns.color_palette("tab10", n_colors=len(fams))
        fam_palette = dict(zip(fams, pal))

    fig, ax = plt.subplots(figsize=(10, 9))
    if map_png.exists():
        img = mpimg.imread(map_png)
        extent = _infer_map_extent_from_png(img, lon_min=44, lon_max=63, lat_min=25, lat_max=40)
        ax.imshow(img, extent=extent if extent else (44, 63, 25, 40), zorder=0)

    
    if gpd is not None:
        try:
            world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
            iran = world[world["iso_a3"].astype(str).eq("IRN")]
            if iran.empty:
                iran = world[world["name"].astype(str).str.contains("Iran", case=False, na=False)]
            if not iran.empty:
                iran.boundary.plot(ax=ax, color="#23415f", linewidth=1.2, zorder=1)
        except Exception:
            pass

    ax.set_xlim(44, 63)
    ax.set_ylim(25, 40)
    ax.set_aspect("equal", adjustable="box")

    if fam_palette:
        point_colors = [fam_palette.get(c, "#1d4ed8") for c in colors]
        ax.scatter(lons, lats, s=sizes, c=point_colors, alpha=0.75, edgecolors="white", linewidths=0.7)

        from matplotlib.lines import Line2D

        handles = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor=fam_palette[f], markersize=8, label=fa(f))
            for f in sorted(fam_palette.keys())
        ]
        ax.legend(handles=handles, loc="lower right", title=fa("خانواده غالب"), frameon=False)
    else:
        ax.scatter(lons, lats, s=sizes, alpha=0.75, edgecolors="white", linewidths=0.7)

    for _, r in d.sort_values("n_ads", ascending=False).iterrows():
        lat, lon = PROVINCE_CENTERS[r["province"]]
        ax.text(
            lon + 0.18,
            lat + 0.12,
            fa(f"{r['province']} ({int(r['n_ads']):,})"),
            fontsize=7,
            fontweight="bold",
        )

    ax.set_title(fa("نقشه ایران: توزیع آگهی‌ها (اندازه = تعداد، رنگ = خانواده غالب)"))
    ax.set_axis_off()
    save_fig(fig, out_path)


def plot_iran_map_city_points(
    df_city: pd.DataFrame,
    out_path: Path,
    offline: bool = False,
    top_n: int = 30,
):
    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "iran"
    assets_dir.mkdir(parents=True, exist_ok=True)
    map_png = assets_dir / "Iran_location_map_1200.png"
    if not map_png.exists() and not offline:
        url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Iran_location_map.svg/1200px-Iran_location_map.svg.png"
        _download_wikimedia_png(url, map_png)

    d = df_city.copy()
    if not {"city", "n_ads"}.issubset(set(d.columns)):
        return

    d["city"] = d["city"].astype(str)
    d["n_ads"] = pd.to_numeric(d["n_ads"], errors="coerce").fillna(0)
    d = d[~d["city"].isin(["نامشخص", "Unknown", "other"])].copy()
    d = d.sort_values("n_ads", ascending=False).head(int(top_n))

    # Keep only cities we can place on map.
    d = d[d["city"].isin(CITY_CENTERS.keys())].copy()
    if d.empty:
        return

    max_n = d["n_ads"].max() if d["n_ads"].max() else 1
    lats, lons, sizes = [], [], []
    for _, r in d.iterrows():
        lat, lon = CITY_CENTERS[r["city"]]
        n = float(r["n_ads"])
        s = 35 + 700 * math.sqrt(n / max_n)
        lats.append(lat)
        lons.append(lon)
        sizes.append(s)

    fig, ax = plt.subplots(figsize=(10, 9))
    if map_png.exists():
        img = mpimg.imread(map_png)
        extent = _infer_map_extent_from_png(img, lon_min=44, lon_max=63, lat_min=25, lat_max=40)
        ax.imshow(img, extent=extent if extent else (44, 63, 25, 40), zorder=0)

    if gpd is not None:
        try:
            world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
            iran = world[world["iso_a3"].astype(str).eq("IRN")]
            if iran.empty:
                iran = world[world["name"].astype(str).str.contains("Iran", case=False, na=False)]
            if not iran.empty:
                iran.boundary.plot(ax=ax, color="#23415f", linewidth=1.2, zorder=1)
        except Exception:
            pass

    ax.scatter(lons, lats, s=sizes, c="#1d4ed8", alpha=0.75, edgecolors="white", linewidths=0.7, zorder=2)

    for _, r in d.iterrows():
        city_name = str(r["city"])
        lat, lon = CITY_CENTERS[city_name]
        dx, dy = CITY_LABEL_OFFSETS_POINTS.get(city_name, (6, 6))
        ha = "left" if dx >= 0 else "right"
        va = "bottom" if dy >= 0 else "top"
        ax.annotate(
            fa(f"{city_name} ({int(r['n_ads']):,})"),
            xy=(lon, lat),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=8,
            fontweight="bold",
            ha=ha,
            va=va,
            zorder=3,
        )

    ax.set_xlim(44, 63)
    ax.set_ylim(25, 40)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(fa("نقشه ایران: توزیع آگهی‌ها به تفکیک شهر (عدد کنار هر نقطه = تعداد)"))
    ax.set_axis_off()
    save_fig(fig, out_path)


def plot_stacked_barh(
    df: pd.DataFrame,
    group_col: str,
    cat_col: str,
    value_col: str,
    title: str,
    out_path: Path,
    top_groups: int | None = 12,
    top_cats: int = 8,
    legend_title: str | None = None,
    normalize_to_pct: bool = False,
):
    if df is None or df.empty:
        return
    if not {group_col, cat_col, value_col}.issubset(set(df.columns)):
        return

    d = df[[group_col, cat_col, value_col]].copy()
    d[group_col] = d[group_col].astype(str)
    d[cat_col] = d[cat_col].astype(str)
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce").fillna(0)
    d = d.dropna(subset=[group_col, cat_col])

    if top_groups is not None:
        top_group_vals = (
            d.groupby(group_col)[value_col].sum().sort_values(ascending=False).head(int(top_groups)).index.tolist()
        )
        d = d[d[group_col].isin(top_group_vals)].copy()
    if d.empty:
        return

    top_cat_vals = (
        d.groupby(cat_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .head(int(top_cats))
        .index.tolist()
    )

    pv_raw = d.pivot_table(index=group_col, columns=cat_col, values=value_col, aggfunc="sum", fill_value=0)

    # Avoid duplicate "سایر" columns by always aggregating everything not in keep_cols.
    keep_cols = [c for c in top_cat_vals if c in pv_raw.columns and str(c) != "سایر"]
    other_cols = [c for c in pv_raw.columns if c not in keep_cols]
    pv2 = pv_raw[keep_cols].copy() if keep_cols else pd.DataFrame(index=pv_raw.index)
    if other_cols:
        pv2["سایر"] = pv_raw[other_cols].sum(axis=1)
    pv = pv2
    pv = pv.reindex(columns=keep_cols + (["سایر"] if "سایر" in pv.columns else []), fill_value=0)

    totals = pv.sum(axis=1).astype(float).replace(0, 1.0)
    if normalize_to_pct:
        pv = pv.div(totals, axis=0) * 100.0

    pv["__total"] = pv.sum(axis=1)
    pv = pv.sort_values("__total", ascending=True)

    fig, ax = plt.subplots(figsize=(12, max(5, 0.45 * len(pv) + 1.5)))
    left = pd.Series([0.0] * len(pv), index=pv.index)

    cats = [c for c in pv.columns if c != "__total"]
    pal = sns.color_palette("tab10", n_colors=len(cats))
    for cat, color in zip(cats, pal):
        ax.barh(pv.index.map(fa), pv[cat].values, left=left.values, label=fa(display_label(cat)), color=color, alpha=0.9)
        left += pv[cat]

    # Add room on the right for total annotations (especially in percent mode).
    if normalize_to_pct:
        ax.set_xlim(0, 110)
    else:
        x0, x1 = ax.get_xlim()
        span0 = x1 - x0 if x1 != x0 else 1
        ax.set_xlim(x0, x1 + span0 * 0.08)

    # Annotate totals at end of bars (use raw totals even in percent mode).
    raw_totals = totals.reindex(pv.index)
    xlim = ax.get_xlim()
    span = xlim[1] - xlim[0] if xlim[1] != xlim[0] else 1
    offset = span * 0.01
    for y_idx, (g, total_raw) in enumerate(raw_totals.items()):
        ax.text(float(pv["__total"].iloc[y_idx]) + offset, y_idx, fa(f"{int(total_raw):,}"), va="center", ha="left", fontsize=8)

    ax.set_title(fa(title))
    ax.set_xlabel(fa("درصد") if normalize_to_pct else fa("تعداد آگهی"))
    ax.set_ylabel("")
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=False,
        title=fa(legend_title) if legend_title else None,
    )
    save_fig(fig, out_path)


def plot_role_top_skills_panels(rs: pd.DataFrame, out_path: Path, top_roles: int = 8, top_skills: int = 8):
    if rs is None or rs.empty:
        return

    role_col = "عنوان_شغل_استاندارد" if "عنوان_شغل_استاندارد" in rs.columns else None
    if role_col is None or not {"skill", "pct_of_role", "n_ads", "n_ads_role"}.issubset(set(rs.columns)):
        return

    d = rs.copy()
    d[role_col] = d[role_col].astype(str)
    d["skill"] = d["skill"].astype(str)
    d["pct_of_role"] = pd.to_numeric(d["pct_of_role"], errors="coerce").fillna(0)
    d["n_ads"] = pd.to_numeric(d["n_ads"], errors="coerce").fillna(0)

    
    if "group" in d.columns:
        d = d[~d["group"].astype(str).eq("soft")].copy()

    role_totals = d[[role_col, "n_ads_role"]].drop_duplicates().sort_values("n_ads_role", ascending=False)
    roles = role_totals.head(int(top_roles))[role_col].tolist()
    d = d[d[role_col].isin(roles)].copy()
    if d.empty:
        return

    
    n_panels = len(roles)
    ncols = 2 if n_panels > 1 else 1
    nrows = int(math.ceil(n_panels / ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, max(5, 3.3 * nrows)))
    if hasattr(axes, "flatten"):
        axes = list(axes.flatten())
    else:
        axes = [axes]

    for ax, role in zip(axes, roles):
        g = d[d[role_col] == role].sort_values(["pct_of_role", "n_ads"], ascending=[False, False]).head(int(top_skills)).copy()
        if g.empty:
            ax.set_axis_off()
            continue

        g["pct"] = (g["pct_of_role"] * 100).round(1)
        g["_skill"] = g["skill"].map(display_label)
        sns.barplot(data=g, x="pct", y=g["_skill"].map(fa), ax=ax, orient="h")
        ax.set_title(fa(role))
        ax.set_xlabel(fa("درصد آگهی‌های نقش که مهارت را ذکر کرده‌اند"))
        ax.set_ylabel("")
        annotate_bars_h(ax, fmt="{:,.1f}%")

    
    for ax in axes[len(roles):]:
        ax.set_axis_off()

    fig.suptitle(fa("مهارت‌های پرتکرار در نقش‌های پرتکرار"), y=1.02, fontsize=13, fontweight="bold")
    save_fig(fig, out_path)


def plot_role_top_skills_pages(
    rs: pd.DataFrame,
    out_dir: Path,
    roles_per_page: int = 12,
    top_skills: int = 10,
):
    if rs is None or rs.empty:
        return

    role_col = "عنوان_شغل_استاندارد" if "عنوان_شغل_استاندارد" in rs.columns else None
    if role_col is None or not {"skill", "pct_of_role", "n_ads", "n_ads_role"}.issubset(set(rs.columns)):
        return

    out_dir.mkdir(parents=True, exist_ok=True)

    d = rs.copy()
    d[role_col] = d[role_col].astype(str)
    d["skill"] = d["skill"].astype(str)
    d["pct_of_role"] = pd.to_numeric(d["pct_of_role"], errors="coerce").fillna(0)
    d["n_ads"] = pd.to_numeric(d["n_ads"], errors="coerce").fillna(0)
    d["n_ads_role"] = pd.to_numeric(d["n_ads_role"], errors="coerce").fillna(0)

    if "group" in d.columns:
        d = d[~d["group"].astype(str).eq("soft")].copy()

    role_totals = d[[role_col, "n_ads_role"]].drop_duplicates().sort_values("n_ads_role", ascending=False)
    roles_all = role_totals[role_col].tolist()
    if not roles_all:
        return

    roles_per_page = max(1, int(roles_per_page))
    n_pages = int(math.ceil(len(roles_all) / roles_per_page))

    for page_idx in range(n_pages):
        start = page_idx * roles_per_page
        end = min(len(roles_all), (page_idx + 1) * roles_per_page)
        roles = roles_all[start:end]
        dd = d[d[role_col].isin(roles)].copy()
        if dd.empty:
            continue

        n_panels = len(roles)
        ncols = 2 if n_panels > 1 else 1
        nrows = int(math.ceil(n_panels / ncols))
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(14, max(5, 3.3 * nrows)))
        if hasattr(axes, "flatten"):
            axes = list(axes.flatten())
        else:
            axes = [axes]

        for ax, role in zip(axes, roles):
            g = (
                dd[dd[role_col] == role]
                .sort_values(["pct_of_role", "n_ads"], ascending=[False, False])
                .head(int(top_skills))
                .copy()
            )
            if g.empty:
                ax.set_axis_off()
                continue

            g["pct"] = (g["pct_of_role"] * 100).round(1)
            g["_skill"] = g["skill"].map(display_label)
            sns.barplot(data=g, x="pct", y=g["_skill"].map(fa), ax=ax, orient="h")
            ax.set_title(fa(role))
            ax.set_xlabel(fa("درصد آگهی‌های نقش که مهارت را ذکر کرده‌اند"))
            ax.set_ylabel("")
            annotate_bars_h(ax, fmt="{:,.1f}%")

        for ax in axes[len(roles) :]:
            ax.set_axis_off()

        fig.suptitle(
            fa(f"مهارت‌های پرتکرار در نقش‌ها (صفحه {page_idx + 1}/{n_pages})"),
            y=1.02,
            fontsize=13,
            fontweight="bold",
        )
        save_fig(fig, out_dir / f"role_top_skills_page_{page_idx + 1:02d}.png")


def configure_stdout():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def maybe_plot(df: pd.DataFrame | None, fn, *args, **kwargs):
    if df is None or df.empty:
        return None
    return fn(df, *args, **kwargs)


def main():
    configure_stdout()

    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs-dir", type=str, default="outputs", help="Directory containing output CSVs")
    parser.add_argument("--fig-dir", type=str, default="outputs/figures", help="Directory to save figures")
    parser.add_argument("--top-n", type=int, default=20, help="Top-N items for bar charts")
    parser.add_argument("--no-map", action="store_true", help="Skip Iran map plot even if geopandas is installed")
    parser.add_argument("--offline", action="store_true", help="Do not download any external assets (e.g., Iran map)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outputs_dir = (root / args.outputs_dir).resolve()
    fig_dir = (root / args.fig_dir).resolve()
    ensure_dir(fig_dir)

    set_main_theme()

    skills = None
    roles = None
    fams = None
    prov = None
    ads_enriched = None

    enriched_path = outputs_dir / "ads_enriched.csv"
    if enriched_path.exists():
        ads_enriched = load_csv(enriched_path)

    # ----------------------------
    # Skills
    # ----------------------------
    skills_path = outputs_dir / "skills_counts.csv"
    if skills_path.exists():
        skills = load_csv(skills_path)
        maybe_plot(
            skills,
            plot_barh,
            "skill",
            "n_ads",
            "مهارت‌های پرتکرار",
            fig_dir / "skills_top.png",
            top_n=args.top_n,
            x_label="تعداد آگهی",
        )
        
        maybe_plot(
            skills,
            plot_barh,
            "skill",
            "n_ads",
            "اهمیت مهارت‌ها (فراوانی ذکر در آگهی‌ها)",
            fig_dir / "skills_importance_all.png",
            top_n=int(len(skills)),
            x_label="تعداد آگهی",
            annotate=True,
            fig_width=18.0,
            height_per_item=0.45,
            base_height=2.5,
            annotate_fontsize=8,
        )
        
        if {"category", "n_ads"}.issubset(set(skills.columns)):
            by_cat = skills.groupby("category", as_index=False)["n_ads"].sum().sort_values("n_ads", ascending=False)
            maybe_plot(
                by_cat,
                plot_barh,
                "category",
                "n_ads",
                "توزیع مهارت‌ها بر اساس دسته‌بندی",
                fig_dir / "skills_by_category.png",
                top_n=20,
                x_label="تعداد آگهی",
            )
            maybe_plot(
                by_cat,
                plot_donut,
                "category",
                "n_ads",
                "سهم دسته‌های مهارتی (دایره‌ای)",
                fig_dir / "skills_by_category_pie.png",
                top_n=8,
            )

        # Capital market certificates (only the 7 main certificates)
        if {"group", "skill", "n_ads"}.issubset(set(skills.columns)):
            certs = skills[skills["group"].astype(str).eq("certificate") & skills["category"].astype(str).eq("capital_market")].copy()
            if not certs.empty:
                maybe_plot(
                    certs,
                    plot_barh,
                    "skill",
                    "n_ads",
                    "گواهی های بازار سرمایه در آگهی ها",
                    fig_dir / "certificates_top.png",
                    top_n=12,
                    x_label="تعداد آگهی",
                )
        maybe_plot(
            skills,
            plot_pareto,
            "skill",
            "n_ads",
            "نمودار پارتو مهارت‌ها",
            fig_dir / "skills_pareto.png",
            top_n=args.top_n,
            y_label="تعداد آگهی",
        )
    else:
        print(f"WARN: Missing file: {skills_path}")

  
    role_path = outputs_dir / "job_role_counts_fa.csv"
    if role_path.exists():
        roles = load_csv(role_path)
        if roles.shape[1] >= 2:
            label_col, value_col = roles.columns[0], roles.columns[1]
            maybe_plot(
                roles,
                plot_barh,
                label_col,
                value_col,
                "توزیع نقش‌های شغلی",
                fig_dir / "job_roles_top.png",
                top_n=int(len(roles)),
                drop_labels=["سایر", "other", "Unknown"],
            )
            
            maybe_plot(
                roles,
                plot_share_barh,
                label_col,
                value_col,
                "سهم نقش‌های شغلی (تعداد و درصد)",
                fig_dir / "job_roles_donut.png",
                top_n=int(len(roles)),
                drop_labels=["other", "Unknown"],
            )
            maybe_plot(
                roles,
                plot_donut,
                label_col,
                value_col,
                "سهم نقش‌های شغلی (دایره‌ای)",
                fig_dir / "job_roles_pie.png",
                top_n=10,
            )
    else:
        print(f"WARN: Missing file: {role_path}")

    fam_path = outputs_dir / "job_family_counts_fa.csv"
    if fam_path.exists():
        fams = load_csv(fam_path)
        if fams.shape[1] >= 2:
            label_col, value_col = fams.columns[0], fams.columns[1]
            maybe_plot(
                fams,
                plot_barh,
                label_col,
                value_col,
                "توزیع خانواده‌های شغلی",
                fig_dir / "job_families_top.png",
                top_n=int(len(fams)),
                annotate=True,
            )
           
            maybe_plot(
                fams,
                plot_share_barh,
                label_col,
                value_col,
                "سهم خانواده‌های شغلی (تعداد و درصد)",
                fig_dir / "job_families_donut.png",
                top_n=int(len(fams)),
                drop_labels=["other", "Unknown"],
            )
            maybe_plot(
                fams,
                plot_donut,
                label_col,
                value_col,
                "سهم خانواده‌های شغلی (دایره‌ای)",
                fig_dir / "job_families_pie.png",
                top_n=10,
            )
    else:
        print(f"WARN: Missing file: {fam_path}")

    prov_path = outputs_dir / "province_counts.csv"
    if prov_path.exists():
        prov = load_csv(prov_path)
        maybe_plot(
            prov,
            plot_barh,
            "province",
            "n_ads",
            "توزیع آگهی‌ها به تفکیک استان",
            fig_dir / "province_counts_top.png",
            top_n=min(args.top_n, 20),
            drop_labels=["نامشخص", "Unknown", "other"],
            x_label="تعداد آگهی",
        )
        if not args.no_map:
            plot_iran_map_points(
                prov,
                fig_dir / "iran_map_points.png",
                df_ads_enriched=ads_enriched,
                offline=bool(args.offline),
            )
    else:
        print(f"WARN: Missing file: {prov_path}")

    city_path = outputs_dir / "city_counts.csv"
    if city_path.exists():
        city = load_csv(city_path)
        maybe_plot(
            city,
            plot_barh,
            "city",
            "n_ads",
            "توزیع آگهی‌ها به تفکیک شهر",
            fig_dir / "city_counts_top.png",
            top_n=min(args.top_n, 25),
            drop_labels=["نامشخص", "Unknown", "other"],
            x_label="تعداد آگهی",
        )
        if not args.no_map:
            plot_iran_map_city_points(
                city,
                fig_dir / "iran_city_map_points.png",
                offline=bool(args.offline),
                top_n=30,
            )
    else:
        print(f"WARN: Missing file: {city_path}")

    teh_nei_path = outputs_dir / "tehran_neighborhood_counts.csv"
    if teh_nei_path.exists():
        tehran_nei = load_csv(teh_nei_path)
        maybe_plot(
            tehran_nei,
            plot_barh,
            "tehran_neighborhood",
            "n_ads",
            "تهران: توزیع آگهی‌ها به تفکیک محله",
            fig_dir / "tehran_neighborhoods_top.png",
            top_n=min(args.top_n, 25),
            drop_labels=["نامشخص", "Unknown", "other"],
            x_label="تعداد آگهی",
        )
    else:
        print(f"WARN: Missing file: {teh_nei_path}")

    teh_dist_path = outputs_dir / "tehran_district_counts.csv"
    if teh_dist_path.exists():
        tehran_dist = load_csv(teh_dist_path)
        maybe_plot(
            tehran_dist,
            plot_barh,
            "tehran_district",
            "n_ads",
            "تهران: توزیع آگهی‌ها به تفکیک منطقه",
            fig_dir / "tehran_districts_top.png",
            top_n=min(args.top_n, 25),
            drop_labels=["نامشخص", "Unknown", "other"],
            x_label="تعداد آگهی",
        )

    skills_ads_path = outputs_dir / "ads_with_skills.csv"
    if skills_ads_path.exists():
        skills_ads = load_csv(skills_ads_path)
        plot_experience_hist(skills_ads, fig_dir / "experience_min_hist.png")

    if isinstance(ads_enriched, pd.DataFrame) and not ads_enriched.empty:
        plot_experience_by_role(ads_enriched, fig_dir / "experience_by_role.png")

        
        fam_col = "job_family_fa" if "job_family_fa" in ads_enriched.columns else None
        if fam_col and "province" in ads_enriched.columns:
            tmp = ads_enriched[["province", fam_col]].copy()
            tmp = tmp.dropna(subset=["province", fam_col])
            tmp = tmp[~tmp["province"].astype(str).isin(["نامشخص", "Unknown", "other"])]
            if not tmp.empty:
                tmp["n_ads"] = 1
                plot_stacked_barh(
                    tmp,
                    group_col="province",
                    cat_col=fam_col,
                    value_col="n_ads",
                    title="ترکیب خانواده‌های شغلی در استان‌های پرتکرار",
                    out_path=fig_dir / "province_top_families_stacked.png",
                    top_groups=12,
                    top_cats=8,
                    legend_title="خانواده شغلی",
                )
                # For small provinces, use a 100% stacked view so composition is visible.
                plot_stacked_barh(
                    tmp,
                    group_col="province",
                    cat_col=fam_col,
                    value_col="n_ads",
                    title="ترکیب خانواده‌های شغلی در استان‌ها (درصد)",
                    out_path=fig_dir / "province_family_heatmap.png",
                    top_groups=None,
                    top_cats=8,
                    legend_title="خانواده شغلی",
                    normalize_to_pct=True,
                )

   
    skill_group_path = outputs_dir / "skill_group_counts.csv"
    if skill_group_path.exists():
        sg = load_csv(skill_group_path)
        maybe_plot(
            sg,
            plot_barh,
            "group",
            "n_ads",
            "توزیع مهارت‌ها بر اساس نوع (سخت/نرم/ابزار/دانش/گواهی)",
            fig_dir / "skills_by_group.png",
            top_n=20,
            x_label="تعداد آگهی",
        )

    role_group_path = outputs_dir / "role_skill_group_counts.csv"
    if role_group_path.exists():
        rg = load_csv(role_group_path)
        if {"job_role_fa", "group", "n_ads"}.issubset(set(rg.columns)):
            plot_stacked_barh(
                rg,
                group_col="job_role_fa",
                cat_col="group",
                value_col="n_ads",
                title="نقش‌های پرتکرار: ترکیب نوع مهارت‌های ذکر شده",
                out_path=fig_dir / "role_skill_groups_stacked.png",
                top_groups=12,
                top_cats=8,
                legend_title="نوع مهارت",
            )

    cert_by_role_path = outputs_dir / "certificates_by_role.csv"
    if cert_by_role_path.exists():
        cr = load_csv(cert_by_role_path)
        if {"job_role_fa", "skill", "n_ads"}.issubset(set(cr.columns)):
            plot_stacked_barh(
                cr,
                group_col="job_role_fa",
                cat_col="skill",
                value_col="n_ads",
                title="نقش گواهی های بازار سرمایه",
                out_path=fig_dir / "certificates_by_role_stacked.png",
                top_groups=12,
                top_cats=8,
                legend_title="گواهی‌نامه",
            )

    
    role_skill_path = outputs_dir / "role_skill_lift_all.csv"
    if role_skill_path.exists():
        rs = load_csv(role_skill_path)
        plot_role_top_skills_panels(rs, fig_dir / "role_top_skills_panels.png", top_roles=8, top_skills=8)
        plot_role_top_skills_pages(rs, fig_dir / "role_top_skills_pages", roles_per_page=12, top_skills=10)

 
    nei_role_path = outputs_dir / "tehran_neighborhood_role_counts.csv"
    if nei_role_path.exists():
        nr = load_csv(nei_role_path)
        if {"tehran_neighborhood", "job_role", "n_ads"}.issubset(set(nr.columns)):
            plot_stacked_barh(
                nr,
                group_col="tehran_neighborhood",
                cat_col="job_role",
                value_col="n_ads",
                title="تهران: ترکیب نقش‌های شغلی در محله‌های پرتکرار",
                out_path=fig_dir / "tehran_neighborhood_top_roles_stacked.png",
                top_groups=12,
                top_cats=10,
                legend_title="نقش شغلی",
            )

    dist_role_path = outputs_dir / "tehran_district_role_counts.csv"
    if dist_role_path.exists():
        dr = load_csv(dist_role_path)
        if {"tehran_district", "job_role", "n_ads"}.issubset(set(dr.columns)):
            plot_stacked_barh(
                dr,
                group_col="tehran_district",
                cat_col="job_role",
                value_col="n_ads",
                title="تهران: ترکیب نقش‌های شغلی در مناطق پرتکرار",
                out_path=fig_dir / "tehran_district_top_roles_stacked.png",
                top_groups=12,
                top_cats=10,
                legend_title="نقش شغلی",
            )

    
    summary_lines = []
    if skills_path.exists():
        top_sk = skills.sort_values("n_ads", ascending=False).head(3)
        items = "، ".join([f"{display_label(r['skill'])} ({int(r['n_ads'])})" for _, r in top_sk.iterrows()])
        summary_lines.append(f"مهارت‌های پرتکرار: {items}")
    if role_path.exists() and roles is not None and roles.shape[1] >= 2:
        r_label, r_value = roles.columns[0], roles.columns[1]
        top_roles = roles.sort_values(r_value, ascending=False).head(3)
        items = "، ".join([f"{display_label(r[r_label])} ({int(r[r_value])})" for _, r in top_roles.iterrows()])
        summary_lines.append(f"نقش‌های پرتکرار: {items}")
    if fam_path.exists() and fams is not None and fams.shape[1] >= 2:
        f_label, f_value = fams.columns[0], fams.columns[1]
        top_fam = fams.sort_values(f_value, ascending=False).head(3)
        items = "، ".join([f"{display_label(r[f_label])} ({int(r[f_value])})" for _, r in top_fam.iterrows()])
        summary_lines.append(f"خانواده‌های پرتکرار: {items}")
    if prov_path.exists():
        top_prov = prov.sort_values("n_ads", ascending=False).head(3)
        items = "، ".join([f"{r['province']} ({int(r['n_ads'])})" for _, r in top_prov.iterrows()])
        summary_lines.append(f"استان‌های پرتکرار: {items}")
    if summary_lines:
        plot_summary_card(summary_lines, fig_dir / "summary_card.png")

    print(f"Saved figures to: {fig_dir}")


if __name__ == "__main__":
    main()
