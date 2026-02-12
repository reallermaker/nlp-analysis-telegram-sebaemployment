# src/skills_catalog.py
# Keep comments and docstrings in English only.

SKILL_PATTERNS = [
    # --------------------
    # Data / BI
    # --------------------
    {"skill": "Python", "group": "hard", "category": "data",
     "pattern": r"پایتون|(?<![A-Za-z0-9_])python(?![A-Za-z0-9_])"},
    {"skill": "SQL", "group": "hard", "category": "data",
     "pattern": r"اس\s*کیو\s*ال|مای\s*اس\s*کیو\s*ال|(?<![A-Za-z0-9_])sql(?![A-Za-z0-9_])|postgres|postgresql|oracle|t-?sql"},
    {"skill": "Power BI", "group": "hard", "category": "data",
     "pattern": r"power\s*bi|پاور\s*بی|پاوربی"},
    {"skill": "DAX", "group": "hard", "category": "data", "parent": "Power BI",
     "pattern": r"(?<![A-Za-z0-9_])dax(?![A-Za-z0-9_])|دایکس|داکس"},
    {"skill": "Power Query", "group": "hard", "category": "data",
     "pattern": r"power\s*query|پاور\s*کوئری|پاور\s*کوئری|کوئری\s*ادیتور"},
    {"skill": "Excel", "group": "hard", "category": "data",
     "pattern": r"اکسل|(?<![A-Za-z0-9_])excel(?![A-Za-z0-9_])"},
    {"skill": "Excel_PivotTable", "group": "hard", "category": "data", "parent": "Excel",
     "pattern": r"pivot\s*table|پیوت\s*تیبل|جدول\s*محوری|pivot"},
    {"skill": "Excel_VBA", "group": "hard", "category": "data", "parent": "Excel",
     "pattern": r"(?<![A-Za-z0-9_])vba(?![A-Za-z0-9_])|وی\s*بی\s*ای|ماکرو\s*نویسی|macro\s*excel"},
    {"skill": "Tableau", "group": "hard", "category": "data",
     "pattern": r"(?<![A-Za-z0-9_])tableau(?![A-Za-z0-9_])|تابلو"},
    {"skill": "Data Analysis", "group": "hard", "category": "data",
     "pattern": r"تحلیل\s*داده|data\s*analysis"},
    {"skill": "Machine Learning", "group": "hard", "category": "data",
     "pattern": r"یادگیری\s*ماشین|machine\s*learning"},
    {"skill": "Deep Learning", "group": "hard", "category": "data",
     "pattern": r"یادگیری\s*عمیق|deep\s*learning"},
    {"skill": "ETL", "group": "hard", "category": "data",
     "pattern": r"(?<![A-Za-z0-9_])etl(?![A-Za-z0-9_])|فرایند\s*etl|استخراج\s*تحویل\s*بارگذاری|extract\s*transform\s*load"},
    {"skill": "Pandas", "group": "hard", "category": "data",
     "pattern": r"(?<![A-Za-z0-9_])pandas(?![A-Za-z0-9_])|پانداس"},
    {"skill": "NumPy", "group": "hard", "category": "data",
     "pattern": r"(?<![A-Za-z0-9_])numpy(?![A-Za-z0-9_])|نامپای"},
    {"skill": "Scikit-learn", "group": "hard", "category": "data",
     "pattern": r"scikit-?learn|sklearn|سایکیت"},

    # --------------------
    # Capital Market (domain + operations + compliance)
    # --------------------
    {"skill": "Capital_Market_Domain", "group": "domain", "category": "capital_market",
     "pattern": r"بازار\s*سرمایه|نهاد\s*مالی|سازمان\s*بورس|کانون\s*کارگزاران|کانون\s*نهادهای\s*سرمایه\s*گذاری|شرکت\s*کارگزاری|سبدگردان|تأمین\s*سرمایه|مشاور\s*سرمایه\s*گذاری|پردازش\s*اطلاعات\s*مالی"},

    {"skill": "CM_Exchanges", "group": "domain", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"بورس\s*تهران|فرابورس|بورس\s*کالا|بورس\s*انرژی|(?<![A-Za-z0-9_])TSE(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])IFB(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])IME(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])IRENEX(?![A-Za-z0-9_])"},
    {"skill": "CM_Brokerage", "group": "domain", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"کارگزاری|معاملات\s*اوراق\s*بهادار|ایستگاه\s*معاملاتی|پذیرش\s*مشتری"},
    {"skill": "CM_Funds", "group": "domain", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"صندوق(?:\s*های)?\s*سرمایه\s*گذاری|صندوق\s*درآمد\s*ثابت|صندوق\s*سهامی|صندوق\s*مختلط|صندوق\s*طلا|ETF|(?<![A-Za-z0-9_])NAV(?![A-Za-z0-9_])"},
    {"skill": "CM_Asset_Management", "group": "domain", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"سبدگردان|سبدگردانی|مدیریت\s*دارایی|asset\s*management|مدیریت\s*پرتفو"},
    {"skill": "CM_Investment_Banking", "group": "domain", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"تأمین\s*سرمایه|investment\s*bank|پذیره\s*نویسی|تعهد\s*پذیره\s*نویسی|بازارگردانی|انتشار\s*اوراق"},
    {"skill": "CM_Market_Making", "group": "domain", "category": "capital_market", "parent": "CM_Investment_Banking",
     "pattern": r"بازارگردان(?:ی)?|market\s*making|market\s*maker|توافقنامه\s*بازارگردانی"},
    {"skill": "CM_Underwriting", "group": "domain", "category": "capital_market", "parent": "CM_Investment_Banking",
     "pattern": r"تعهد\s*پذیره\s*نویسی|پذیره\s*نویسی|underwriting"},

    {"skill": "CM_Custody_Settlement", "group": "hard", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"تسویه|پایاپای|اتاق\s*پایاپای|سپرده\s*گذاری|شرکت\s*سپرده\s*گذاری|سمات|پس\s*از\s*معامله|back\s*office"},
    {"skill": "CM_Codal_Disclosure", "group": "tool", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"کدال|افشا(?:ی)?\s*اطلاعات|اطلاعیه\s*شفاف\s*سازی|صورت(?:های)?\s*مالی\s*میاندوره(?:ای)?|گزارش\s*۱۲\s*ماهه"},

    {"skill": "CM_Regulations", "group": "domain", "category": "capital_market", "parent": "Capital_Market_Domain",
     "pattern": r"قوانین\s*بازار\s*سرمایه|قانون\s*بازار\s*اوراق\s*بهادار|دستورالعمل|آیین\s*نامه|مصوبات\s*سازمان\s*بورس"},
    {"skill": "CM_Compliance", "group": "domain", "category": "capital_market", "parent": "CM_Regulations",
     "pattern": r"انطباق|(?<![A-Za-z0-9_])compliance(?![A-Za-z0-9_])|واحد\s*انطباق|کنترل\s*داخلی"},
    {"skill": "AML_KYC", "group": "domain", "category": "capital_market", "parent": "CM_Regulations",
     "pattern": r"مبارزه\s*با\s*پولشویی|(?<![A-Za-z0-9_])AML(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])KYC(?![A-Za-z0-9_])|شناخت\s*مشتری|پایش\s*تراکنش"},

    # --------------------
    # Trading (parent + children)
    # --------------------
    {"skill": "Trading", "group": "hard", "category": "finance",
     "pattern": r"معامله\s*گر|معامله\s*گری|تریدر|(?<![A-Za-z0-9_])trader(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])trading(?![A-Za-z0-9_])"},

    {"skill": "Trading_Equities", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"سهام|equities|بازار\s*سهام|نماد"},
    {"skill": "Trading_FixedIncome", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"اوراق\s*بدهی|درآمد\s*ثابت|اخزا|صکوک|bond|fixed\s*income"},
    {"skill": "Trading_Derivatives", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"مشتقه|آتی|اختیار\s*معامله|آپشن|futures|options"},
    {"skill": "Trading_Commodity", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"بورس\s*کالا|گواهی\s*سپرده|commodity|رینگ\s*صادراتی|رینگ\s*داخلی"},
    {"skill": "Trading_Energy", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"بورس\s*انرژی|energy|نفت|گاز|فراورده\s*نفتی"},
    {"skill": "Trading_Technical", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"تحلیل\s*تکنیکال|technical\s*analysis|اندیکاتور|پرایس\s*اکشن|RSI|MACD|ایچیموکو|ichimoku|price\s*action"},
    {"skill": "Trading_Algo", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"معامله\s*گری\s*الگوریتمی|algorithmic\s*trading|ربات\s*معامله|trading\s*bot"},
    {"skill": "Trading_Forex", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"فارکس|(?<![A-Za-z0-9_])forex(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])fx(?![A-Za-z0-9_])|جفت\s*ارز"},
    {"skill": "Trading_Crypto", "group": "hard", "category": "finance", "parent": "Trading",
     "pattern": r"رمزارز|کریپتو|(?<![A-Za-z0-9_])crypto(?![A-Za-z0-9_])|bitcoin|btc|ethereum|eth"},

    # --------------------
    # Fund / Portfolio / Analysis / Valuation
    # --------------------
    {"skill": "Fund_Management", "group": "hard", "category": "finance",
     "pattern": r"مدیریت\s*صندوق|fund\s*management|مدیر\s*صندوق|portfolio\s*manager"},
    {"skill": "Fund_Accounting_NAV", "group": "hard", "category": "finance", "parent": "Fund_Management",
     "pattern": r"حسابداری\s*صندوق|(?<![A-Za-z0-9_])NAV(?![A-Za-z0-9_])|خالص\s*ارزش\s*دارایی|صدور\s*و\s*ابطال"},

    {"skill": "Portfolio", "group": "hard", "category": "finance",
     "pattern": r"پرتفو|portfolio|مدیریت\s*پرتفو|asset\s*allocation"},
    {"skill": "Portfolio_RiskMetrics", "group": "hard", "category": "finance", "parent": "Portfolio",
     "pattern": r"VaR|value\s*at\s*risk|بتا|انحراف\s*معیار|risk\s*metrics|حد\s*نصاب"},

    {"skill": "Financial_Analysis", "group": "hard", "category": "finance",
     "pattern": r"تحلیل\s*مالی|financial\s*analysis|تحلیل\s*صورت(?:های)?\s*مالی"},
    {"skill": "Financial_Modeling", "group": "hard", "category": "finance", "parent": "Financial_Analysis",
     "pattern": r"مدل(?:سازی)?\s*مالی|financial\s*model|forecast|پیش\s*بینی\s*مالی|بودجه(?:\s*بندی)?"},

    {"skill": "Valuation", "group": "hard", "category": "finance",
     "pattern": r"ارزشگذاری|valuation"},
    {"skill": "Valuation_DCF", "group": "hard", "category": "finance", "parent": "Valuation",
     "pattern": r"DCF|تنزیل\s*جریان\s*نقدی|discounted\s*cash\s*flow"},
    {"skill": "Valuation_Relative", "group": "hard", "category": "finance", "parent": "Valuation",
     "pattern": r"P/?E|P/?B|EV/?EBITDA|نسبت(?:های)?\s*ارزشیابی|multiple"},
    {"skill": "Valuation_NAV", "group": "hard", "category": "finance", "parent": "Valuation",
     "pattern": r"(?<![A-Za-z0-9_])NAV(?![A-Za-z0-9_])|ارزش\s*خالص\s*دارایی"},

    # --------------------
    # Reporting / Accounting / Audit / Risk
    # --------------------
    {"skill": "IFRS", "group": "domain", "category": "finance",
     "pattern": r"(?<![A-Za-z0-9_])ifrs(?![A-Za-z0-9_])|استاندارد(?:های)?\s*بین\s*المللی\s*گزارشگری"},
    {"skill": "Financial_Reporting", "group": "hard", "category": "finance", "parent": "IFRS",
     "pattern": r"تهیه\s*صورت(?:های)?\s*مالی|گزارش(?:گری)?\s*مالی|یادداشت(?:های)?\s*توضیحی|consolidation|تلفیق"},

    {"skill": "Accounting", "group": "hard", "category": "finance",
     "pattern": r"حسابداری|accounting"},
    {"skill": "Accounting_Financial", "group": "hard", "category": "finance", "parent": "Accounting",
     "pattern": r"حسابداری\s*مالی|financial\s*accounting|ثبت\s*اسناد|سند\s*حسابداری|دفتر\s*کل|closing"},
    {"skill": "Accounting_Tax", "group": "hard", "category": "finance", "parent": "Accounting",
     "pattern": r"مالیاتی|tax|ارزش\s*افزوده|VAT|اظهارنامه|TTMS|سامانه\s*مودیان|گزارش\s*فصلی"},
    {"skill": "Accounting_Payroll", "group": "hard", "category": "finance", "parent": "Accounting",
     "pattern": r"حقوق\s*و\s*دستمزد|payroll|لیست\s*بیمه|تامین\s*اجتماعی|فیش\s*حقوق"},
    {"skill": "Accounting_Cost", "group": "hard", "category": "finance", "parent": "Accounting",
     "pattern": r"حسابداری\s*صنعتی|بهای\s*تمام\s*شده|cost\s*accounting|کاردکس|انبار|کنترل\s*موجودی"},
    {"skill": "Treasury", "group": "hard", "category": "finance", "parent": "Accounting",
     "pattern": r"خزانه(?:\s*داری)?|دریافت\s*و\s*پرداخت|تنخواه|چک|نقدینگی|cash\s*management"},

    {"skill": "Audit", "group": "hard", "category": "finance",
     "pattern": r"حسابرسی|audit"},
    {"skill": "Audit_Internal", "group": "hard", "category": "finance", "parent": "Audit",
     "pattern": r"حسابرسی\s*داخلی|internal\s*audit|کنترل\s*داخلی"},
    {"skill": "Audit_External", "group": "hard", "category": "finance", "parent": "Audit",
     "pattern": r"حسابرسی\s*مستقل|external\s*audit|موسسه\s*حسابرسی|حسابرسی\s*قانونی"},

    {"skill": "Risk_Management", "group": "hard", "category": "finance",
     "pattern": r"مدیریت\s*ریسک|risk\s*management|ریسک"},
    {"skill": "Risk_Market", "group": "hard", "category": "finance", "parent": "Risk_Management",
     "pattern": r"ریسک\s*بازار|market\s*risk|VaR|stress\s*test|back\s*testing"},
    {"skill": "Risk_Credit", "group": "hard", "category": "finance", "parent": "Risk_Management",
     "pattern": r"ریسک\s*اعتباری|credit\s*risk|رتبه(?:\s*بندی)?\s*اعتباری"},
    {"skill": "Risk_Operational", "group": "hard", "category": "finance", "parent": "Risk_Management",
     "pattern": r"ریسک\s*عملیاتی|operational\s*risk|کنترل(?:های)?\s*فرایندی"},

    # --------------------
    # Certificates / Licenses
    # --------------------
    {"skill": "ICDL", "group": "certificate", "category": "computer_literacy",
     "pattern": r"(?<![A-Za-z0-9_])icdl(?![A-Za-z0-9_])|آی\s*سی\s*دی\s*ال|گواهینامه\s*icdl"},

    {"skill": "CM_Principles_Cert", "group": "certificate", "category": "capital_market",
     "pattern": r"اصول\s*بازار\s*سرمایه|گواهینامه\s*اصول\s*بازار\s*سرمایه|مدرک\s*اصول\s*بازار\s*سرمایه"},
    {"skill": "CM_Analysis_Cert", "group": "certificate", "category": "capital_market",
     "pattern": r"تحلیل\s*گری\s*بازار\s*سرمایه|گواهینامه\s*تحلیل\s*گری|مدرک\s*تحلیل\s*گری"},
    {"skill": "CM_Portfolio_Cert", "group": "certificate", "category": "capital_market",
     "pattern": r"مدیریت\s*سبد\s*اوراق\s*بهادار|مدیریت\s*سبد|گواهینامه\s*مدیریت\s*سبد|مدرک\s*مدیریت\s*سبد|گواهینامه\s*سبدگردانی|مدرک\s*سبدگردانی"},
    {"skill": "CM_Valuation_Cert", "group": "certificate", "category": "capital_market",
     "pattern": r"ارزشیابی\s*اوراق\s*بهادار|گواهینامه\s*ارزشیابی|مدرک\s*ارزشیابی"},
    {"skill": "CM_SupplyAdmission_Cert", "group": "certificate", "category": "capital_market",
     "pattern": r"عرضه\s*و\s*پذیرش|کارشناسی\s*عرضه\s*و\s*پذیرش|گواهینامه\s*عرضه\s*و\s*پذیرش|مدرک\s*عرضه\s*و\s*پذیرش"},
    {"skill": "CM_InstitutionsMgmt_Cert", "group": "certificate", "category": "capital_market",
     "pattern": r"مدیریت\s*نهادهای\s*بازار\s*سرمایه|مدیریت\s*نهادهای\s*مالی|گواهینامه\s*مدیریت\s*نهادها|مدرک\s*مدیریت\s*نهادها"},

    {"skill": "CM_Trading_Cert", "group": "certificate", "category": "capital_market",
     "pattern": r"معامله\s*گری\s*بازار\s*سرمایه|گواهینامه\s*معامله\s*گری\s*بازار\s*سرمایه|مدرک\s*معامله\s*گری\s*بازار\s*سرمایه|معامله\s*گری\s*اوراق(?:\s*بهادار)?|معامله\s*گر\s*اوراق(?:\s*بهادار)?|(?:معامله\s*گری|معامله\s*گر)\s*(?:بورس\s*)?کالا|گواهینامه\s*معامله\s*گری\s*بورس\s*کالا|مدرک\s*معامله\s*گری\s*بورس\s*کالا|(?:معامله\s*گری|معامله\s*گر)\s*(?:بورس\s*)?انرژی|گواهینامه\s*معامله\s*گری\s*بورس\s*انرژی|مدرک\s*معامله\s*گری\s*بورس\s*انرژی|(?:معامله\s*گری|معامله\s*گر)\s*(?:ابزار|اوراق)\s*مشتقه|قراردادهای\s*آتی|اختیار\s*معامله"},

    # --------------------
    # Tools / Software
    # --------------------
    {"skill": "TadbirPardaz", "group": "tool", "category": "finance_software",
     "pattern": r"تدبیر\s*پرداز|تدبیرپرداز"},
    {"skill": "Rahavard365", "group": "tool", "category": "finance_software",
     "pattern": r"رهآورد\s*365|رهآورد365|rahavard\s*365"},
    {"skill": "MetaTrader", "group": "tool", "category": "trading_platform",
     "pattern": r"متاتریدر|meta\s*trader|(?<![A-Za-z0-9_])mt4(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])mt5(?![A-Za-z0-9_])"},
    {"skill": "Sepidar", "group": "tool", "category": "accounting_software",
     "pattern": r"سپیدار"},
    {"skill": "RayanHamAfza", "group": "tool", "category": "accounting_software",
     "pattern": r"رایان\s*هم\s*افزا|rayan\s*ham\s*afza|ham\s*afza\s*rayan|hamafza\s*rayan"},
    {"skill": "HamkaranSystems", "group": "tool", "category": "erp_accounting",
     "pattern": r"همکاران\s*سیستم|راهکاران"},
    {"skill": "Office", "group": "tool", "category": "office_suite",
     "pattern": r"مایکروسافت\s*آفیس|آفیس|(?<![A-Za-z0-9_])office(?![A-Za-z0-9_])"},

    # --------------------
    # Marketing / Sales
    # --------------------
    {"skill": "Digital Marketing", "group": "hard", "category": "marketing",
     "pattern": r"دیجیتال\s*مارکتینگ|digital\s*marketing"},
    {"skill": "SEO", "group": "hard", "category": "marketing",
     "pattern": r"(?<![\u0600-\u06FF])سئو(?![\u0600-\u06FF])|(?<![A-Za-z0-9_])seo(?![A-Za-z0-9_])"},
    {"skill": "Content Marketing", "group": "hard", "category": "marketing",
     "pattern": r"تولید\s*محتوا|content\s*marketing"},
    {"skill": "CRM", "group": "tool", "category": "marketing",
     "pattern": r"(?<![A-Za-z0-9_])crm(?![A-Za-z0-9_])|سی\s*آر\s*ام|مدیریت\s*ارتباط\s*با\s*مشتری"},
    {"skill": "Sales", "group": "hard", "category": "marketing",
     "pattern": r"فروش|(?<![A-Za-z0-9_])sales(?![A-Za-z0-9_])"},
    {"skill": "Negotiation", "group": "soft", "category": "marketing",
     "pattern": r"مذاکره|negotiation"},

    # --------------------
    # Soft skills
    # --------------------
    {"skill": "Communication", "group": "soft", "category": "soft",
     "pattern": r"روابط\s*عمومی|ارتباطات|communication"},
    {"skill": "Teamwork", "group": "soft", "category": "soft",
     "pattern": r"کار\s*تیمی|team\s*work|teamwork"},
    {"skill": "Problem Solving", "group": "soft", "category": "soft",
     "pattern": r"حل\s*مسئله|problem\s*solving"},
    {"skill": "Time Management", "group": "soft", "category": "soft",
     "pattern": r"مدیریت\s*زمان|time\s*management"},
]
