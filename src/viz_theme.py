# src/viz_theme.py
# Keep comments and docstrings in English only.

from __future__ import annotations

import datetime
import re
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager


try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except Exception:
    arabic_reshaper = None
    get_display = None


def pick_persian_font() -> str:
    # Pick the first available Persian-capable font on Windows
    preferred = [
        "B Nazanin",
        "Vazirmatn",
        "Vazir",
        "IRANSans",
        "Tahoma",
        "Segoe UI",
        "Arial",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            return name
    return "DejaVu Sans"


def fa(text: str) -> str:
    # Shape + bidi for Persian/Arabic strings
    if text is None:
        return ""
    s = str(text)
    if arabic_reshaper is None or get_display is None:
        return s  # fallback: may look broken, but avoids crash
    # Only apply shaping if Arabic/Persian characters exist.
    if not re.search(r"[\u0600-\u06FF]", s):
        return s

    # Keep Latin chunks (e.g., NAV, SQL, CRM) left-to-right inside RTL text.
    # This reduces cases where acronyms get visually reversed after bidi.
    lrm = "\u200e"
    s = re.sub(r"([A-Za-z0-9_]+)", lambda m: f"{lrm}{m.group(1)}{lrm}", s)
    reshaped = arabic_reshaper.reshape(s)
    return get_display(reshaped)


def set_main_theme():
    plt.rcdefaults()
    font_name = pick_persian_font()

    if arabic_reshaper is None or get_display is None:
        print("WARN: Persian shaping disabled. Install 'arabic-reshaper' and 'python-bidi' for correct rendering.")

    sns.set_theme(
        style="white",
        context="notebook",
        rc={
            "figure.dpi": 160,
            "savefig.dpi": 300,
            "figure.facecolor": "#eaf2ff",
            "axes.facecolor":   "#f2fff6",

            "font.family": "sans-serif",
            # Keep B Nazanin as the primary look; render Latin chunks (NAV/SQL/...) via per-text overrides.
            "font.sans-serif": [font_name, "DejaVu Sans"],
            "axes.unicode_minus": False,

            "font.weight": "bold",
            "axes.labelweight": "bold",
            "axes.titleweight": "bold",

            "axes.edgecolor": "#23415f",
            "axes.linewidth": 1.3,
            "axes.spines.top": False,
            "axes.spines.right": False,

            "axes.grid": True,
            "grid.color": "#a9c0d8",
            "grid.alpha": 0.25,
            "grid.linewidth": 0.8,

            "text.color": "#0f1f33",
            "axes.labelcolor": "#23415f",
            "xtick.color": "#23415f",
            "ytick.color": "#23415f",

            "axes.titlesize": 12,
            "axes.titlepad": 10,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,

            "lines.linewidth": 2.0,
            "legend.frameon": False,
            "legend.fontsize": 9,
        },
    )
    sns.set_palette(["#1d4ed8", "#0ea5e9", "#16a34a", "#f59e0b", "#ef4444"])


def add_footer(fig, footer_text="Reallermaker", footer_color="#23415f"):
    year = datetime.date.today().year
    fig.text(
        0.01, 0.01, f"{footer_text} {year}",
        ha="left", va="bottom",
        fontsize=8, fontweight="bold", fontfamily="DejaVu Sans",
        alpha=0.85, color=footer_color,
    )
