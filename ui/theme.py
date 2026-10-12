"""
ui/theme.py - Bang mau & QSS cho giao dien desktop chuyen nghiep, tham khao ban PC
cua 醒图 (Xingtu Pro, retouchpics.com) va CapCut Windows: nen den/gan den, diem nhan
mau xanh chanh neon (lime), the/card bo tron lon, anh that lam chu dao, cua so
frameless bo goc gan voi quy uoc Windows 11 (Mica/Acrylic, rounded corners).

Luu y: bang mau nay la lua chon thiet ke thu cong (built-in defaults, tong hop tu
quan sat truc tiep giao dien cong khai cua retouchpics.com va nguyen tac UX chuan -
khong phai ket qua tra ve tu co so du lieu cua cong cu tim kiem ui-ux-pro-max, cong
cu do khong co san (chi co tai lieu SKILL.md, khong co script/du lieu) trong moi
truong build nay)."""
import sys

COLORS = {
    "bg": "#0A0A0A",
    "bg_elevated": "#111111",
    "card": "#161616",
    "card_hover": "#1F1F1F",
    "card_active": "#272727",
    "border": "#262626",
    "border_strong": "#363636",
    "text": "#F5F5F0",
    "text_secondary": "#A3A39A",
    "text_muted": "#6B6B62",
    # Diem nhan chinh: xanh chanh neon (lime/chartreuse) tren nen gan den - lay truc
    # tiep tu quan sat giao dien cong khai cua retouchpics.com (nut CTA, vien active).
    "accent": "#C6FF4D",
    "accent_hover": "#D8FF7A",
    "accent_pressed": "#AEE639",
    "accent_soft": "#1B2008",
    "accent2": "#9FE62E",
    "on_accent": "#10140A",  # chu/icon tren nen accent (lime) - tuong phan ~15:1
    "success": "#4DFFC6",
    "warning": "#FFD24D",
    "danger": "#FF5C5C",
    "danger_soft": "#2A1414",
}

# Gradient 2 sac lime dung cho thanh truot/progress/checkbox (hoi sau hon o diem
# cuoi de co chieu sau nhe), khong dung cho nut chinh (nut chinh dung mau dac lime
# - giong nut CTA dang pill mau lime dac tren nen den cua retouchpics.com).
GRADIENT_PRIMARY = (
    "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
    f"stop:0 {COLORS['accent']}, stop:1 {COLORS['accent2']})"
)

# Uu tien font native cua Windows 11 (Segoe UI Variable), lui ve Segoe UI thuong
# tren Windows 10 hoac cac OS khac khi build/test ngoai Windows.
FONT_FAMILY = "'Segoe UI Variable Text', 'Segoe UI', 'Noto Sans', sans-serif"

MIN_TOUCH = 44  # px toi thieu cho vung cham (nguyen tac Touch & Interaction)

# Thang khoang cach & bo tron dung chung, theo luoi 4/8px de giao dien dong nhat.
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24

RADIUS_SM = 12
RADIUS_MD = 16
RADIUS_LG = 22
RADIUS_XL = 28
RADIUS_PILL = 999

TITLEBAR_HEIGHT = 44
NAV_RAIL_WIDTH = 88
WINDOW_CORNER_RADIUS = 12  # chi dung de ve khung ngoai cung (root container)


def apply_windows_dark_titlebar(window) -> None:
    """Bat dark-mode cho vien/titlebar goc cua Windows (qua DWM). Voi cua so frameless
    (xem apply_windows_native_chrome) titlebar goc da bi an nen goi nay chu yeu anh
    huong toi mau cua khung vien/bong do Windows ve xung quanh cua so. Khong lam gi
    tren cac OS khac hoac khi API khong co san - loi duoc bo qua hoan toan."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        hwnd = int(window.winId())
        value = ctypes.c_int(1)
        dwmapi = ctypes.windll.dwmapi
        # 20 = DWMWA_USE_IMMERSIVE_DARK_MODE (Windows 10 2004+/Windows 11),
        # 19 = gia tri cu tren cac build Windows 10 truoc do.
        for attr in (20, 19):
            dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
    except Exception:
        pass


def apply_windows_native_chrome(window) -> None:
    """Ap dung bo goc tron (DWMWA_WINDOW_CORNER_PREFERENCE) va vat lieu Mica
    (DWMWA_SYSTEMBACKDROP_TYPE) cho cua so - hai API chi co tu Windows 11, dung
    de cua so frameless cua app van "nhin" giong mot cua so native Windows 11
    (bo goc tron, chat lieu mo nen), giong CapCut/cac app UWP/WinUI3. Chi dung
    ctypes (co san trong Python chuan) - khong them dependency moi. Tren Windows
    10/Linux/macOS hoac khi API khong ton tai, ham nay khong lam gi va khong
    nem loi - cua so van hien thi binh thuong voi nen mau dac (QSS) thay cho Mica."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        hwnd = int(window.winId())
        dwmapi = ctypes.windll.dwmapi

        # DWMWA_WINDOW_CORNER_PREFERENCE = 33, DWMWCP_ROUND = 2
        corner_pref = ctypes.c_int(2)
        dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(corner_pref), ctypes.sizeof(corner_pref))

        # DWMWA_SYSTEMBACKDROP_TYPE = 38, DWMSBT_MAINWINDOW (Mica) = 2
        backdrop = ctypes.c_int(2)
        dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(backdrop), ctypes.sizeof(backdrop))
    except Exception:
        pass


QSS = f"""
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: {FONT_FAMILY};
    font-size: 14px;
    selection-background-color: {COLORS['accent']};
    selection-color: {COLORS['on_accent']};
}}

QMainWindow {{
    background-color: transparent;
}}

/* QLabel ke thua background-color dac tu luat QWidget o tren, tao thanh mot "mieng
   vuong" sau nhan chu khi dat trong Card (nen Card sang hon nen goc) - ghi de thanh
   trong suot de nhan chu hoa tan vao nen cha, dung kieu native. Cac QLabel muon tu
   co nen rieng (ChipAvatar, v.v.) dung selector theo object name, cu the hon nen
   van thang luat nay. */
QLabel {{
    background-color: transparent;
}}

/* RootContainer chi bo tron 2 goc tren (khop voi TitleBar o ngay tren no); 2 goc
   duoi duoc QStatusBar (nam duoi RootContainer, ngoai centralWidget cua
   QMainWindow) tu bo tron rieng, de toan bo cua so van nhin lien mach nhu mot
   khoi bo goc tron duy nhat du gom 2 widget khac nhau o cap QMainWindow. */
QWidget#RootContainer {{
    background-color: {COLORS['bg']};
    border-top-left-radius: {WINDOW_CORNER_RADIUS}px;
    border-top-right-radius: {WINDOW_CORNER_RADIUS}px;
}}
/* Khi cua so duoc phong to (Aero Snap/nut Maximize), bo goc tron bi tat (xem
   MainWindow.changeEvent) - khong co ly do bo tron o sat canh man hinh, va de
   tranh goc trong suot "khuyet" vao noi dung khi cua so phu kin man hinh. */
QWidget#RootContainer[maximized="true"] {{
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}}
QFrame#TitleBar[maximized="true"] {{
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}}
QStatusBar[maximized="true"] {{
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
}}

QToolTip {{
    background-color: {COLORS['card_active']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: {RADIUS_SM}px;
    padding: 6px 10px;
}}

/* ---- Thanh tieu de tuy bien (frameless, thay titlebar goc cua Windows) ---- */
QFrame#TitleBar {{
    background-color: {COLORS['bg_elevated']};
    border-top-left-radius: {WINDOW_CORNER_RADIUS}px;
    border-top-right-radius: {WINDOW_CORNER_RADIUS}px;
    border-bottom: 1px solid {COLORS['border']};
}}
QLabel#TitleBarApp {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}}
QLabel#TitleBarIcon {{
    color: {COLORS['accent']};
    font-size: 15px;
}}
QPushButton#WinCaptionButton, QPushButton#WinCloseButton {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    min-width: 46px;
    max-width: 46px;
    min-height: {TITLEBAR_HEIGHT}px;
    max-height: {TITLEBAR_HEIGHT}px;
    font-size: 14px;
}}
QPushButton#WinCaptionButton:hover {{
    background-color: {COLORS['card_hover']};
    color: {COLORS['text']};
}}
QPushButton#WinCloseButton:hover {{
    background-color: #E81123;
    color: white;
    border-top-right-radius: {WINDOW_CORNER_RADIUS}px;
}}

/* ---- Thanh dieu huong doc ben trai (nav rail, kieu app desktop native thay cho
   bottom-nav di dong) - vach chi bao truot mau lime theo chieu doc ---- */
QFrame#NavRail {{
    background-color: {COLORS['bg_elevated']};
    border-right: 1px solid {COLORS['border']};
}}

QFrame#NavIndicator {{
    background-color: {COLORS['accent_soft']};
    border-radius: {RADIUS_MD}px;
}}

QPushButton#NavButton {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    border-radius: {RADIUS_MD}px;
    padding: 6px 4px;
    font-size: 11px;
    font-weight: 600;
    min-height: 64px;
}}
QPushButton#NavButton:checked {{
    color: {COLORS['accent']};
}}
QPushButton#NavButton:hover {{
    color: {COLORS['text']};
}}
QPushButton#NavButton:focus {{
    outline: none;
    border: 1px solid {COLORS['accent']};
}}

/* ---- Nut chinh (mau lime dac, chu den - kieu nut CTA cua retouchpics.com) ---- */
QPushButton#PrimaryButton {{
    background-color: {COLORS['accent']};
    color: {COLORS['on_accent']};
    border: none;
    border-radius: {RADIUS_PILL}px;
    padding: 14px 22px;
    font-size: 15px;
    font-weight: 700;
    min-height: {MIN_TOUCH}px;
}}
QPushButton#PrimaryButton:hover {{ background-color: {COLORS['accent_hover']}; }}
QPushButton#PrimaryButton:pressed {{ background-color: {COLORS['accent_pressed']}; }}
QPushButton#PrimaryButton:disabled {{ background-color: {COLORS['border']}; color: {COLORS['text_muted']}; }}
QPushButton#PrimaryButton:focus {{ outline: none; border: 2px solid white; }}

QPushButton#SecondaryButton {{
    background-color: {COLORS['card']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: {RADIUS_PILL}px;
    padding: 12px 18px;
    font-size: 14px;
    font-weight: 600;
    min-height: {MIN_TOUCH}px;
}}
QPushButton#SecondaryButton:hover {{ background-color: {COLORS['card_hover']}; border-color: {COLORS['border_strong']}; }}
QPushButton#SecondaryButton:pressed {{ background-color: {COLORS['card_active']}; }}
QPushButton#SecondaryButton:disabled {{ color: {COLORS['text_muted']}; border-color: {COLORS['border']}; }}
QPushButton#SecondaryButton:focus {{ outline: none; border: 1px solid {COLORS['accent']}; }}

QPushButton#IconButton {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: {RADIUS_XL}px;
    min-width: {MIN_TOUCH}px;
    min-height: {MIN_TOUCH}px;
    font-size: 18px;
}}
QPushButton#IconButton:hover {{ background-color: {COLORS['card_hover']}; }}
QPushButton#IconButton:pressed {{ background-color: {COLORS['card_active']}; }}

/* ---- The/Card (khung nhom noi dung, bo tron lon kieu bang dieu khien desktop) ---- */
QFrame#Card {{
    background-color: {COLORS['card']};
    border-radius: {RADIUS_LG}px;
    border: 1px solid {COLORS['border']};
}}
QFrame#CanvasCard {{
    background-color: {COLORS['card']};
    border-radius: {RADIUS_XL}px;
    border: 1px solid {COLORS['border']};
}}

/* ---- Tieu de ---- */
QLabel#SectionTitle {{
    font-size: 20px;
    font-weight: 700;
    color: {COLORS['text']};
}}
QLabel#CardTitle {{
    font-size: 12px;
    font-weight: 700;
    color: {COLORS['accent']};
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}
QLabel#Caption {{
    font-size: 13px;
    color: {COLORS['text_secondary']};
}}
QLabel#FieldLabel {{
    font-size: 13px;
    font-weight: 600;
    color: {COLORS['text']};
}}
QLabel#FieldHint {{
    font-size: 12px;
    color: {COLORS['text_muted']};
}}

/* ---- Style chip / preset card (carousel chon phong cach) ---- */
QPushButton#StyleChip {{
    background-color: {COLORS['card']};
    border: 2px solid {COLORS['border']};
    border-radius: {RADIUS_LG}px;
}}
QPushButton#StyleChip:checked {{
    border-color: {COLORS['accent']};
    background-color: {COLORS['accent_soft']};
}}
QPushButton#StyleChip:hover {{ background-color: {COLORS['card_hover']}; }}
QPushButton#StyleChip:focus {{ outline: none; border-color: {COLORS['accent']}; }}

QLabel#ChipAvatar {{
    background-color: {COLORS['card_hover']};
    border-radius: 22px;
    font-size: 20px;
}}
QLabel#ChipAvatar[selected="true"] {{
    background-color: {COLORS['accent']};
}}
QLabel#ChipLabel {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#StyleChip:checked QLabel#ChipLabel {{
    color: {COLORS['text']};
}}

/* ---- Luoi anh trong Thu vien ---- */
QListWidget#PhotoGrid {{
    background-color: transparent;
    border: none;
}}
QListWidget#PhotoGrid::item {{
    border-radius: {RADIUS_MD}px;
    padding: 4px;
}}
QListWidget#PhotoGrid::item:hover {{
    background-color: {COLORS['card_hover']};
}}
QListWidget#PhotoGrid::item:selected {{
    background-color: {COLORS['accent_soft']};
    border: 2px solid {COLORS['accent']};
}}

/* ---- Slider (vung cham lon cho handle, mau lime khi da keo) ---- */
QSlider::groove:horizontal {{
    height: 6px;
    background: {COLORS['border']};
    border-radius: 3px;
}}
QSlider::sub-page:horizontal {{
    background: {GRADIENT_PRIMARY};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {COLORS['text']};
    border: 3px solid {COLORS['accent']};
    width: 22px;
    height: 22px;
    margin: -9px 0;
    border-radius: 11px;
}}
QSlider::handle:horizontal:hover {{ border-color: {COLORS['accent_hover']}; }}

/* ---- Input ---- */
QLineEdit, QTextEdit, QComboBox {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: {RADIUS_MD}px;
    padding: 10px 14px;
    min-height: {MIN_TOUCH}px;
    font-size: 14px;
    color: {COLORS['text']};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border-color: {COLORS['accent']};
}}
QLineEdit:disabled, QComboBox:disabled {{
    color: {COLORS['text_muted']};
    background-color: {COLORS['bg_elevated']};
}}

QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['card']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: {RADIUS_SM}px;
    selection-background-color: {COLORS['accent_soft']};
    selection-color: {COLORS['text']};
    padding: 4px;
}}

QListWidget {{
    background-color: transparent;
    border: none;
}}
QListWidget::item {{
    border-radius: {RADIUS_MD}px;
    padding: 4px;
}}
QListWidget::item:selected {{
    background-color: {COLORS['accent_soft']};
}}

/* ---- Menu ngu canh (chuot phai xoa preset, v.v.) ---- */
QMenu {{
    background-color: {COLORS['card_active']};
    border: 1px solid {COLORS['border_strong']};
    border-radius: {RADIUS_MD}px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 20px;
    border-radius: {RADIUS_SM}px;
    color: {COLORS['text']};
}}
QMenu::item:selected {{
    background-color: {COLORS['accent_soft']};
    color: {COLORS['text']};
}}
QMenu::separator {{
    height: 1px;
    background: {COLORS['border']};
    margin: 4px 8px;
}}

/* ---- Thanh/ho thoai tien trinh (xu ly hang loat, tai ban cap nhat) ---- */
QProgressBar {{
    background-color: {COLORS['border']};
    border: none;
    border-radius: {RADIUS_SM}px;
    min-height: 10px;
    text-align: center;
    color: {COLORS['text']};
    font-size: 11px;
}}
QProgressBar::chunk {{
    background: {GRADIENT_PRIMARY};
    border-radius: {RADIUS_SM}px;
}}
QProgressDialog {{
    background-color: {COLORS['bg_elevated']};
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: transparent;
    width: 8px;
    height: 8px;
}}
QScrollBar::handle {{
    background: {COLORS['border_strong']};
    border-radius: 4px;
    min-height: 24px;
    min-width: 24px;
}}
QScrollBar::handle:hover {{ background: {COLORS['text_muted']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0; width: 0;
}}

QCheckBox {{
    spacing: 10px;
    font-size: 14px;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 2px solid {COLORS['border_strong']};
    background: {COLORS['card']};
}}
QCheckBox::indicator:checked {{
    background: {GRADIENT_PRIMARY};
    border-color: transparent;
}}
QCheckBox::indicator:hover {{ border-color: {COLORS['accent']}; }}

QStatusBar {{
    background-color: {COLORS['bg_elevated']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border']};
    border-bottom-left-radius: {WINDOW_CORNER_RADIUS}px;
    border-bottom-right-radius: {WINDOW_CORNER_RADIUS}px;
}}

QMessageBox, QInputDialog, QFileDialog {{
    background-color: {COLORS['bg_elevated']};
}}
"""
