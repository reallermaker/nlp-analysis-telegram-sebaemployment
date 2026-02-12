# Telegram Job Mining (SEBAemployment) — NLP Analysis

## فارسی

این پروژه خروجی **Telegram Export** (فایل‌های `messages*.html`) را به یک دیتاست قابل تحلیل تبدیل می‌کند و سپس گزارش‌ها و نمودارهای آماده ارائه تولید می‌کند. تمرکز پروژه روی آگهی‌های استخدامی حوزه مالی/بازار سرمایه ایران است.

### آمار دیتاست (خروجی فعلی)

- تعداد آگهی‌ها (Ad Groups): `8842`
- تعداد پیام‌ها/سمپل‌ها (Messages): `39083`

تعریف‌ها:

- آگهی (Ad): یک «گروه پیام» که ممکن است شامل چند پیام joined باشد. در خروجی‌ها با ستون `message_ids` مشخص می‌شود. در `outputs/ads_enriched.csv` هر سطر یک آگهی است.
- سمپل (Sample): یک پیام منفرد تلگرام (یک `message_id`). هر آگهی می‌تواند چند سمپل داشته باشد.

### ساختار پوشه‌ها

- `data/raw/`: فایل‌های خروجی تلگرام (مثلاً `messages.html`, `messages2.html`, ...)
- `src/`: کد استخراج/تحلیل/ویژوال
- `outputs/`: خروجی‌های جدولی (CSV) و گزارش‌ها
- `outputs/figures/`: نمودارهای خروجی (PNG)
- `assets/iran/`: دارایی‌های نقشه ایران برای نمودارهای جغرافیا

### نصب (Windows)

پیش‌نیاز: Python 3.10+ (تست‌شده با Python 3.13)

```powershell
cd telegram-job-mining
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### اجرای Pipeline

```powershell
# 1) Parse Telegram export -> ads
python src/parse_telegram.py --input-dir data/raw --output outputs/ads_parsed_all.csv

# 2) Skills extraction
python src/extract_skills.py

# 3) Job role/family standardization
python src/refine_job_titles.py

# 4) Role x Skill analysis + skill grouping
python src/analyze_role_skills.py
python src/analyze_skill_groups.py

# 5) Location extraction (province/city/Tehran) + role distribution by location
python src/analyze_locations.py
python src/analyze_location_roles.py

# 6) Master report + final enriched dataset
python src/make_master_report.py
python src/build_dataset.py

# 7) Charts (offline = no download)
python src/eda_viz.py --offline
```

### خروجی‌های مهم (CSV)

- دیتاست نهایی: `outputs/ads_enriched.csv` (یک سطر به‌ازای هر آگهی)
- گزارش جامع: `outputs/master_report.csv` (meta + manifest + خلاصه نتایج و جداول کلیدی)
- شمارش مهارت‌ها: `outputs/skills_counts_with_fa.csv`
- شمارش نقش‌ها/خانواده‌ها: `outputs/job_role_counts_fa.csv`, `outputs/job_family_counts_fa.csv`
- توزیع جغرافیایی: `outputs/province_counts.csv`, `outputs/city_counts.csv`
- تهران: `outputs/tehran_neighborhood_counts.csv`, `outputs/tehran_district_counts.csv`
- نقش×مهارت (Lift): `outputs/role_skill_lift_all.csv`
- گواهی‌های بازار سرمایه: `outputs/certificates_counts.csv`, `outputs/certificates_by_role.csv`

### نمودارهای تولیدشده (PNG)

فایل‌های زیر در `outputs/figures/` تولید می‌شوند و برای ارائه/گزارش آماده هستند:

- `skills_top.png`: مهارت‌های پرتکرار
- `skills_importance_all.png`: اهمیت مهارت‌ها (به‌همراه مقدار روی میله‌ها)
- `skills_pareto.png`: نمودار پارتو مهارت‌ها
- `skills_by_group.png`: توزیع مهارت‌ها بر اساس نوع (سخت/نرم/ابزار/دانش/گواهی)
- `skills_by_category.png`: توزیع مهارت‌ها بر اساس دسته
- `skills_by_category_pie.png`: نسخه دایره‌ای توزیع دسته‌ها
- `job_roles_top.png`: توزیع نقش‌های شغلی (میله‌ای)
- `job_roles_donut.png`: سهم نقش‌های شغلی (میله‌ای سهم/درصد)
- `job_roles_pie.png`: نسخه دایره‌ای نقش‌ها (Top)
- `job_families_top.png`: توزیع خانواده‌های شغلی (میله‌ای)
- `job_families_donut.png`: سهم خانواده‌های شغلی (میله‌ای سهم/درصد)
- `job_families_pie.png`: نسخه دایره‌ای خانواده‌ها (Top)
- `certificates_top.png`: میزان ذکر گواهی‌های بازار سرمایه در آگهی‌ها
- `certificates_by_role_stacked.png`: نقش گواهی های بازار سرمایه به تفکیک نقش‌های پرتکرار
- `role_skill_groups_stacked.png`: ترکیب نوع مهارت‌ها در نقش‌های پرتکرار
- `role_top_skills_panels.png`: مهارت‌های شاخص هر نقش (پنل‌های چندگانه)
- `province_counts_top.png`: توزیع آگهی‌ها به تفکیک استان (Top)
- `province_top_families_stacked.png`: ترکیب خانواده‌های شغلی در استان‌های پرتکرار
- `province_family_heatmap.png`: ترکیب خانواده‌ها در استان‌ها به‌صورت 100% (درصد)
- `city_counts_top.png`: توزیع آگهی‌ها به تفکیک شهر (Top)
- `iran_map_points.png`: نقشه ایران (استان‌ها؛ اندازه = تعداد، رنگ = خانواده غالب)
- `iran_city_map_points.png`: نقشه ایران (شهرها؛ نام شهر و تعداد کنار هر نقطه)
- `tehran_neighborhoods_top.png`: محله‌های پرتکرار تهران
- `tehran_neighborhood_top_roles_stacked.png`: ترکیب نقش‌ها در محله‌های پرتکرار تهران
- `tehran_districts_top.png`: مناطق پرتکرار تهران
- `tehran_district_top_roles_stacked.png`: ترکیب نقش‌ها در مناطق پرتکرار تهران
- `experience_min_hist.png`: توزیع حداقل سابقه استخراج‌شده
- `experience_by_role.png`: حداقل سابقه موردنیاز به تفکیک نقش (Boxplot)
- `summary_card.png`: کارت خلاصه مدیریتی خروجی‌ها

### گواهی‌های بازار سرمایه (7 مورد استاندارد)

در این پروژه گواهی‌های بازار سرمایه فقط این 7 مورد هستند:

1. اصول بازار سرمایه
2. تحلیل‌گری بازار سرمایه
3. معامله‌گری بازار سرمایه
4. ارزشیابی اوراق بهادار
5. مدیریت نهادهای بازار سرمایه
6. کارشناسی عرضه و پذیرش
7. مدیریت سبد اوراق بهادار

### نمایش فارسی و فونت‌ها

برای نمایش درست فارسی (RTL + شکل‌دهی حروف) از `arabic-reshaper` و `python-bidi` استفاده شده است (`src/viz_theme.py`).

فونت پیش‌فرض متن‌های فارسی **B Nazanin** است. از آنجا که این فونت معمولاً حروف لاتین را کامل پوشش نمی‌دهد، برای نمایش صحیح عبارت‌های لاتین مانند `NAV`, `SQL`, `Power BI`, `CRM`, `ICDL` در نمودارها از یک فونت لاتین جایگزین استفاده می‌شود تا به‌جای `?` درست نمایش داده شوند.

### انتشار در GitHub (محدودیت حجم فایل‌ها)

بعضی فایل‌های `outputs/ads_*.csv` بسیار بزرگ هستند و همچنین می‌توانند شامل متن کامل آگهی‌ها باشند؛ برای انتشار عمومی توصیه می‌شود:

- کدها و نمودارها را commit کنید (`src/`, `assets/`, `outputs/figures/`).
- فایل‌های خام و دیتاست‌های حجیم را در GitHub قرار ندهید (یا در صورت نیاز از Git LFS استفاده کنید).

---

## English

This project converts **Telegram Export** HTML files (`messages*.html`) into an analysis-ready dataset and produces reports and publication-ready charts. The focus is Iranian finance / capital market job ads.

### Dataset Stats (current outputs)

- Ads (ad groups): `8842`
- Messages (samples): `39083`

Definitions:

- Ad (group): a group of Telegram messages (may include joined messages). It is represented by `message_ids`. In `outputs/ads_enriched.csv`, each row corresponds to one ad.
- Sample: a single Telegram message (`message_id`). Each ad may contain multiple samples.

### Project Layout

- `data/raw/`: Telegram export files (e.g., `messages.html`, `messages2.html`, ...)
- `src/`: extraction, analytics, visualization code
- `outputs/`: generated CSV outputs and reports
- `outputs/figures/`: generated charts (PNG)
- `assets/iran/`: Iran map assets used by the geography charts

### Installation (Windows)

Requirement: Python 3.10+ (tested with Python 3.13)

```powershell
cd telegram-job-mining
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Run The Pipeline

```powershell
python src/parse_telegram.py --input-dir data/raw --output outputs/ads_parsed_all.csv
python src/extract_skills.py
python src/refine_job_titles.py
python src/analyze_role_skills.py
python src/analyze_skill_groups.py
python src/analyze_locations.py
python src/analyze_location_roles.py
python src/make_master_report.py
python src/build_dataset.py
python src/eda_viz.py --offline
```

### Key Outputs (CSV)

- Final dataset: `outputs/ads_enriched.csv` (one row per ad)
- Master report: `outputs/master_report.csv`
- Skill counts: `outputs/skills_counts_with_fa.csv`
- Role/family counts: `outputs/job_role_counts_fa.csv`, `outputs/job_family_counts_fa.csv`
- Geography: `outputs/province_counts.csv`, `outputs/city_counts.csv`
- Tehran: `outputs/tehran_neighborhood_counts.csv`, `outputs/tehran_district_counts.csv`
- Role × skill association (Lift): `outputs/role_skill_lift_all.csv`
- Capital market certificates: `outputs/certificates_counts.csv`, `outputs/certificates_by_role.csv`

### Generated Figures (PNG)

All charts are saved in `outputs/figures/` (see the Persian section for the full list and descriptions).

### Capital Market Certificates (7 official items)

This project tracks only these seven certificates:

1. Principles of Capital Market
2. Capital Market Analysis
3. Capital Market Trading
4. Securities Valuation
5. Capital Market Institutions Management
6. Supply & Admission Specialist
7. Portfolio Management

### Persian Text Rendering

For correct Persian rendering (RTL + shaping), the project uses `arabic-reshaper` and `python-bidi` (`src/viz_theme.py`).

The default Persian font is **B Nazanin**. Since it typically does not fully support Latin glyphs, Latin tokens such as `NAV`, `SQL`, `Power BI`, `CRM`, `ICDL` are rendered using a Latin-capable fallback font to avoid `?` glyphs in charts.

### Publishing To GitHub (file size)

Some `outputs/ads_*.csv` files can be large and may contain full ad texts. For public publishing:

- Commit code and charts (`src/`, `assets/`, `outputs/figures/`).
- Do not commit raw exports or large datasets (or use Git LFS if you must).

