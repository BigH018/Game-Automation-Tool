# ── Shared accent colours (same in both themes) ───────────────────────────────
C_ACCENT = "#2de8bc"   # electric teal  — active / running
C_DANGER = "#e8503d"   # warm red       — stopped / idle
C_GOLD   = "#f5c840"   # bright gold    — shiny detected


# ── Per-theme colour maps ─────────────────────────────────────────────────────
DARK = {
    "bg":       "#0c0d13",
    "surface":  "#111318",
    "border":   "#1d2035",
    "border_l": "#2d3358",
    "text":     "#c8ccdf",
    "muted":    "#565a78",
    "dim":      "#181a26",
    "log_text": "#767ca0",
}

LIGHT = {
    "bg":       "#f0f1f7",
    "surface":  "#ffffff",
    "border":   "#d0d3e8",
    "border_l": "#9fa5c8",
    "text":     "#1a1d2e",
    "muted":    "#4a5070",
    "dim":      "#e4e6f5",
    "log_text": "#3a4060",
}


def _build_stylesheet(c: dict) -> str:
    return f"""
/* ── Base ──────────────────────────────────────────────────── */
QWidget {{
    background-color: {c["bg"]};
    color: {c["text"]};
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    font-size: 12px;
}}

/* ── Frames / dividers ─────────────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    color: {c["border"]};
    max-height: 1px;
}}

/* ── Labels ────────────────────────────────────────────────── */
QLabel {{
    color: {c["muted"]};
    font-size: 11px;
    letter-spacing: 0.04em;
}}
QLabel#section_title {{
    color: {c["text"]};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 0.24em;
    padding: 3px 0 3px 8px;
    border-left: 2px solid {C_ACCENT};
}}
QLabel#guide_title {{
    color: {C_ACCENT};
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 0.1em;
}}
QLabel#guide_content {{
    color: {c["text"]};
    font-size: 13px;
}}
QLabel#tab_placeholder {{
    color: {c["muted"]};
    font-size: 12px;
    letter-spacing: 0.05em;
}}
QLabel#key_value {{
    color: {C_ACCENT};
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 0.14em;
}}
QLabel#header_sub {{
    color: {c["muted"]};
    font-size: 10px;
    letter-spacing: 0.2em;
}}

/* ── Custom tab bar ─────────────────────────────────────────── */
QScrollArea#tab_scroll {{
    border: none;
    background-color: transparent;
}}
QScrollArea#tab_scroll > QWidget {{
    background-color: transparent;
}}
QWidget#tab_strip {{
    background-color: transparent;
}}
QStackedWidget#tab_stack {{
    border: 1px solid {c["border"]};
    border-top: none;
    background-color: {c["bg"]};
}}
QPushButton#btn_tab {{
    background-color: {c["dim"]};
    color: {c["muted"]};
    border: 1px solid {c["border"]};
    border-bottom: none;
    padding: 10px 18px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.06em;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}}
QPushButton#btn_tab:checked {{
    background-color: {c["bg"]};
    color: {C_ACCENT};
    border-color: {c["border"]};
}}
QPushButton#btn_tab:hover:!checked {{
    background-color: {c["surface"]};
    color: {c["text"]};
    border-color: {c["border_l"]};
}}

/* ── Tab arrow buttons ──────────────────────────────────────── */
QPushButton#btn_tab_arrow {{
    background-color: {c["surface"]};
    border: 1px solid {c["border_l"]};
    border-radius: 4px;
    color: {C_ACCENT};
    font-size: 12px;
    font-weight: bold;
    padding: 0;
}}
QPushButton#btn_tab_arrow:hover {{
    background-color: {c["dim"]};
    border-color: {C_ACCENT};
}}
QPushButton#btn_tab_arrow:disabled {{
    color: {c["border"]};
    border-color: {c["border"]};
    background-color: {c["dim"]};
}}

/* ── Scroll area ────────────────────────────────────────────── */
QScrollArea {{
    border: none;
    background-color: {c["bg"]};
}}
QAbstractScrollArea > QWidget {{
    background-color: {c["bg"]};
}}

/* ── Line edits ────────────────────────────────────────────── */
QLineEdit, QDoubleSpinBox, QSpinBox {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    color: {c["text"]};
    padding: 6px 9px;
    font-size: 12px;
    selection-background-color: {C_ACCENT};
    selection-color: {c["bg"]};
}}
QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
    border: 1px solid {c["border_l"]};
    background-color: {c["dim"]};
}}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
QSpinBox::up-button,       QSpinBox::down-button {{
    width: 18px;
    background: {c["dim"]};
    border: none;
    border-left: 1px solid {c["border"]};
}}
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover,
QSpinBox::up-button:hover,       QSpinBox::down-button:hover {{
    background: {c["border_l"]};
}}

/* ── Buttons — base ────────────────────────────────────────── */
QPushButton {{
    background-color: {c["surface"]};
    border: 1px solid {c["border_l"]};
    border-radius: 4px;
    color: {c["text"]};
    padding: 7px 20px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.09em;
}}
QPushButton:hover   {{ border-color: {C_ACCENT}; color: {C_ACCENT}; background-color: {c["dim"]}; }}
QPushButton:pressed {{ background-color: {c["border"]}; }}
QPushButton:disabled {{ color: {c["border_l"]}; border-color: {c["border"]}; background-color: {c["surface"]}; }}

/* ── Buttons — small utility ───────────────────────────────── */
QPushButton#btn_browse,
QPushButton#btn_scan {{
    padding: 6px 12px;
    font-size: 10px;
    border-color: {c["border"]};
    color: {c["muted"]};
}}
QPushButton#btn_browse:hover,
QPushButton#btn_scan:hover {{ color: {c["text"]}; border-color: {c["border_l"]}; background-color: {c["dim"]}; }}

QPushButton#btn_clear {{
    padding: 4px 10px;
    font-size: 10px;
    border-color: {c["border"]};
    color: {c["muted"]};
    background-color: transparent;
}}
QPushButton#btn_clear:hover {{ color: {c["text"]}; border-color: {c["border_l"]}; }}

QPushButton#btn_rebind {{
    padding: 5px 14px;
    font-size: 10px;
    border-color: {c["border"]};
    color: {c["muted"]};
}}
QPushButton#btn_rebind:hover {{ color: {c["text"]}; border-color: {c["border_l"]}; background-color: {c["dim"]}; }}
QPushButton#btn_rebind[rebinding="true"] {{
    border-color: {C_GOLD};
    color: {C_GOLD};
    background-color: {c["dim"]};
}}

/* ── Buttons — notification toggle ──────────────────────────── */
QPushButton#btn_notif_toggle {{
    padding: 5px 16px;
    font-size: 10px;
}}
QPushButton#btn_notif_toggle[notif_on="false"] {{
    color: {c["muted"]};
    border-color: {c["border"]};
}}
QPushButton#btn_notif_toggle[notif_on="true"] {{
    color: {C_ACCENT};
    border-color: {C_ACCENT};
    background-color: {c["dim"]};
}}

QPushButton#btn_notif_test {{
    padding: 6px 14px;
    font-size: 10px;
    border-color: {c["border"]};
    color: {c["muted"]};
}}
QPushButton#btn_notif_test:hover {{ color: {c["text"]}; border-color: {c["border_l"]}; background-color: {c["dim"]}; }}
QPushButton#btn_notif_test:disabled {{
    color: {c["border_l"]};
    border-color: {c["border"]};
}}

/* ── Buttons — debug toggle ─────────────────────────────────── */
QPushButton#btn_debug_toggle {{
    padding: 5px 16px;
    font-size: 10px;
}}
QPushButton#btn_debug_toggle[debug_on="false"] {{
    color: {c["muted"]};
    border-color: {c["border"]};
}}
QPushButton#btn_debug_toggle[debug_on="true"] {{
    color: {C_ACCENT};
    border-color: {C_ACCENT};
    background-color: {c["dim"]};
}}

/* ── Buttons — header icons ────────────────────────────────── */
QPushButton#btn_theme,
QPushButton#btn_guide {{
    padding: 4px 10px;
    font-size: 11px;
    border-color: {c["border"]};
    color: {c["muted"]};
    letter-spacing: 0;
}}
QPushButton#btn_theme {{ font-size: 14px; }}
QPushButton#btn_theme:hover,
QPushButton#btn_guide:hover {{ color: {c["text"]}; border-color: {c["border_l"]}; background-color: {c["dim"]}; }}

/* ── Log text area ──────────────────────────────────────────── */
QTextEdit#log {{
    background-color: {c["surface"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    color: {c["log_text"]};
    font-size: 11px;
    line-height: 1.7;
    padding: 10px 12px;
    selection-background-color: {C_ACCENT};
    selection-color: {c["bg"]};
}}

/* ── Scrollbar ─────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {c["bg"]};
    width: 7px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c["border_l"]};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c["muted"]};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; }}
"""
