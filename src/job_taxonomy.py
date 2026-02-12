# src/job_taxonomy.py


JOB_TITLE_PATTERNS = [
    # -----------------------
    # Trading (very specific first)
    # -----------------------
    {"code": "trader_energy", "family_fa": "معاملات و ترید", "role_fa": "معامله‌گر بورس انرژی",
     "pattern": r"معامله\s*گر.*بورس\s*انرژی|بورس\s*انرژی.*معامله\s*گر|energy.*trader"},

    {"code": "trader_commodity", "family_fa": "معاملات و ترید", "role_fa": "معامله‌گر بورس کالا",
     "pattern": r"معامله\s*گر.*بورس\s*کالا|بورس\s*کالا.*معامله\s*گر|commodity.*trader"},

    {"code": "trader_derivatives", "family_fa": "معاملات و ترید", "role_fa": "معامله‌گر مشتقه/آتی/اختیار",
     "pattern": r"معامله\s*گر.*(مشتقه|آتی|اختیار|آپشن)|trader.*(futures|options|derivatives)"},

    {"code": "trader_securities", "family_fa": "معاملات و ترید", "role_fa": "معامله‌گر اوراق بهادار",
     "pattern": r"معامله\s*گر.*(اوراق|بهادار|سهام)|معامله\s*گری\s*اوراق|securities\s*trader|equities\s*trader"},

    {"code": "trading_ops", "family_fa": "عملیات کارگزاری و پذیرش", "role_fa": "کارشناس عملیات معاملات/ایستگاه معاملاتی",
     "pattern": r"(ایستگاه\s*معاملاتی|اتاق\s*معاملات|سامانه\s*معاملاتی|OMS|ثبت\s*سفارش|عملیات\s*معاملات)"},

    # -----------------------
    # Brokerage / Admission / Backoffice
    # -----------------------
    {"code": "customer_admission", "family_fa": "عملیات کارگزاری و پذیرش", "role_fa": "کارشناس پذیرش مشتری/سجام",
     "pattern": r"(پذیرش\s*مشتری|پذیرش\s*مشتریان|سجام|احراز\s*هویت|کد\s*بورسی|افتتاح\s*حساب)"},

    {"code": "settlement_clearing", "family_fa": "پس از معامله و سپرده‌گذاری", "role_fa": "کارشناس تسویه و پایاپای/پس از معامله",
     "pattern": r"(تسویه|پایاپای|اتاق\s*پایاپای|پس\s*از\s*معامله|back\s*office|سمات|سپرده\s*گذاری)"},

    {"code": "custody", "family_fa": "پس از معامله و سپرده‌گذاری", "role_fa": "کارشناس امور سهام/سپرده‌گذاری",
     "pattern": r"(امور\s*سهام|سپرده\s*گذاری|سمات|گواهی\s*سپرده)"},

    # -----------------------
    # Funds / Portfolio
    # -----------------------
    {"code": "fund_accounting", "family_fa": "صندوق‌ها و سبدگردانی", "role_fa": "کارشناس حسابداری صندوق/NAV/صدور و ابطال",
     "pattern": r"(حسابداری\s*صندوق|NAV|صدور\s*و\s*ابطال|خالص\s*ارزش\s*دارایی|unit\s*holder)"},

    {"code": "fund_expert", "family_fa": "صندوق‌ها و سبدگردانی", "role_fa": "کارشناس صندوق‌های سرمایه‌گذاری",
     "pattern": r"(کارشناس\s*صندوق|صندوق(?:\s*های)?\s*سرمایه\s*گذاری)"},

    {"code": "portfolio_manager", "family_fa": "صندوق‌ها و سبدگردانی", "role_fa": "مدیر سبد/مدیر پرتفوی",
     "pattern": r"(مدیر\s*سبد|مدیر\s*پرتفو|مدیر\s*پرتفوی|portfolio\s*manager)"},

    {"code": "portfolio_expert", "family_fa": "صندوق‌ها و سبدگردانی", "role_fa": "کارشناس سبدگردانی/مدیریت پرتفوی",
     "pattern": r"(سبدگردان|سبدگردانی|کارشناس\s*سبد|مدیریت\s*پرتفو|مدیریت\s*پرتفوی|asset\s*allocation)"},

    # -----------------------
    # Analysis / Research / Valuation
    # -----------------------
    {"code": "equity_research", "family_fa": "تحلیل و پژوهش", "role_fa": "تحلیل‌گر بازار سرمایه",
     "pattern": r"(تحلیل\s*گر|تحلیلگر)\s*(بازار\s*سرمایه|سهام|اوراق|سرمایه\s*گذاری)|equity\s*research"},

    {"code": "valuation", "family_fa": "تحلیل و پژوهش", "role_fa": "کارشناس ارزش‌گذاری",
     "pattern": r"(ارزشگذاری|ارزشیابی)\s*(اوراق|شرکت|سهام)?|valuation"},

    {"code": "financial_modeling", "family_fa": "تحلیل و پژوهش", "role_fa": "کارشناس مدل‌سازی/پیش‌بینی مالی",
     "pattern": r"(مدل(?:سازی)?\s*مالی|financial\s*model|forecast|پیش\s*بینی\s*مالی|بودجه(?:\s*بندی)?)"},

    {"code": "technical_analysis", "family_fa": "تحلیل و پژوهش", "role_fa": "تحلیل‌گر تکنیکال",
     "pattern": r"(تحلیل\s*تکنیکال|پرایس\s*اکشن|RSI|MACD|ایچیموکو|technical\s*analysis)"},

    # -----------------------
    # Accounting (fine-grained)
    # -----------------------
    {"code": "accounting_payroll", "family_fa": "حسابداری و مالی", "role_fa": "کارشناس حقوق و دستمزد",
     "pattern": r"(حقوق\s*و\s*دستمزد|payroll|لیست\s*بیمه|فیش\s*حقوق|کارگزینی)"},

    {"code": "accounting_tax", "family_fa": "حسابداری و مالی", "role_fa": "کارشناس حسابداری مالیاتی",
     "pattern": r"(مالیاتی|tax|ارزش\s*افزوده|VAT|اظهارنامه|سامانه\s*مودیان|TTMS|گزارش\s*فصلی)"},

    {"code": "accounting_treasury", "family_fa": "حسابداری و مالی", "role_fa": "خزانه‌دار/کارشناس دریافت و پرداخت",
     "pattern": r"(خزانه(?:\s*داری)?|دریافت\s*و\s*پرداخت|تنخواه|چک|نقدینگی|cash\s*management)"},

    {"code": "accounting_financial", "family_fa": "حسابداری و مالی", "role_fa": "کارشناس حسابداری مالی/تهیه صورت‌های مالی",
     "pattern": r"(حسابداری\s*مالی|تهیه\s*صورت(?:های)?\s*مالی|ترازنامه|سود\s*و\s*زیان|دفتر\s*کل|ثبت\s*اسناد|سند\s*حسابداری)"},

    {"code": "accountant_general", "family_fa": "حسابداری و مالی", "role_fa": "حسابدار/کارشناس حسابداری",
     "pattern": r"(حسابدار|کارشناس\s*حسابداری|accounting)"},

    # -----------------------
    # Audit / Risk / Compliance
    # -----------------------
    {"code": "internal_audit", "family_fa": "حسابرسی و کنترل داخلی", "role_fa": "حسابرس داخلی/کنترل داخلی",
     "pattern": r"(حسابرسی\s*داخلی|internal\s*audit|کنترل\s*داخلی)"},

    {"code": "external_audit", "family_fa": "حسابرسی و کنترل داخلی", "role_fa": "حسابرسی مستقل/قانونی",
     "pattern": r"(حسابرسی\s*مستقل|موسسه\s*حسابرسی|external\s*audit)"},

    {"code": "risk_management", "family_fa": "ریسک و انطباق", "role_fa": "کارشناس مدیریت ریسک",
     "pattern": r"(مدیریت\s*ریسک|risk\s*management|ریسک\s*بازار|ریسک\s*اعتباری|ریسک\s*عملیاتی)"},

    {"code": "compliance_aml", "family_fa": "ریسک و انطباق", "role_fa": "کارشناس انطباق/مبارزه با پولشویی",
     "pattern": r"(انطباق|compliance|مبارزه\s*با\s*پولشویی|AML|KYC|شناخت\s*مشتری)"},

    # -----------------------
    # IT / Data
    # -----------------------
    {"code": "data_analyst", "family_fa": "داده و فناوری", "role_fa": "تحلیل‌گر داده/هوش تجاری",
     "pattern": r"(تحلیل\s*داده|data\s*analysis|power\s*bi|tableau|هوش\s*تجاری|BI)"},

    {"code": "developer", "family_fa": "داده و فناوری", "role_fa": "برنامه‌نویس/توسعه‌دهنده نرم‌افزار",
     "pattern": r"(برنامه\s*نویس|توسعه\s*دهنده|developer|python|django|flask|java|\.net|frontend|backend)"},

    {"code": "it_support", "family_fa": "داده و فناوری", "role_fa": "پشتیبان نرم‌افزار/شبکه",
     "pattern": r"(پشتیبان\s*نرم\s*افزار|support|شبکه|network|sysadmin|helpdesk)"},

    # -----------------------
    # Sales / Marketing
    # -----------------------
    {"code": "sales", "family_fa": "فروش و بازاریابی", "role_fa": "کارشناس فروش/توسعه بازار",
     "pattern": r"(فروش|sales|توسعه\s*بازار|بازاریابی|marketing)"},

    {"code": "digital_marketing", "family_fa": "فروش و بازاریابی", "role_fa": "دیجیتال مارکتینگ/محتوا/سئو",
     "pattern": r"(دیجیتال\s*مارکتینگ|digital\s*marketing|تولید\s*محتوا|content|seo|سئو)"},

    # -----------------------
    # Admin / Office / Ops
    # -----------------------
    {"code": "office_manager", "family_fa": "اداری و پشتیبانی", "role_fa": "مسئول دفتر/منشی",
     "pattern": r"(مسئول\s*دفتر|منشی|assistant|secretary)"},

    {"code": "cashier_runner", "family_fa": "اداری و پشتیبانی", "role_fa": "تحصیلدار/کارپرداز",
     "pattern": r"(تحصیلدار|کارپرداز|runner)"},

    # -----------------------
    # Management (keep late to avoid stealing matches)
    # -----------------------
    {"code": "operations_manager", "family_fa": "مدیریت", "role_fa": "مدیر عملیاتی",
     "pattern": r"(مدیر\s*عملیاتی|operations\s*manager)"},

    {"code": "manager_general", "family_fa": "مدیریت", "role_fa": "مدیر/سرپرست",
     "pattern": r"(مدیر|سرپرست|head\s*of|team\s*lead)"},
]
