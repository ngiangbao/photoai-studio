"""
ui/widgets.py - Cac widget tai su dung: thanh dieu huong doc ben trai (nav rail kieu
desktop native, co nen highlight truot muot), thanh tieu de tuy bien (titlebar) cho
cua so frameless, the/chip chon phong cach kieu luoi hieu ung (avatar + nhan), cong
tac bat/tat dang pill truot, va thanh keo so sanh truoc/sau (compare slider).
"""
from typing import Optional

from PIL.ImageQt import ImageQt
from PySide6.QtCore import (
    Qt, QRect, QRectF, QPoint, Signal, Property, QPropertyAnimation, QEasingCurve,
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QButtonGroup, QSizePolicy
)

from ui.theme import COLORS, MIN_TOUCH, NAV_RAIL_WIDTH, TITLEBAR_HEIGHT
from i18n import t


def pil_to_pixmap(pil_image) -> QPixmap:
    """Chuyen PIL.Image sang QPixmap."""
    rgb_image = pil_image.convert("RGB")
    return QPixmap.fromImage(ImageQt(rgb_image))


class NavItem:
    def __init__(self, key: str, label_key: str, icon_text: str):
        self.key = key
        self.label_key = label_key  # khoa i18n, de retranslate khi doi ngon ngu
        self.icon_text = icon_text


class NavRail(QFrame):
    """Thanh dieu huong doc, dat co dinh ben trai cua so - kieu "nav rail" cua cac
    app desktop native (CapCut Windows, Photos/Settings cua Windows 11) thay cho
    bottom-nav kieu app di dong. Nen highlight (pill bo tron, mau lime nhat) truot
    muot bang animation phia sau nut dang chon khi doi tab."""

    tabChanged = Signal(str)

    def __init__(self, items: list[NavItem], parent=None):
        super().__init__(parent)
        self.setObjectName("NavRail")
        self.setFixedWidth(NAV_RAIL_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 16, 10, 16)
        layout.setSpacing(8)

        self._items = items
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}
        self._active_key = items[0].key if items else ""

        for item in items:
            btn = QPushButton(f"{item.icon_text}\n{t(item.label_key)}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(68)
            btn.clicked.connect(lambda _checked, k=item.key: self._on_clicked(k))
            self._group.addButton(btn)
            self._buttons[item.key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        if items:
            self._buttons[items[0].key].setChecked(True)

        # Nen highlight truot: phu kin nut dang chon (khong phai mot vach mong), di
        # chuyen theo truc doc bang QPropertyAnimation. Khong them vao layout - dinh
        # vi thu cong qua setGeometry() trong resizeEvent/showEvent de luon bam dung
        # vi tri nut, va luon nam duoi (lower) de khong che chu/icon cua nut.
        self.indicator = QFrame(self)
        self.indicator.setObjectName("NavIndicator")
        self.indicator.lower()
        self._indicator_anim = QPropertyAnimation(self.indicator, b"geometry", self)
        self._indicator_anim.setDuration(220)
        self._indicator_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _indicator_target_rect(self, key: str) -> QRect:
        btn = self._buttons.get(key)
        if btn is None or btn.width() <= 0:
            return QRect(0, 0, 0, 0)
        return QRect(btn.x(), btn.y(), btn.width(), btn.height())

    def _move_indicator_to(self, key: str, animate: bool = True):
        target = self._indicator_target_rect(key)
        if target.width() == 0:
            return
        if animate and self.indicator.geometry().width() > 0:
            self._indicator_anim.stop()
            self._indicator_anim.setStartValue(self.indicator.geometry())
            self._indicator_anim.setEndValue(target)
            self._indicator_anim.start()
        else:
            self.indicator.setGeometry(target)
        self._active_key = key

    def _on_clicked(self, key: str):
        self._move_indicator_to(key)
        self.tabChanged.emit(key)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._move_indicator_to(self._active_key, animate=False)

    def showEvent(self, event):
        super().showEvent(event)
        self._move_indicator_to(self._active_key, animate=False)

    def set_active(self, key: str):
        if key in self._buttons:
            self._buttons[key].setChecked(True)
            self._move_indicator_to(key)

    def retranslate(self):
        for item in self._items:
            btn = self._buttons.get(item.key)
            if btn is not None:
                btn.setText(f"{item.icon_text}\n{t(item.label_key)}")


class TitleBar(QFrame):
    """Thanh tieu de tuy bien thay cho titlebar goc cua Windows (cua so chay o che
    do frameless de co the bo goc tron + vat lieu Mica kieu Windows 11/CapCut). Keo
    de di chuyen va nut thu nho/phong to/dong dung QWindow.startSystemMove() va
    startSystemResize() cua Qt6 - de he dieu hanh tu xu ly viec keo/tha, nho do van
    co duoc Aero Snap (keo len dau man hinh de phong to, keo sang canh de chia doi
    man hinh) giong mot cua so native that su, khong phai tu mo phong lai."""

    minimizeRequested = Signal()
    maximizeRequested = Signal()
    closeRequested = Signal()

    def __init__(self, app_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(TITLEBAR_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 0, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel("◆")
        self.icon_label.setObjectName("TitleBarIcon")
        layout.addWidget(self.icon_label)

        self.title_label = QLabel(app_name)
        self.title_label.setObjectName("TitleBarApp")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("WinCaptionButton")
        self.min_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self.min_btn.setToolTip(t("titlebar.minimize"))
        self.min_btn.setAccessibleName(t("titlebar.minimize"))
        self.min_btn.clicked.connect(self.minimizeRequested.emit)
        layout.addWidget(self.min_btn)

        self.max_btn = QPushButton("▢")
        self.max_btn.setObjectName("WinCaptionButton")
        self.max_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self.max_btn.setToolTip(t("titlebar.maximize"))
        self.max_btn.setAccessibleName(t("titlebar.maximize"))
        self.max_btn.clicked.connect(self.maximizeRequested.emit)
        layout.addWidget(self.max_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("WinCloseButton")
        self.close_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self.close_btn.setToolTip(t("titlebar.close"))
        self.close_btn.setAccessibleName(t("titlebar.close"))
        self.close_btn.clicked.connect(self.closeRequested.emit)
        layout.addWidget(self.close_btn)

        self._drag_pos: Optional[QPoint] = None

    def set_app_name(self, name: str):
        self.title_label.setText(name)

    def retranslate(self):
        self.min_btn.setToolTip(t("titlebar.minimize"))
        self.min_btn.setAccessibleName(t("titlebar.minimize"))
        self.max_btn.setToolTip(t("titlebar.maximize"))
        self.max_btn.setAccessibleName(t("titlebar.maximize"))
        self.close_btn.setToolTip(t("titlebar.close"))
        self.close_btn.setAccessibleName(t("titlebar.close"))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            handle = window.windowHandle() if window is not None else None
            if handle is not None:
                handle.startSystemMove()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.maximizeRequested.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class StyleChip(QPushButton):
    """Mot 'the' (card) chon phong cach AI dang luoi hieu ung, dung trong carousel
    ngang: vong tron avatar (emoji) phia tren + nhan phia duoi, vien/nen doi mau khi
    duoc chon - kieu luoi hieu ung cua CapCut va bo loc cua Xingtu."""

    def __init__(self, key: str, label: str, emoji: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.emoji = emoji
        self.setObjectName("StyleChip")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(100, 112)

        inner = QVBoxLayout(self)
        inner.setContentsMargins(8, 12, 8, 10)
        inner.setSpacing(8)
        inner.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._avatar = QLabel(emoji)
        self._avatar.setObjectName("ChipAvatar")
        self._avatar.setFixedSize(44, 44)
        self._avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner.addWidget(self._avatar, 0, Qt.AlignmentFlag.AlignHCenter)

        self._label = QLabel(label)
        self._label.setObjectName("ChipLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setWordWrap(True)
        inner.addWidget(self._label)

        self.toggled.connect(self._update_avatar_state)

    def _update_avatar_state(self, checked: bool):
        self._avatar.setProperty("selected", checked)
        self._avatar.style().unpolish(self._avatar)
        self._avatar.style().polish(self._avatar)

    def set_label(self, label: str):
        self._label.setText(label)

    def label_text(self) -> str:
        return self._label.text()


class ToggleSwitch(QWidget):
    """Cong tac bat/tat dang 'pill' truot (giong toggle cua app di dong/Windows 11),
    thay the QCheckBox don dieu cho cac tuy chon quan trong trong Cai dat. Co animation
    muot khi bam, ho tro ban phim (Space/Enter) va vong focus de dam bao accessibility."""

    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(52, 30)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._checked = False
        self._knob_pos = 3.0

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool, animate: bool = False):
        checked = bool(checked)
        self._checked = checked
        target = float(self.width() - (self.height() - 6) - 3) if checked else 3.0
        if animate and self.isVisible():
            anim = QPropertyAnimation(self, b"knobPos", self)
            anim.setDuration(160)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setStartValue(self._knob_pos)
            anim.setEndValue(target)
            anim.start()
            self._anim = anim  # giu tham chieu de khong bi garbage-collect giua chung
        else:
            self._knob_pos = target
            self.update()

    def _get_knob_pos(self):
        return self._knob_pos

    def _set_knob_pos(self, value):
        self._knob_pos = value
        self.update()

    knobPos = Property(float, _get_knob_pos, _set_knob_pos)

    def _toggle(self):
        self.setChecked(not self._checked, animate=True)
        self.toggled.emit(self._checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._toggle()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track_rect = QRectF(0, 0, self.width(), self.height()).adjusted(0, 0, -1, -1)
        radius = track_rect.height() / 2

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLORS["accent"] if self._checked else COLORS["border_strong"]))
        painter.drawRoundedRect(track_rect, radius, radius)

        knob_d = track_rect.height() - 6
        knob_y = (track_rect.height() - knob_d) / 2
        painter.setBrush(QColor("white"))
        painter.drawEllipse(QRectF(self._knob_pos, knob_y, knob_d, knob_d))

        if self.hasFocus():
            pen = QPen(QColor(COLORS["accent"]))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(track_rect.adjusted(1, 1, -1, -1), radius, radius)

        painter.end()


class CompareSlider(QWidget):
    """Widget keo de so sanh anh truoc/sau, giong tinh nang cua cac app chinh anh di dong.
    Ho tro ca chuot va cham (Qt tu dong chuyen touch -> mouse event tren Windows)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setMinimumSize(300, 300)
        self._before: Optional[QPixmap] = None
        self._after: Optional[QPixmap] = None
        self._divider = 0.5  # 0..1
        self._dragging = False

    def set_images(self, before: Optional[QPixmap], after: Optional[QPixmap]):
        self._before = before
        self._after = after
        self._divider = 0.5
        self.update()

    def _scaled(self, pixmap: QPixmap) -> QPixmap:
        return pixmap.scaled(
            self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        painter.fillRect(rect, QColor(COLORS["card"]))

        if self._before is None:
            painter.setPen(QColor(COLORS["text_muted"]))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, t("compare.no_image"))
            painter.end()
            return

        before_scaled = self._scaled(self._before)
        x_off = (rect.width() - before_scaled.width()) // 2
        y_off = (rect.height() - before_scaled.height()) // 2
        painter.drawPixmap(x_off, y_off, before_scaled)

        if self._after is not None:
            after_scaled = self._scaled(self._after)
            divider_x = int(rect.width() * self._divider)
            clip = QRect(0, 0, divider_x, rect.height())
            painter.setClipRect(clip)
            ax_off = (rect.width() - after_scaled.width()) // 2
            ay_off = (rect.height() - after_scaled.height()) // 2
            painter.drawPixmap(ax_off, ay_off, after_scaled)
            painter.setClipping(False)

            pen = QPen(QColor("white"))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(divider_x, 0, divider_x, rect.height())

            painter.setBrush(QColor(COLORS["accent"]))
            painter.setPen(QPen(QColor("white"), 2))
            handle_y = rect.height() // 2
            painter.drawEllipse(divider_x - 16, handle_y - 16, 32, 32)

            painter.setPen(QColor("white"))
            painter.drawText(QRect(8, 8, 60, 24), Qt.AlignmentFlag.AlignLeft, t("compare.after_label"))
            painter.drawText(QRect(rect.width() - 68, 8, 60, 24), Qt.AlignmentFlag.AlignRight, t("compare.before_label"))

        painter.end()

    def _update_divider_from_x(self, x: int):
        self._divider = max(0.0, min(1.0, x / max(1, self.width())))
        self.update()

    def mousePressEvent(self, event):
        if self._after is not None:
            self._dragging = True
            self._update_divider_from_x(event.position().x())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_divider_from_x(event.position().x())

    def mouseReleaseEvent(self, event):
        self._dragging = False
