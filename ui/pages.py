"""
ui/pages.py - 4 trang chinh cua ung dung: Thu vien, Chinh AI, Chinh tay, Cai dat.
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
from ui.widgets import StyleChip, CompareSlider, pil_to_pixmap
from i18n import t, get_language, set_language, SUPPORTED_LANGUAGES, LANGUAGE_NAMES

THUMB_SIZE = QSize(150, 150)

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
        layout.setContentsMargins(20, 20, 20, 12)
        layout.setSpacing(16)

        header = QHBoxLayout()
        self.title_label = section_title(t("library.title"))
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)

        self.capture_btn = QPushButton(t("library.capture_button"))
        self.capture_btn.setObjectName("PrimaryButton")
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.clicked.connect(self.captureRequested.emit)
        layout.addWidget(self.capture_btn)

        selection_row = QHBoxLayout()
        self.multi_select_btn = QPushButton(t("library.multi_select_button"))
        self.multi_select_btn.setObjectName("SecondaryButton")
        self.multi_select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.multi_select_btn.setCheckable(True)
        self.multi_select_btn.toggled.connect(self._on_multi_select_toggled)
        selection_row.addWidget(self.multi_select_btn)

        self.batch_btn = QPushButton()
        self.batch_btn.setObjectName("SecondaryButton")
        self.batch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.batch_btn.setEnabled(False)
        self.batch_btn.setVisible(False)
        self.batch_btn.clicked.connect(self._emit_batch)
        selection_row.addWidget(self.batch_btn)
        layout.addLayout(selection_row)

        self.photo_list = QListWidget()
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 12)
        layout.setSpacing(14)

        self.title_label = section_title(t("ai.title"))
        layout.addWidget(self.title_label)

        self.compare = CompareSlider()
        self.compare.setMinimumHeight(320)
        layout.addWidget(self.compare, stretch=1)
        self.compare_hint = caption(t("ai.compare_hint"))
        layout.addWidget(self.compare_hint)

        self.choose_style_label = caption(t("ai.choose_style"))
        layout.addWidget(self.choose_style_label)
        carousel_scroll = QScrollArea()
        carousel_scroll.setWidgetResizable(True)
        carousel_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        carousel_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        carousel_scroll.setFixedHeight(120)

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
        layout.addWidget(carousel_scroll)

        if STYLES:
            self.style_chips[STYLES[0].key].setChecked(True)
        self._selected_style = STYLES[0].key if STYLES else None
        self._before_pixmap: Optional[QPixmap] = None

        intensity_row = QHBoxLayout()
        self.intensity_label = caption(t("ai.intensity"))
        intensity_row.addWidget(self.intensity_label)
        self.intensity_value_label = QLabel("100%")
        intensity_row.addStretch()
        intensity_row.addWidget(self.intensity_value_label)
        layout.addLayout(intensity_row)

        self.intensity_slider = QSlider(Qt.Orientation.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(100)
        self.intensity_slider.valueChanged.connect(
            lambda v: self.intensity_value_label.setText(f"{v}%")
        )
        layout.addWidget(self.intensity_slider)

        self.extra_edit = QTextEdit()
        self.extra_edit.setPlaceholderText(t("ai.extra_placeholder"))
        self.extra_edit.setFixedHeight(50)
        layout.addWidget(self.extra_edit)

        actions_row = QHBoxLayout()
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
        layout.addLayout(actions_row)

        self.save_preset_btn = QPushButton(t("ai.save_preset_button"))
        self.save_preset_btn.setObjectName("SecondaryButton")
        self.save_preset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_preset_btn.clicked.connect(self.presetSaveRequested.emit)
        layout.addWidget(self.save_preset_btn)

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 12)
        layout.setSpacing(14)

        self.title_label = section_title(t("manual.title"))
        layout.addWidget(self.title_label)

        self._has_image = False
        self.preview_label = QLabel(t("manual.no_image"))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(260)
        self.preview_label.setObjectName("Card")
        layout.addWidget(self.preview_label, stretch=1)

        rotate_row = QHBoxLayout()
        rotate_left = QPushButton("⟲")
        rotate_left.setObjectName("IconButton")
        rotate_left.setCursor(Qt.CursorShape.PointingHandCursor)
        rotate_left.clicked.connect(lambda: self.rotateRequested.emit(-90))
        rotate_right = QPushButton("⟳")
        rotate_right.setObjectName("IconButton")
        rotate_right.setCursor(Qt.CursorShape.PointingHandCursor)
        rotate_right.clicked.connect(lambda: self.rotateRequested.emit(90))
        rotate_row.addWidget(rotate_left)
        rotate_row.addWidget(rotate_right)
        rotate_row.addStretch()
        layout.addLayout(rotate_row)

        # Cong cu 1 cham (xu ly cuc bo, khong can AI): can bang trang, tu dong chinh
        one_tap_row = QHBoxLayout()
        self.white_balance_btn = QPushButton(t("manual.white_balance_button"))
        self.white_balance_btn.setObjectName("SecondaryButton")
        self.white_balance_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.white_balance_btn.clicked.connect(self.whiteBalanceRequested.emit)
        self.auto_adjust_btn = QPushButton(t("manual.auto_adjust_button"))
        self.auto_adjust_btn.setObjectName("SecondaryButton")
        self.auto_adjust_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_adjust_btn.clicked.connect(self.autoAdjustRequested.emit)
        one_tap_row.addWidget(self.white_balance_btn)
        one_tap_row.addWidget(self.auto_adjust_btn)
        layout.addLayout(one_tap_row)

        self.sliders: dict[str, QSlider] = {}
        self.slider_labels: dict[str, QLabel] = {}
        for key, label_key in self.SLIDER_SPECS:
            row_label = QHBoxLayout()
            label_widget = caption(t(label_key))
            self.slider_labels[key] = label_widget
            row_label.addWidget(label_widget)
            row_label.addStretch()
            layout.addLayout(row_label)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 200)
            slider.setValue(100)
            slider.valueChanged.connect(self._emit_adjustments)
            layout.addWidget(slider)
            self.sliders[key] = slider

        actions_row = QHBoxLayout()
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
        layout.addLayout(actions_row)

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


# ---------------------------------------------------------------------------
# 4. Trang Cai dat
# ---------------------------------------------------------------------------
class SettingsPage(QWidget):
    settingsSaved = Signal(dict)
    languageChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 12)
        outer.setSpacing(16)
        self.title_label = section_title(t("settings.title"))
        outer.addWidget(self.title_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        inner = QWidget()
        self.form = QFormLayout(inner)
        self.form.setSpacing(14)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.language_combo = QComboBox()
        for code in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(LANGUAGE_NAMES[code], userData=code)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.language_row_label = self._add_row("settings.language_label", self.language_combo)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_row_label = self._add_row("settings.api_key_label", self.api_key_edit)

        self.model_edit = QLineEdit()
        self.model_row_label = self._add_row("settings.model_label", self.model_edit)

        self.digicam_edit, digicam_row = self._path_row(self._browse_digicam)
        self.digicam_row_label = self._add_row("settings.digicam_label", digicam_row)

        self.capture_folder_edit, capture_row = self._path_row(self._browse_capture)
        self.capture_row_label = self._add_row("settings.capture_folder_label", capture_row)

        self.output_folder_edit, output_row = self._path_row(self._browse_output)
        self.output_row_label = self._add_row("settings.output_folder_label", output_row)

        scroll.setWidget(inner)

        self.save_btn = QPushButton(t("settings.save_button"))
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._emit_save)
        outer.addWidget(self.save_btn)

        self._app_name = ""
        self._app_version = ""
        self.version_label = caption("")
        outer.addWidget(self.version_label)

    def _add_row(self, label_key: str, widget: QWidget) -> QLabel:
        label = QLabel(t(label_key))
        self.form.addRow(label, widget)
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

    def _emit_save(self):
        self.settingsSaved.emit({
            "gemini_api_key": self.api_key_edit.text().strip(),
            "gemini_model": self.model_edit.text().strip() or "gemini-2.5-flash-image",
            "digicam_cmd_path": self.digicam_edit.text().strip(),
            "capture_folder": self.capture_folder_edit.text().strip(),
            "output_folder": self.output_folder_edit.text().strip(),
            "language": self.language_combo.currentData() or get_language(),
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
        if self._app_name:
            self.version_label.setText(
                t("settings.version_label", app_name=self._app_name, app_version=self._app_version)
            )
        for row in (self.digicam_edit.parentWidget(), self.capture_folder_edit.parentWidget(),
                    self.output_folder_edit.parentWidget()):
            if hasattr(row, "_browse_btn"):
                row._browse_btn.setText(t("settings.browse_button"))
