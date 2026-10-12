"""
ui/pages.py - 4 trang chinh cua ung dung: Thu vien, Chinh AI, Chinh tay, Cai dat.
Giao dien to chuc theo tung 'the' (card) bo tron de nhom noi dung, tham khao bang
dieu khien cua CapCut va bo loc/preset cua 醒图 (Xingtu/retouchpics.com).
"""
from pathlib import Path
from typing import Optional

from PIL import Image
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QScrollArea, QFrame, QSlider, QLineEdit,
    QFormLayout, QFileDialog, QTextEdit, QComboBox, QAbstractItemView, QMenu
)

from ai.styles import STYLES
from ai.manual_edit import ManualAdjustments
from ui.widgets import StyleChip, CompareSlider, ToggleSwitch, pil_to_pixmap
from i18n import t, get_language, set_language, SUPPORTED_LANGUAGES, LANGUAGE_NAMES

THUMB_SIZE = QSize(190, 190)

# Chieu rong co dinh cho cot dieu khien ben phai trong bo cuc 2 cot (canvas lon ben
# trai + bang dieu khien ben phai) kieu app chinh anh desktop chuyen nghiep (tham
# khao ban PC cua 醒图/Xingtu Pro - retouchpics.com - va CapCut Windows), dung chung
# cho trang Chinh AI va Chinh tay de giao dien dong nhat khi chuyen qua lai.
CONTROL_PANEL_WIDTH = 360

STYLE_EMOJI = {
    "portrait": "🧑",
    "outdoor": "🌳",
    "landscape": "🏞️",
    "people": "👥",
    "graduation": "🎓",
    "cleanup": "🧹",
}


def section_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("SectionTitle")
    return label


def caption(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Caption")
    label.setWordWrap(True)
    return label


def make_card(title_label: Optional[QLabel] = None) -> tuple[QFrame, QVBoxLayout]:
    """Tao mot khung 'Card' bo tron de nhom noi dung (giong bang dieu khien cua
    CapCut/Xingtu). title_label (tuy chon) la mot QLabel da tao san (vd mot caption
    co san duoc tai su dung) - se duoc gan lai object name 'CardTitle' va dat len
    dau card, de khong can them khoa dich moi cho tieu de."""
    frame = QFrame()
    frame.setObjectName("Card")
    inner = QVBoxLayout(frame)
    inner.setContentsMargins(16, 14, 16, 16)
    inner.setSpacing(10)
    if title_label is not None:
        title_label.setObjectName("CardTitle")
        inner.addWidget(title_label)
    return frame, inner


def make_canvas_card() -> tuple[QFrame, QVBoxLayout]:
    """Tao khung 'CanvasCard' - the lon bo goc rong hon dung lam vung xem anh chinh
    (ben trai trong bo cuc 2 cot), tham khao khung anh lon bo goc cua retouchpics.com
    ban PC va vung preview cua CapCut Windows."""
    frame = QFrame()
    frame.setObjectName("CanvasCard")
    inner = QVBoxLayout(frame)
    inner.setContentsMargins(14, 14, 14, 14)
    inner.setSpacing(10)
    return frame, inner


def make_control_panel() -> tuple[QScrollArea, QVBoxLayout]:
    """Tao cot dieu khien ben phai (scroll doc, chieu rong co dinh) dung chung cho
    cac trang co bo cuc 2 cot (Chinh AI, Chinh tay)."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setFixedWidth(CONTROL_PANEL_WIDTH)

    inner = QWidget()
    layout = QVBoxLayout(inner)
    layout.setContentsMargins(0, 0, 4, 0)
    layout.setSpacing(12)
    scroll.setWidget(inner)
    return scroll, layout


# ---------------------------------------------------------------------------
# 1. Trang Thu vien
# ---------------------------------------------------------------------------
class LibraryPage(QWidget):
    captureRequested = Signal()
    photoSelected = Signal(str)
    batchRequested = Signal(list)  # danh sach duong dan anh da chon

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        self.title_label = section_title(t("library.title"))
        header.addWidget(self.title_label)
        header.addStretch()
        self.capture_btn = QPushButton(t("library.capture_button"))
        self.capture_btn.setObjectName("PrimaryButton")
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.clicked.connect(self.captureRequested.emit)
        header.addWidget(self.capture_btn)
        layout.addLayout(header)

        selection_row = QHBoxLayout()
        selection_row.setSpacing(8)
        self.multi_select_btn = QPushButton(t("library.multi_select_button"))
        self.multi_select_btn.setObjectName("SecondaryButton")
        self.multi_select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.multi_select_btn.setCheckable(True)
        self.multi_select_btn.toggled.connect(self._on_multi_select_toggled)
        selection_row.addWidget(self.multi_select_btn)
        selection_row.addStretch()

        self.batch_btn = QPushButton()
        self.batch_btn.setObjectName("PrimaryButton")
        self.batch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.batch_btn.setEnabled(False)
        self.batch_btn.setVisible(False)
        self.batch_btn.clicked.connect(self._emit_batch)
        selection_row.addWidget(self.batch_btn)
        layout.addLayout(selection_row)

        self.photo_list = QListWidget()
        self.photo_list.setObjectName("PhotoGrid")
        self.photo_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.photo_list.setIconSize(THUMB_SIZE)
        self.photo_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.photo_list.setSpacing(10)
        self.photo_list.setMovement(QListWidget.Movement.Static)
        self.photo_list.itemClicked.connect(self._on_item_clicked)
        self.photo_list.itemSelectionChanged.connect(self._update_batch_button)
        layout.addWidget(self.photo_list)

        self.empty_hint = caption(t("library.empty_hint"))
        layout.addWidget(self.empty_hint)
        self._update_batch_button()

    def refresh(self, folder: str):
        path = Path(folder)
        existing = {
            self.photo_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.photo_list.count())
        }
        files = sorted(
            list(path.glob("*.jpg")) + list(path.glob("*.jpeg")) + list(path.glob("*.png")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for p in files:
            if str(p) in existing:
                continue
            icon = QIcon(QPixmap(str(p)).scaled(
                THUMB_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
            item = QListWidgetItem(icon, p.name)
            item.setData(Qt.ItemDataRole.UserRole, str(p))
            self.photo_list.insertItem(0, item)
        self.empty_hint.setVisible(self.photo_list.count() == 0)

    def _on_multi_select_toggled(self, checked: bool):
        if checked:
            self.photo_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        else:
            self.photo_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.photo_list.clearSelection()
        self.batch_btn.setVisible(checked)
        self._update_batch_button()

    def _on_item_clicked(self, item: QListWidgetItem):
        if self.multi_select_btn.isChecked():
            self._update_batch_button()
            return
        self.photoSelected.emit(item.data(Qt.ItemDataRole.UserRole))

    def _update_batch_button(self):
        count = len(self.photo_list.selectedItems())
        self.batch_btn.setEnabled(count > 0)
        self.batch_btn.setText(t("library.batch_button", count=count))

    def _emit_batch(self):
        paths = [item.data(Qt.ItemDataRole.UserRole) for item in self.photo_list.selectedItems()]
        if paths:
            self.batchRequested.emit(paths)

    def retranslate(self):
        self.title_label.setText(t("library.title"))
        self.capture_btn.setText(t("library.capture_button"))
        self.empty_hint.setText(t("library.empty_hint"))
        self.multi_select_btn.setText(t("library.multi_select_button"))
        self._update_batch_button()


# ---------------------------------------------------------------------------
# 2. Trang Chinh sua AI
# ---------------------------------------------------------------------------
class AIEditPage(QWidget):
    processRequested = Signal(str, float, str)  # style_key, intensity(0..1), extra_note
    presetSaveRequested = Signal()
    presetDeleteRequested = Signal(int)  # chi so preset trong danh sach custom_presets

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(14)

        self.title_label = section_title(t("ai.title"))
        outer.addWidget(self.title_label)

        # Bo cuc 2 cot kieu app chinh anh desktop chuyen nghiep: canvas lon ben trai
        # (anh xem truoc + thanh keo so sanh truoc/sau) + bang dieu khien co chieu
        # rong co dinh ben phai (carousel phong cach, cuong do, ghi chu, hanh dong) -
        # tham khao bo cuc ban PC cua 醒图/Xingtu Pro (retouchpics.com) va CapCut Windows.
        split = QHBoxLayout()
        split.setSpacing(16)
        outer.addLayout(split, stretch=1)

        # ---- Cot trai: canvas xem truoc + thanh keo so sanh truoc/sau ----
        canvas_card, canvas_layout = make_canvas_card()
        self.compare = CompareSlider()
        self.compare.setMinimumHeight(300)
        canvas_layout.addWidget(self.compare, stretch=1)
        self.compare_hint = caption(t("ai.compare_hint"))
        canvas_layout.addWidget(self.compare_hint)
        split.addWidget(canvas_card, stretch=1)

        # ---- Cot phai: bang dieu khien (cuon doc, chieu rong co dinh) ----
        control_scroll, layout = make_control_panel()
        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        right_col.addWidget(control_scroll, stretch=1)
        split.addLayout(right_col, stretch=0)

        # ---- Card: carousel chon phong cach / preset ----
        self.choose_style_label = caption(t("ai.choose_style"))
        style_card, style_layout = make_card(self.choose_style_label)

        carousel_scroll = QScrollArea()
        carousel_scroll.setWidgetResizable(True)
        carousel_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        carousel_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        carousel_scroll.setFrameShape(QFrame.Shape.NoFrame)
        carousel_scroll.setFixedHeight(136)

        carousel_inner = QWidget()
        carousel_layout = QHBoxLayout(carousel_inner)
        carousel_layout.setSpacing(10)
        carousel_layout.setContentsMargins(2, 2, 2, 2)

        self.style_chips: dict[str, StyleChip] = {}
        for style in STYLES:
            chip = StyleChip(style.key, style.label, STYLE_EMOJI.get(style.key, "✨"))
            chip.clicked.connect(lambda _c=False, k=style.key: self._select_style(k))
            carousel_layout.addWidget(chip)
            self.style_chips[style.key] = chip
        self._carousel_layout = carousel_layout
        self.preset_chips: dict[int, StyleChip] = {}
        self._presets: list[dict] = []
        carousel_layout.addStretch()
        carousel_scroll.setWidget(carousel_inner)
        style_layout.addWidget(carousel_scroll)
        layout.addWidget(style_card)

        if STYLES:
            self.style_chips[STYLES[0].key].setChecked(True)
        self._selected_style = STYLES[0].key if STYLES else None
        self._before_pixmap: Optional[QPixmap] = None

        # ---- Card: cuong do hieu ung + ghi chu tuy chinh ----
        self.intensity_label = caption(t("ai.intensity"))
        tune_card, tune_layout = make_card(self.intensity_label)

        intensity_row = QHBoxLayout()
        self.intensity_value_label = QLabel("100%")
        self.intensity_value_label.setObjectName("FieldLabel")
        intensity_row.addStretch()
        intensity_row.addWidget(self.intensity_value_label)
        tune_layout.addLayout(intensity_row)

        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(100)
        self.intensity_slider.valueChanged.connect(
            lambda v: self.intensity_value_label.setText(f"{v}%")
        )
        tune_layout.addWidget(self.intensity_slider)

        self.extra_edit = QTextEdit()
        self.extra_edit.setPlaceholderText(t("ai.extra_placeholder"))
        self.extra_edit.setFixedHeight(60)
        tune_layout.addWidget(self.extra_edit)
        layout.addWidget(tune_card)
        layout.addStretch()

        # ---- Thanh hanh dong, ghim duoi cung cot phai (ngoai vung cuon) ----
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        self.process_btn = QPushButton(t("ai.process_button"))
        self.process_btn.setObjectName("PrimaryButton")
        self.process_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.process_btn.clicked.connect(self._emit_process)
        actions_row.addWidget(self.process_btn)

        self.save_btn = QPushButton(t("ai.save_button"))
        self.save_btn.setObjectName("SecondaryButton")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setEnabled(False)
        actions_row.addWidget(self.save_btn)
        right_col.addLayout(actions_row)

        self.save_preset_btn = QPushButton(t("ai.save_preset_button"))
        self.save_preset_btn.setObjectName("SecondaryButton")
        self.save_preset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_preset_btn.clicked.connect(self.presetSaveRequested.emit)
        right_col.addWidget(self.save_preset_btn)

    def _select_style(self, key: str):
        self._selected_style = key
        for k, chip in self.style_chips.items():
            chip.setChecked(k == key)
        for chip in self.preset_chips.values():
            chip.setChecked(False)

    def _emit_process(self):
        if self._selected_style is None:
            return
        intensity = self.intensity_slider.value() / 100.0
        self.processRequested.emit(self._selected_style, intensity, self.extra_edit.toPlainText())

    def current_settings(self):
        """Tra ve (style_key, intensity 0..1, extra_note) hien dang chon - dung de luu preset
        hoac xu ly hang loat."""
        return self._selected_style, self.intensity_slider.value() / 100.0, self.extra_edit.toPlainText()

    def set_presets(self, presets: list[dict]):
        """Ve lai danh sach chip preset tuy chinh (sau cac style dung san) tu config."""
        for chip in list(self.preset_chips.values()):
            self._carousel_layout.removeWidget(chip)
            chip.deleteLater()
        self.preset_chips.clear()
        self._presets = presets

        insert_pos = self._carousel_layout.count() - 1  # ngay truoc stretch cuoi carousel
        for idx, preset in enumerate(presets):
            chip = StyleChip(f"preset:{idx}", preset.get("name", "?"), "⭐")
            chip.clicked.connect(lambda _c=False, i=idx: self._select_preset(i))
            chip.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            chip.customContextMenuRequested.connect(lambda _pos, i=idx, c=chip: self._show_preset_menu(c, i))
            self._carousel_layout.insertWidget(insert_pos, chip)
            insert_pos += 1
            self.preset_chips[idx] = chip

    def _select_preset(self, idx: int):
        if idx >= len(self._presets):
            return
        preset = self._presets[idx]
        self._selected_style = preset.get("base_style")
        self.intensity_slider.setValue(round(preset.get("intensity", 1.0) * 100))
        self.extra_edit.setPlainText(preset.get("extra_note", ""))
        for chip in self.style_chips.values():
            chip.setChecked(False)
        for i, chip in self.preset_chips.items():
            chip.setChecked(i == idx)

    def _show_preset_menu(self, chip: StyleChip, idx: int):
        menu = QMenu(self)
        delete_action = menu.addAction(t("ai.preset_delete_action"))
        delete_action.triggered.connect(lambda: self.presetDeleteRequested.emit(idx))
        menu.exec(chip.mapToGlobal(chip.rect().center()))

    def set_before_image(self, pil_image: Optional[Image.Image]):
        self._before_pixmap = pil_to_pixmap(pil_image) if pil_image is not None else None
        self.compare.set_images(self._before_pixmap, None)
        self.save_btn.setEnabled(False)

    def set_after_image(self, pil_image: Image.Image):
        after_pixmap = pil_to_pixmap(pil_image)
        self.compare.set_images(self._before_pixmap, after_pixmap)
        self.save_btn.setEnabled(True)

    def retranslate(self):
        self.title_label.setText(t("ai.title"))
        self.compare_hint.setText(t("ai.compare_hint"))
        self.choose_style_label.setText(t("ai.choose_style"))
        self.intensity_label.setText(t("ai.intensity"))
        self.extra_edit.setPlaceholderText(t("ai.extra_placeholder"))
        self.process_btn.setText(t("ai.process_button"))
        self.save_btn.setText(t("ai.save_button"))
        self.save_preset_btn.setText(t("ai.save_preset_button"))
        for style in STYLES:
            self.style_chips[style.key].set_label(style.label)
        self.compare.update()


# ---------------------------------------------------------------------------
# 3. Trang Chinh tay
# ---------------------------------------------------------------------------
class ManualEditPage(QWidget):
    adjustmentsChanged = Signal(object)  # ManualAdjustments
    rotateRequested = Signal(int)        # +-90
    resetRequested = Signal()
    saveRequested = Signal()
    whiteBalanceRequested = Signal()
    autoAdjustRequested = Signal()

    SLIDER_SPECS = [
        ("brightness", "manual.brightness"),
        ("contrast", "manual.contrast"),
        ("saturation", "manual.saturation"),
        ("sharpness", "manual.sharpness"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(14)

        self.title_label = section_title(t("manual.title"))
        outer.addWidget(self.title_label)

        # Bo cuc 2 cot giong trang Chinh AI: canvas lon ben trai, bang dieu khien
        # (cac thanh truot) co chieu rong co dinh ben phai.
        split = QHBoxLayout()
        split.setSpacing(16)
        outer.addLayout(split, stretch=1)

        # ---- Cot trai: anh xem truoc + xoay + cong cu 1 cham ----
        canvas_card, canvas_layout = make_canvas_card()
        self._has_image = False
        self.preview_label = QLabel(t("manual.no_image"))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(240)
        canvas_layout.addWidget(self.preview_label, stretch=1)

        rotate_row = QHBoxLayout()
        self.rotate_left_btn = QPushButton("⟲")
        self.rotate_left_btn.setObjectName("IconButton")
        self.rotate_left_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rotate_left_btn.setToolTip(t("manual.rotate_left_tooltip"))
        self.rotate_left_btn.setAccessibleName(t("manual.rotate_left_tooltip"))
        self.rotate_left_btn.clicked.connect(lambda: self.rotateRequested.emit(-90))
        self.rotate_right_btn = QPushButton("⟳")
        self.rotate_right_btn.setObjectName("IconButton")
        self.rotate_right_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rotate_right_btn.setToolTip(t("manual.rotate_right_tooltip"))
        self.rotate_right_btn.setAccessibleName(t("manual.rotate_right_tooltip"))
        self.rotate_right_btn.clicked.connect(lambda: self.rotateRequested.emit(90))
        rotate_row.addWidget(self.rotate_left_btn)
        rotate_row.addWidget(self.rotate_right_btn)
        rotate_row.addStretch()

        # Cong cu 1 cham (xu ly cuc bo, khong can AI): can bang trang, tu dong chinh
        self.white_balance_btn = QPushButton(t("manual.white_balance_button"))
        self.white_balance_btn.setObjectName("SecondaryButton")
        self.white_balance_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.white_balance_btn.clicked.connect(self.whiteBalanceRequested.emit)
        self.auto_adjust_btn = QPushButton(t("manual.auto_adjust_button"))
        self.auto_adjust_btn.setObjectName("SecondaryButton")
        self.auto_adjust_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_adjust_btn.clicked.connect(self.autoAdjustRequested.emit)
        rotate_row.addWidget(self.white_balance_btn)
        rotate_row.addWidget(self.auto_adjust_btn)
        canvas_layout.addLayout(rotate_row)
        split.addWidget(canvas_card, stretch=1)

        # ---- Cot phai: bang dieu khien (cac thanh truot, cuon doc) ----
        control_scroll, layout = make_control_panel()
        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        right_col.addWidget(control_scroll, stretch=1)
        split.addLayout(right_col, stretch=0)

        sliders_card, sliders_layout = make_card()
        self.sliders: dict[str, QSlider] = {}
        self.slider_labels: dict[str, QLabel] = {}
        for key, label_key in self.SLIDER_SPECS:
            row_label = QHBoxLayout()
            label_widget = caption(t(label_key))
            self.slider_labels[key] = label_widget
            row_label.addWidget(label_widget)
            row_label.addStretch()
            sliders_layout.addLayout(row_label)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 200)
            slider.setValue(100)
            slider.valueChanged.connect(self._emit_adjustments)
            sliders_layout.addWidget(slider)
            self.sliders[key] = slider
        layout.addWidget(sliders_card)
        layout.addStretch()

        # ---- Thanh hanh dong, ghim duoi cung cot phai (ngoai vung cuon) ----
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        self.reset_btn = QPushButton(t("manual.reset_button"))
        self.reset_btn.setObjectName("SecondaryButton")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self._on_reset)
        actions_row.addWidget(self.reset_btn)

        self.save_btn = QPushButton(t("manual.save_button"))
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.saveRequested.emit)
        actions_row.addWidget(self.save_btn)
        right_col.addLayout(actions_row)

    def _emit_adjustments(self, *_args):
        adj = ManualAdjustments(
            brightness=self.sliders["brightness"].value() / 100.0,
            contrast=self.sliders["contrast"].value() / 100.0,
            saturation=self.sliders["saturation"].value() / 100.0,
            sharpness=self.sliders["sharpness"].value() / 100.0,
        )
        self.adjustmentsChanged.emit(adj)

    def _on_reset(self):
        for slider in self.sliders.values():
            slider.blockSignals(True)
            slider.setValue(100)
            slider.blockSignals(False)
        self.resetRequested.emit()
        self._emit_adjustments()

    def set_preview(self, pil_image: Optional[Image.Image]):
        if pil_image is None:
            self._has_image = False
            self.preview_label.setText(t("manual.no_image"))
            self.preview_label.setPixmap(QPixmap())
            return
        self._has_image = True
        pixmap = pil_to_pixmap(pil_image).scaled(
            self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(pixmap)

    def retranslate(self):
        self.title_label.setText(t("manual.title"))
        if not self._has_image:
            self.preview_label.setText(t("manual.no_image"))
        for key, label_key in self.SLIDER_SPECS:
            self.slider_labels[key].setText(t(label_key))
        self.reset_btn.setText(t("manual.reset_button"))
        self.save_btn.setText(t("manual.save_button"))
        self.white_balance_btn.setText(t("manual.white_balance_button"))
        self.auto_adjust_btn.setText(t("manual.auto_adjust_button"))
        self.rotate_left_btn.setToolTip(t("manual.rotate_left_tooltip"))
        self.rotate_left_btn.setAccessibleName(t("manual.rotate_left_tooltip"))
        self.rotate_right_btn.setToolTip(t("manual.rotate_right_tooltip"))
        self.rotate_right_btn.setAccessibleName(t("manual.rotate_right_tooltip"))


# ---------------------------------------------------------------------------
# 4. Trang Cai dat
# ---------------------------------------------------------------------------
class SettingsPage(QWidget):
    settingsSaved = Signal(dict)
    languageChanged = Signal(str)
    checkUpdateRequested = Signal()

    MAX_CONTENT_WIDTH = 640  # cot noi dung gioi han chieu rong, kieu app Cai dat cua Windows 11

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)
        self.title_label = section_title(t("settings.title"))
        outer.addWidget(self.title_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll, stretch=1)

        # Cot noi dung gioi han chieu rong toi da va can giua trong vung cuon - kieu
        # app Cai dat native cua Windows 11 (khong keo gian form ra het chieu rong
        # cua so, du cua so rong kieu desktop).
        centering = QWidget()
        centering_layout = QHBoxLayout(centering)
        centering_layout.setContentsMargins(0, 0, 0, 0)
        centering_layout.addStretch()
        scroll.setWidget(centering)

        inner = QWidget()
        inner.setMaximumWidth(self.MAX_CONTENT_WIDTH)
        cards_layout = QVBoxLayout(inner)
        cards_layout.setContentsMargins(0, 0, 4, 0)
        cards_layout.setSpacing(12)
        centering_layout.addWidget(inner, stretch=1)
        centering_layout.addStretch()

        # ---- Card: Ngon ngu ----
        self.language_row_label = QLabel(t("settings.language_label"))
        lang_card, lang_form = self._card_form(self.language_row_label)
        self.language_combo = QComboBox()
        for code in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(LANGUAGE_NAMES[code], userData=code)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_form.addRow(self.language_combo)
        cards_layout.addWidget(lang_card)

        # ---- Card: Gemini AI ----
        ai_card, ai_form = self._card_form(QLabel("Gemini AI"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_row_label = self._add_row(ai_form, "settings.api_key_label", self.api_key_edit)
        self.model_edit = QLineEdit()
        self.model_row_label = self._add_row(ai_form, "settings.model_label", self.model_edit)
        cards_layout.addWidget(ai_card)

        # ---- Card: May anh & thu muc ----
        folders_card, folders_layout = make_card()
        folders_form = QFormLayout()
        folders_form.setSpacing(12)
        folders_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        folders_layout.addLayout(folders_form)
        self.digicam_edit, digicam_row = self._path_row(self._browse_digicam)
        self.digicam_row_label = self._add_row(folders_form, "settings.digicam_label", digicam_row)
        self.capture_folder_edit, capture_row = self._path_row(self._browse_capture)
        self.capture_row_label = self._add_row(folders_form, "settings.capture_folder_label", capture_row)
        self.output_folder_edit, output_row = self._path_row(self._browse_output)
        self.output_row_label = self._add_row(folders_form, "settings.output_folder_label", output_row)
        cards_layout.addWidget(folders_card)

        # ---- Card: Cap nhat ----
        update_card, update_layout = make_card()
        toggle_row = QHBoxLayout()
        self.auto_update_label = QLabel(t("settings.auto_update_checkbox"))
        self.auto_update_label.setObjectName("FieldLabel")
        self.auto_update_label.setWordWrap(True)
        toggle_row.addWidget(self.auto_update_label, stretch=1)
        self.auto_update_toggle = ToggleSwitch()
        toggle_row.addWidget(self.auto_update_toggle)
        update_layout.addLayout(toggle_row)

        self.check_update_btn = QPushButton(t("settings.check_update_button"))
        self.check_update_btn.setObjectName("SecondaryButton")
        self.check_update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_update_btn.clicked.connect(self.checkUpdateRequested.emit)
        update_layout.addWidget(self.check_update_btn)

        self.update_status_label = caption("")
        update_layout.addWidget(self.update_status_label)
        cards_layout.addWidget(update_card)

        cards_layout.addStretch()

        self._app_name = ""
        self._app_version = ""
        self.version_label = caption("")
        outer.addWidget(self.version_label)

        self.save_btn = QPushButton(t("settings.save_button"))
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._emit_save)
        outer.addWidget(self.save_btn)

    @staticmethod
    def _card_form(title_label: QLabel) -> tuple[QFrame, QFormLayout]:
        card, card_layout = make_card(title_label)
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        card_layout.addLayout(form)
        return card, form

    @staticmethod
    def _add_row(form: QFormLayout, label_key: str, widget: QWidget) -> QLabel:
        label = QLabel(t(label_key))
        label.setObjectName("FieldLabel")
        form.addRow(label, widget)
        return label

    @staticmethod
    def _path_row(browse_slot):
        edit = QLineEdit()
        browse_btn = QPushButton(t("settings.browse_button"))
        browse_btn.setObjectName("SecondaryButton")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(lambda: browse_slot(edit))
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(edit)
        row_layout.addWidget(browse_btn)
        row_widget._browse_btn = browse_btn  # de retranslate sau
        return edit, row_widget

    def _browse_digicam(self, edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(self, t("settings.dialog_digicam_title"), filter="*.exe")
        if path:
            edit.setText(path)

    def _browse_capture(self, edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, t("settings.dialog_capture_title"))
        if path:
            edit.setText(path)

    def _browse_output(self, edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, t("settings.dialog_output_title"))
        if path:
            edit.setText(path)

    def _on_language_changed(self, _index: int):
        code = self.language_combo.currentData()
        if code:
            self.languageChanged.emit(code)

    def load_from_config(self, cfg: dict, app_name: str, app_version: str):
        self.api_key_edit.setText(cfg.get("gemini_api_key", ""))
        self.model_edit.setText(cfg.get("gemini_model", ""))
        self.digicam_edit.setText(cfg.get("digicam_cmd_path", ""))
        self.capture_folder_edit.setText(cfg.get("capture_folder", ""))
        self.output_folder_edit.setText(cfg.get("output_folder", ""))
        self._app_name = app_name
        self._app_version = app_version
        self.version_label.setText(t("settings.version_label", app_name=app_name, app_version=app_version))

        lang = cfg.get("language")
        idx = self.language_combo.findData(lang)
        if idx >= 0:
            self.language_combo.blockSignals(True)
            self.language_combo.setCurrentIndex(idx)
            self.language_combo.blockSignals(False)

        self.auto_update_toggle.setChecked(bool(cfg.get("auto_check_updates", True)))

    def set_update_status(self, text: str):
        self.update_status_label.setText(text)

    def _emit_save(self):
        self.settingsSaved.emit({
            "gemini_api_key": self.api_key_edit.text().strip(),
            "gemini_model": self.model_edit.text().strip() or "gemini-2.5-flash-image",
            "digicam_cmd_path": self.digicam_edit.text().strip(),
            "capture_folder": self.capture_folder_edit.text().strip(),
            "output_folder": self.output_folder_edit.text().strip(),
            "language": self.language_combo.currentData() or get_language(),
            "auto_check_updates": self.auto_update_toggle.isChecked(),
        })

    def retranslate(self):
        self.title_label.setText(t("settings.title"))
        self.language_row_label.setText(t("settings.language_label"))
        self.api_key_row_label.setText(t("settings.api_key_label"))
        self.model_row_label.setText(t("settings.model_label"))
        self.digicam_row_label.setText(t("settings.digicam_label"))
        self.capture_row_label.setText(t("settings.capture_folder_label"))
        self.output_row_label.setText(t("settings.output_folder_label"))
        self.save_btn.setText(t("settings.save_button"))
        self.auto_update_label.setText(t("settings.auto_update_checkbox"))
        self.check_update_btn.setText(t("settings.check_update_button"))
        if self._app_name:
            self.version_label.setText(
                t("settings.version_label", app_name=self._app_name, app_version=self._app_version)
            )
        for row in (self.digicam_edit.parentWidget(), self.capture_folder_edit.parentWidget(),
                    self.output_folder_edit.parentWidget()):
            if hasattr(row, "_browse_btn"):
                row._browse_btn.setText(t("settings.browse_button"))
