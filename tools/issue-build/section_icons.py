# -*- coding: utf-8 -*-
"""Fixed section-type -> icon + accent colour mapping for Neurodynamics Digest, reused by every issue.
Icons: monochrome text symbols (Patrick's decision, 27 Oct 2026); U+FE0E forces text presentation where a
symbol has an emoji default. Colours: muted night-friendly accents, each >=4.5:1 against the #1c252e and
#26323d panels and the #33424f header bar (checked with the WCAG formula in contrast_report())."""
VS = "\ufe0e"
HEADER_BG = "#33424f"   # header bar: a step lighter than the panels (#1c252e / #26323d)
BRAND_RED = "#e0453b"   # masthead, No. box, PREPRINT badge
ICON_COLOR = BRAND_RED  # legacy name
FALLBACK = "\u25c6"     # ◆
FALLBACK_COLOR = "#c3a6f0"
SECTIONS = [  # (section type, title keywords, icon, accent colour, colour name)
    ("headline act",            ("headline",),                         "\u2605",      "#f0a35e", "amber"),      # ★
    ("EEG",                     ("eeg",),                              "\u223f",      "#5fc9bf", "teal"),       # ∿
    ("your own corner",         ("own corner",),                       "\u2302",      "#e8c15a", "gold"),       # ⌂
    ("psychedelic neuroimaging",("psychedelic neuroimaging",),         FALLBACK,      "#c3a6f0", "violet"),     # ◆ (no own icon yet)
    ("complexity/methods",      ("complexity", "dynamics", "methods"), "\u2211",      "#7fc0ee", "sky blue"),   # ∑
    ("weekly explainer",        ("explainer",),                        "\u03a6",      "#b9d86a", "lime"),       # Φ
    ("addiction",               ("addiction",),                        "\u27f3",      "#f095ad", "rose"),       # ⟳
    ("brain-body coupling",     ("brain\u2013body", "brain-body"),     "\u2665" + VS, "#f39a85", "coral"),      # ♥
    ("preclinical",             ("preclinical",),                      "\u2697" + VS, "#7ddcae", "mint"),       # ⚗
    ("critiques and nulls",     ("critique", "null"),                  "\u2205",      "#d0b090", "sand"),       # ∅
    ("rogue picks",             ("rogue", "wildcard"),                 "\u2726",      "#e3a5e0", "orchid"),     # ✦
    ("datasets and tools",      ("dataset", "tools"),                  "\u2699" + VS, "#9fb4f2", "periwinkle"), # ⚙
    ("policy pulse",            ("policy",),                           "\u2696" + VS, "#a8d8e8", "ice blue"),   # ⚖
    ("conferences",             ("conference",),                       "\u25ce",      "#e6d27a", "straw"),      # ◎
    ("summer schools/training", ("summer school", "training"),         "\u270e" + VS, "#a6dc8f", "sage green"), # ✎
    ("funding radar",           ("funding",),                          "\u00a3",      "#e7b97a", "honey"),      # £
    ("reviews",                 ("best reviews", "reviews of the week"), "\u2261",    "#b8c4d6", "silver"),     # ≡ "Best reviews of the week" (second-to-last, 4 Nov 2026)
    ("catch-up",                ("catch-up", "catch up"),                "\u21ba",    "#d0a882", "copper"),     # ↺ FINAL section (4 Nov 2026)
]
ICONS = [(t, k, i) for t, k, i, _, _ in SECTIONS]  # backwards compatible
def _match(title):
    t = title.lower()
    for row in SECTIONS:
        if any(k in t for k in row[1]):
            return row
    return None
def icon_for(title):
    r = _match(title); return r[2] if r else FALLBACK
def color_for(title):
    r = _match(title); return r[3] if r else FALLBACK_COLOR
def _lum(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def contrast(a, b):
    x, y = sorted((_lum(a), _lum(b)), reverse=True); return (x + 0.05) / (y + 0.05)
def contrast_report():
    return [(t, c, n, round(contrast(c, "#1c252e"), 2), round(contrast(c, "#26323d"), 2), round(contrast(c, HEADER_BG), 2)) for t, _, _, c, n in SECTIONS]

# ---- Masthead brainwave strip (replaces the circles/squares row; text only, survives image blocking) ----
# Three stacked "channels" in monospace, tinted with section accents, clipped with nowrap/overflow:hidden.
# Each trace has 48 wave glyphs + 20 line/spike glyphs so the channels end together (~650px at 12px); mobile clips the overflow.
BRAINWAVE = [
    ("Fz", "#5fc9bf", "\u223f\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u2500\u2500\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u2500\u2500\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u2500\u2500\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"),
    ("Cz", "#f0a35e", "\u223f\u223f\u223f\u2500\u2571\u2572\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u2571\u2572\u2571\u2572\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u2500\u2571\u2572\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u2500\u2571\u2572\u223f\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u223f"),
    ("Pz", "#c3a6f0", "\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u2500\u223f\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u2571\u2572\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u2500\u223f\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u2500\u223f\u223f\u223f\u223f\u2500\u223f\u223f\u223f\u223f\u223f\u2571\u2572\u2500\u223f\u223f\u223f\u223f\u223f\u223f\u223f\u2500\u2500\u2500\u2500\u2500\u2500"),
]
def brainwave_html(mono="monospace", label_color="#9aa7b2", size=12, lh=14, tstyle="", pad=0):
    lines = "<br>".join(f'{lab}&nbsp;&nbsp;<span style="color:{c}">{tr}</span>' for lab, c, tr in BRAINWAVE)
    # table-layout:fixed lets the cell clip instead of widening the layout on narrow screens
    return (f'<table width="100%" cellpadding="{pad}" cellspacing="0" style="{tstyle}table-layout:fixed"><tr>'
            f'<td style="white-space:nowrap;overflow:hidden;font:{size}px/{lh}px {mono};color:{label_color}">{lines}</td></tr></table>')
def brainwave_text():
    return "\n".join(f"{lab}  {tr}" for lab, _, tr in BRAINWAVE)
