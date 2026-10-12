"""
ui/widgets.py - Cac widget tai su dung: thanh dieu huong duoi, chip chon phong cach,
thanh keo so sanh truoc/sau (compare slider).
"""
from typing import Optional

from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QButtonGroup
)

from ui.theme import COLORS, MIN_TOUCH
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


class BottomNavBar(QFrame):
    """Thanh dieu huong duoi man hinh, toi uu cho cam ung (giong app di dong)."""

    tabChanged = Signal(str)

    def __init__(self, items: list[NavItem], parent=None):
        super().__init__(parent)
        self.setObjectName("BottomNav")
        self.setFixedHeight(72)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self._items = items
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        for item in items:
            btn = QPushButton(f"{item.icon_text}\n{t(item.label_key)}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(MIN_TOUCH)
            btn.clicked.connect(lambda _checked, k=item.key: self.tabChanged.emit(k))
            self._group.addButton(btn)
            self._buttons[item.key] = btn
            layout.addWidget(btn)

        if items:
            self._buttons[items[0].key].setChecked(True)

    def set_active(self, key: str):
        if key in self._buttons:
            self._buttons[key].setChecked(True)

    def retranslate(self):
        for item in self._items:
            btn = self._buttons.get(item.key)
            if btn is not None:
                btn.setText(f"{item.icon_text}\n{t(item.label_key)}")


class StyleChip(QPushButton):
    """Mot 'chip' tron chon phong cach AI, dung trong carousel ngang."""

    def __init__(self, key: str, label: str, emoji: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.emoji = emoji
        self.setObjectName("StyleChip")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText(f"{emoji}\n{label}")

    def set_label(self, label: str):
        self.setText(f"{self.emoji}\n{label}")


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
