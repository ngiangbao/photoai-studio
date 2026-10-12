"""
ui/theme.py - Bang mau & QSS cho giao diện kieu app chinh anh di dong (Xingtu-style):
nen toi, diem nhan hong/tim ruc ro, vung cham lon.

Luu y: bang mau nay la lua chon mac dinh thu cong (built-in defaults), khong phai
ket qua tra ve tu cong cu tim kiem cua ui-ux-pro-max (cong cu do khong co san trong
moi truong build nay).
"""

COLORS = {
    "bg": "#121214",
    "bg_elevated": "#1C1C20",
    "card": "#222226",
    "card_hover": "#2A2A30",
    "border": "#323238",
    "text": "#F5F5F7",
    "text_secondary": "#9A9AA4",
    "text_muted": "#6E6E78",
    "accent": "#FF4D8D",
    "accent_hover": "#FF6AA0",
    "accent_pressed": "#E63D79",
    "accent_soft": "#3A1F2B",
    "accent2": "#7C5CFF",
    "success": "#3DD68C",
    "danger": "#FF5C5C",
}

FONT_FAMILY = "Segoe UI"

MIN_TOUCH = 44  # px toi thieu cho vung cham (nguyen tac Touch & Interaction)

QSS = f"""
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: '{FONT_FAMILY}';
    font-size: 15px;
}}

QMainWindow {{
    background-color: {COLORS['bg']};
}}

/* ---- Thanh dieu huong duoi (bottom nav) ---- */
QFrame#BottomNav {{
    background-color: {COLORS['bg_elevated']};
    border-top: 1px solid {COLORS['border']};
}}

QPushButton#NavButton {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-radius: 12px;
    padding: 8px 4px;
    font-size: 13px;
    min-height: 56px;
}}
QPushButton#NavButton:checked {{
    color: {COLORS['accent']};
    background-color: {COLORS['accent_soft']};
}}
QPushButton#NavButton:hover {{
    color: {COLORS['text']};
}}

/* ---- Nut chinh (accent, to, bo tron) ---- */
QPushButton#PrimaryButton {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 16px;
    padding: 14px 20px;
    font-size: 16px;
    font-weight: 600;
    min-height: {MIN_TOUCH}px;
}}
QPushButton#PrimaryButton:hover {{ background-color: {COLORS['accent_hover']}; }}
QPushButton#PrimaryButton:pressed {{ background-color: {COLORS['accent_pressed']}; }}
QPushButton#PrimaryButton:disabled {{ background-color: {COLORS['border']}; color: {COLORS['text_muted']}; }}

QPushButton#SecondaryButton {{
    background-color: {COLORS['card']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
    padding: 12px 18px;
    font-size: 15px;
    min-height: {MIN_TOUCH}px;
}}
QPushButton#SecondaryButton:hover {{ background-color: {COLORS['card_hover']}; }}
QPushButton#SecondaryButton:disabled {{ color: {COLORS['text_muted']}; }}

QPushButton#IconButton {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 22px;
    min-width: {MIN_TOUCH}px;
    min-height: {MIN_TOUCH}px;
    font-size: 18px;
}}
QPushButton#IconButton:hover {{ background-color: {COLORS['card_hover']}; }}

/* ---- The/Card ---- */
QFrame#Card {{
    background-color: {COLORS['card']};
    border-radius: 18px;
    border: 1px solid {COLORS['border']};
}}

/* ---- Tieu de section ---- */
QLabel#SectionTitle {{
    font-size: 18px;
    font-weight: 700;
    color: {COLORS['text']};
}}
QLabel#Caption {{
    font-size: 13px;
    color: {COLORS['text_secondary']};
}}

/* ---- Style chip (carousel chon phong cach) ---- */
QPushButton#StyleChip {{
    background-color: {COLORS['card']};
    border: 2px solid {COLORS['border']};
    border-radius: 18px;
    color: {COLORS['text_secondary']};
    font-size: 14px;
    font-weight: 600;
    padding: 10px;
    min-width: 92px;
    min-height: 92px;
}}
QPushButton#StyleChip:checked {{
    border-color: {COLORS['accent']};
    color: {COLORS['accent']};
    background-color: {COLORS['accent_soft']};
}}
QPushButton#StyleChip:hover {{ background-color: {COLORS['card_hover']}; }}

/* ---- Slider (vung cham lon cho handle) ---- */
QSlider::groove:horizontal {{
    height: 6px;
    background: {COLORS['border']};
    border-radius: 3px;
}}
QSlider::sub-page:horizontal {{
    background: {COLORS['accent']};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: white;
    border: 3px solid {COLORS['accent']};
    width: 26px;
    height: 26px;
    margin: -11px 0;
    border-radius: 13px;
}}

/* ---- Input ---- */
QLineEdit, QTextEdit, QComboBox {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 10px 14px;
    min-height: {MIN_TOUCH}px;
    font-size: 15px;
    color: {COLORS['text']};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border-color: {COLORS['accent']};
}}

QListWidget {{
    background-color: transparent;
    border: none;
}}
QListWidget::item {{
    border-radius: 16px;
    padding: 4px;
}}
QListWidget::item:selected {{
    background-color: {COLORS['accent_soft']};
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: transparent;
    width: 8px;
    height: 8px;
}}
QScrollBar::handle {{
    background: {COLORS['border']};
    border-radius: 4px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0; width: 0;
}}

QStatusBar {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_secondary']};
}}
"""
