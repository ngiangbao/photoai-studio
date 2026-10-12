"""
ui/pages.py - 4 trang chinh cua ung dung: Thu vien, Chinh AI, Chinh tay, Cai dat.
"""
from pathlib import Path
from typing import Optional

from PIL import Image
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QScrollArea, QFrame, QSlider, QLineEdit,
    QFormLayout, QFileDialog, QTextEdit, QSizePolicy
)

from ai.styles import STYLES
from ai.manual_edit import ManualAdjustments
from ui.widgets import StyleChip, CompareSlider, pil_to_pixmap

THUMB_SIZE = QSize(150, 150)

STYLE_EMOJI = {
    "portrait": "🧑",
    "outdoor": "🌳",
    "landscape": "🏞️",
    "people": "👥",
    "graduation": "🎓",
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


def card_frame() -> QFrame:
    frame = QFrame()
    frame.setObjectName("Card")
    return frame


# ---------------------------------------------------------------------------
# 1. Trang Thu vien
# ---------------------------------------------------------------------------
class LibraryPage(QWidget):
    captureRequested = Signal()
    photoSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 12)
        layout.setSpacing(16)

        header = QHBoxLayout()
        header.addWidget(section_title("Thư viện"))
        header.addStretch()
        layout.addLayout(header)

        self.capture_btn = QPushButton("📷  Chụp ảnh mới")
        self.capture_btn.setObjectName("PrimaryButton")
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.clicked.connect(self.captureRequested.emit)
        layout.addWidget(self.capture_btn)

        self.photo_list = QListWidget()
        self.photo_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.photo_list.setIconSize(THUMB_SIZE)
        self.photo_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.photo_list.setSpacing(10)
        self.photo_list.setMovement(QListWidget.Movement.Static)
        self.photo_list.itemClicked.connect(
            lambda item: self.photoSelected.emit(item.data(Qt.ItemDataRole.UserRole))
        )
        layout.addWidget(self.photo_list)

        self.empty_hint = caption("Chưa có ảnh nào. Cắm máy ảnh qua USB rồi bấm \"Chụp ảnh mới\".")
        layout.addWidget(self.empty_hint)

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


# ---------------------------------------------------------------------------
# 2. Trang Chinh sua AI
# ---------------------------------------------------------------------------
class AIEditPage(QWidget):
    processRequested = Signal(str, float, str)  # style_key, intensity(0..1), extra_note

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 12)
        layout.setSpacing(14)

        layout.addWidget(section_title("Chỉnh sửa bằng AI"))

        self.compare = CompareSlider()
        self.compare.setMinimumHeight(320)
        layout.addWidget(self.compare, stretch=1)
        layout.addWidget(caption("Kéo thanh trắng để so sánh ảnh gốc / kết quả AI."))

        layout.addWidget(caption("Chọn phong cách"))
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
        carousel_layout.addStretch()
        carousel_scroll.setWidget(carousel_inner)
        layout.addWidget(carousel_scroll)

        if STYLES:
            self.style_chips[STYLES[0].key].setChecked(True)
        self._selected_style = STYLES[0].key if STYLES else None
        self._before_pixmap: Optional[QPixmap] = None

        intensity_row = QHBoxLayout()
        intensity_row.addWidget(caption("Cường độ hiệu ứng"))
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
        self.extra_edit.setPlaceholderText("Ghi chú thêm cho AI (tuỳ chọn)...")
        self.extra_edit.setFixedHeight(50)
        layout.addWidget(self.extra_edit)

        actions_row = QHBoxLayout()
        self.process_btn = QPushButton("✨  Áp dụng AI")
        self.process_btn.setObjectName("PrimaryButton")
        self.process_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.process_btn.clicked.connect(self._emit_process)
        actions_row.addWidget(self.process_btn)

        self.save_btn = QPushButton("💾  Lưu ảnh")
        self.save_btn.setObjectName("SecondaryButton")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setEnabled(False)
        actions_row.addWidget(self.save_btn)
        layout.addLayout(actions_row)

    def _select_style(self, key: str):
        self._selected_style = key
        for k, chip in self.style_chips.items():
            chip.setChecked(k == key)

    def _emit_process(self):
        if self._selected_style is None:
            return
        intensity = self.intensity_slider.value() / 100.0
        self.processRequested.emit(self._selected_style, intensity, self.extra_edit.toPlainText())

    def set_before_image(self, pil_image: Optional[Image.Image]):
        self._before_pixmap = pil_to_pixmap(pil_image) if pil_image is not None else None
        self.compare.set_images(self._before_pixmap, None)
        self.save_btn.setEnabled(False)

    def set_after_image(self, pil_image: Image.Image):
        after_pixmap = pil_to_pixmap(pil_image)
        self.compare.set_images(self._before_pixmap, after_pixmap)
        self.save_btn.setEnabled(True)


# ---------------------------------------------------------------------------
# 3. Trang Chinh tay
# ---------------------------------------------------------------------------
class ManualEditPage(QWidget):
    adjustmentsChanged = Signal(object)  # ManualAdjustments
    rotateRequested = Signal(int)        # +-90
    resetRequested = Signal()
    saveRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 12)
        layout.setSpacing(14)

        layout.addWidget(section_title("Chỉnh tay"))

        self.preview_label = QLabel("Chưa chọn ảnh")
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

        self.sliders: dict[str, QSlider] = {}
        for key, label in [
            ("brightness", "Độ sáng"),
            ("contrast", "Tương phản"),
            ("saturation", "Bão hoà"),
            ("sharpness", "Độ nét"),
        ]:
            row_label = QHBoxLayout()
            row_label.addWidget(caption(label))
            row_label.addStretch()
            layout.addLayout(row_label)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 200)
            slider.setValue(100)
            slider.valueChanged.connect(self._emit_adjustments)
            layout.addWidget(slider)
            self.sliders[key] = slider

        actions_row = QHBoxLayout()
        reset_btn = QPushButton("Đặt lại")
        reset_btn.setObjectName("SecondaryButton")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset)
        actions_row.addWidget(reset_btn)

        self.save_btn = QPushButton("💾  Lưu ảnh")
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
            self.preview_label.setText("Chưa chọn ảnh")
            self.preview_label.setPixmap(QPixmap())
            return
        pixmap = pil_to_pixmap(pil_image).scaled(
            self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(pixmap)


# ---------------------------------------------------------------------------
# 4. Trang Cai dat
# ---------------------------------------------------------------------------
class SettingsPage(QWidget):
    settingsSaved = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 12)
        outer.setSpacing(16)
        outer.addWidget(section_title("Cài đặt"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        inner = QWidget()
        form = QFormLayout(inner)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Gemini API key", self.api_key_edit)

        self.model_edit = QLineEdit()
        form.addRow("Model Gemini", self.model_edit)

        self.digicam_edit, digicam_row = self._path_row(self._browse_digicam)
        form.addRow("CameraControlCmd.exe", digicam_row)

        self.capture_folder_edit, capture_row = self._path_row(self._browse_capture)
        form.addRow("Thư mục ảnh chụp", capture_row)

        self.output_folder_edit, output_row = self._path_row(self._browse_output)
        form.addRow("Thư mục ảnh đã chỉnh", output_row)

        scroll.setWidget(inner)

        self.save_btn = QPushButton("💾  Lưu cài đặt")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._emit_save)
        outer.addWidget(self.save_btn)

        self.version_label = caption("")
        outer.addWidget(self.version_label)

    @staticmethod
    def _path_row(browse_slot):
        edit = QLineEdit()
        browse_btn = QPushButton("Chọn...")
        browse_btn.setObjectName("SecondaryButton")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(lambda: browse_slot(edit))
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(edit)
        row_layout.addWidget(browse_btn)
        return edit, row_widget

    def _browse_digicam(self, edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn CameraControlCmd.exe", filter="*.exe")
        if path:
            edit.setText(path)

    def _browse_capture(self, edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "Chọn thư mục ảnh chụp")
        if path:
            edit.setText(path)

    def _browse_output(self, edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "Chọn thư mục ảnh đã chỉnh")
        if path:
            edit.setText(path)

    def load_from_config(self, cfg: dict, app_name: str, app_version: str):
        self.api_key_edit.setText(cfg.get("gemini_api_key", ""))
        self.model_edit.setText(cfg.get("gemini_model", ""))
        self.digicam_edit.setText(cfg.get("digicam_cmd_path", ""))
        self.capture_folder_edit.setText(cfg.get("capture_folder", ""))
        self.output_folder_edit.setText(cfg.get("output_folder", ""))
        self.version_label.setText(f"{app_name} • phiên bản {app_version}")

    def _emit_save(self):
        self.settingsSaved.emit({
            "gemini_api_key": self.api_key_edit.text().strip(),
            "gemini_model": self.model_edit.text().strip() or "gemini-2.5-flash-image",
            "digicam_cmd_path": self.digicam_edit.text().strip(),
            "capture_folder": self.capture_folder_edit.text().strip(),
            "output_folder": self.output_folder_edit.text().strip(),
        })
