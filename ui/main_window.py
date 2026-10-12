"""
ui/main_window.py - Giao dien chinh cua ung dung
"""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, QThread, Signal, QFileSystemWatcher
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QComboBox, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QFileDialog, QStatusBar,
    QSplitter, QTextEdit
)

from config import load_config, save_config, APP_NAME, APP_VERSION
from camera.digicam import DigiCamController, DigiCamError
from ai.styles import STYLES
from ai.gemini_editor import GeminiEditor, GeminiEditError

THUMB_SIZE = QSize(140, 140)


class SettingsDialog(QDialog):
    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cai dat")
        self.cfg = cfg.copy()

        layout = QFormLayout(self)

        self.api_key_edit = QLineEdit(self.cfg.get("gemini_api_key", ""))
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Gemini API key:", self.api_key_edit)

        self.model_edit = QLineEdit(self.cfg.get("gemini_model", "gemini-2.5-flash-image"))
        layout.addRow("Model Gemini:", self.model_edit)

        self.digicam_edit = QLineEdit(self.cfg.get("digicam_cmd_path", ""))
        browse_digicam = QPushButton("Chon...")
        browse_digicam.clicked.connect(self._browse_digicam)
        digicam_row = QHBoxLayout()
        digicam_row.addWidget(self.digicam_edit)
        digicam_row.addWidget(browse_digicam)
        layout.addRow("CameraControlCmd.exe:", digicam_row)

        self.capture_folder_edit = QLineEdit(self.cfg.get("capture_folder", ""))
        browse_capture = QPushButton("Chon...")
        browse_capture.clicked.connect(self._browse_capture_folder)
        capture_row = QHBoxLayout()
        capture_row.addWidget(self.capture_folder_edit)
        capture_row.addWidget(browse_capture)
        layout.addRow("Thu muc anh chup:", capture_row)

        self.output_folder_edit = QLineEdit(self.cfg.get("output_folder", ""))
        browse_output = QPushButton("Chon...")
        browse_output.clicked.connect(self._browse_output_folder)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_folder_edit)
        output_row.addWidget(browse_output)
        layout.addRow("Thu muc anh da chinh:", output_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _browse_digicam(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chon CameraControlCmd.exe", filter="*.exe")
        if path:
            self.digicam_edit.setText(path)

    def _browse_capture_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Chon thu muc anh chup")
        if path:
            self.capture_folder_edit.setText(path)

    def _browse_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Chon thu muc anh da chinh")
        if path:
            self.output_folder_edit.setText(path)

    def result_config(self) -> dict:
        self.cfg["gemini_api_key"] = self.api_key_edit.text().strip()
        self.cfg["gemini_model"] = self.model_edit.text().strip() or "gemini-2.5-flash-image"
        self.cfg["digicam_cmd_path"] = self.digicam_edit.text().strip()
        self.cfg["capture_folder"] = self.capture_folder_edit.text().strip()
        self.cfg["output_folder"] = self.output_folder_edit.text().strip()
        return self.cfg


class CaptureWorker(QThread):
    finished_ok = Signal(str)
    failed = Signal(str)

    def __init__(self, controller: DigiCamController, parent=None):
        super().__init__(parent)
        self.controller = controller

    def run(self):
        try:
            path = self.controller.capture_photo()
            self.finished_ok.emit(str(path))
        except DigiCamError as exc:
            self.failed.emit(str(exc))


class EditWorker(QThread):
    finished_ok = Signal(object, str)
    failed = Signal(str)

    def __init__(self, editor: GeminiEditor, image_path: str, style_key: str, extra: str, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.image_path = image_path
        self.style_key = style_key
        self.extra = extra

    def run(self):
        try:
            result = self.editor.edit_image(self.image_path, self.style_key, self.extra)
            self.finished_ok.emit(result, self.image_path)
        except GeminiEditError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"Loi khong xac dinh: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} ({APP_VERSION})")
        self.resize(1100, 700)

        self.cfg = load_config()
        self.selected_photo_path: Optional[str] = None
        self.last_edited_image = None
        self._capture_worker = None
        self._edit_worker = None

        self._build_ui()
        self._init_camera()
        self._init_watcher()
        self._refresh_photo_list()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        left = QVBoxLayout()
        self.capture_btn = QPushButton("Chup anh moi")
        self.capture_btn.clicked.connect(self.on_capture_clicked)
        left.addWidget(self.capture_btn)

        self.photo_list = QListWidget()
        self.photo_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.photo_list.setIconSize(THUMB_SIZE)
        self.photo_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.photo_list.itemClicked.connect(self.on_photo_selected)
        left.addWidget(self.photo_list)

        settings_btn = QPushButton("Cai dat")
        settings_btn.clicked.connect(self.on_settings_clicked)
        left.addWidget(settings_btn)

        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(280)

        right = QVBoxLayout()

        preview_row = QHBoxLayout()
        self.before_label = QLabel("Chua chon anh")
        self.before_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.before_label.setMinimumSize(360, 360)
        self.before_label.setStyleSheet("border: 1px solid #999;")
        self.after_label = QLabel("Ket qua AI")
        self.after_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.after_label.setMinimumSize(360, 360)
        self.after_label.setStyleSheet("border: 1px solid #999;")
        preview_row.addWidget(self.before_label)
        preview_row.addWidget(self.after_label)
        right.addLayout(preview_row)

        controls_row = QHBoxLayout()
        self.style_combo = QComboBox()
        for style in STYLES:
            self.style_combo.addItem(style.label, userData=style.key)
        controls_row.addWidget(QLabel("Phong cach:"))
        controls_row.addWidget(self.style_combo)

        self.process_btn = QPushButton("Chinh sua bang AI")
        self.process_btn.clicked.connect(self.on_process_clicked)
        controls_row.addWidget(self.process_btn)

        self.save_btn = QPushButton("Luu anh")
        self.save_btn.clicked.connect(self.on_save_clicked)
        self.save_btn.setEnabled(False)
        controls_row.addWidget(self.save_btn)
        right.addLayout(controls_row)

        self.extra_edit = QTextEdit()
        self.extra_edit.setPlaceholderText("Ghi chu them cho AI (tuy chon)...")
        self.extra_edit.setFixedHeight(60)
        right.addWidget(self.extra_edit)

        right_widget = QWidget()
        right_widget.setLayout(right)

        splitter = QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        root.addWidget(splitter)

        self.setStatusBar(QStatusBar())

    def _init_camera(self):
        self.digicam = DigiCamController(
            self.cfg["digicam_cmd_path"], self.cfg["capture_folder"]
        )

    def _init_watcher(self):
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.cfg["capture_folder"])
        self.watcher.directoryChanged.connect(self._refresh_photo_list)

    def _refresh_photo_list(self):
        folder = Path(self.cfg["capture_folder"])
        existing = {
            self.photo_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.photo_list.count())
        }
        files = sorted(
            list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg")) + list(folder.glob("*.png")),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for path in files:
            if str(path) in existing:
                continue
            icon = QIcon(QPixmap(str(path)).scaled(
                THUMB_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
            item = QListWidgetItem(icon, path.name)
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.photo_list.insertItem(0, item)

    def on_capture_clicked(self):
        if not self.digicam.is_available():
            QMessageBox.warning(
                self, "Thieu digiCamControl",
                "Khong tim thay CameraControlCmd.exe. Vao Cai dat de chinh duong dan, "
                "hoac cai digiCamControl tai digicamcontrol.com."
            )
            return
        self.capture_btn.setEnabled(False)
        self.statusBar().showMessage("Dang chup anh tu may anh...")
        self._capture_worker = CaptureWorker(self.digicam)
        self._capture_worker.finished_ok.connect(self._on_capture_ok)
        self._capture_worker.failed.connect(self._on_capture_failed)
        self._capture_worker.start()

    def _on_capture_ok(self, path: str):
        self.capture_btn.setEnabled(True)
        self.statusBar().showMessage(f"Da chup: {path}", 5000)
        self._refresh_photo_list()

    def _on_capture_failed(self, message: str):
        self.capture_btn.setEnabled(True)
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "Loi chup anh", message)

    def on_photo_selected(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.selected_photo_path = path
        pixmap = QPixmap(path).scaled(
            self.before_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.before_label.setPixmap(pixmap)
        self.after_label.setText("Ket qua AI")
        self.after_label.setPixmap(QPixmap())
        self.save_btn.setEnabled(False)
        self.last_edited_image = None

    def on_settings_clicked(self):
        dialog = SettingsDialog(self.cfg, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cfg = dialog.result_config()
            save_config(self.cfg)
            self._init_camera()
            self.watcher.removePaths(self.watcher.directories())
            self.watcher.addPath(self.cfg["capture_folder"])
            self._refresh_photo_list()

    def on_process_clicked(self):
        if not self.selected_photo_path:
            QMessageBox.information(self, "Chua chon anh", "Hay chon mot anh o danh sach ben trai.")
            return
        if not self.cfg.get("gemini_api_key"):
            QMessageBox.warning(self, "Thieu API key", "Hay vao Cai dat de nhap Gemini API key.")
            return

        try:
            editor = GeminiEditor(self.cfg["gemini_api_key"], self.cfg["gemini_model"])
        except GeminiEditError as exc:
            QMessageBox.critical(self, "Loi cau hinh", str(exc))
            return

        style_key = self.style_combo.currentData()
        extra = self.extra_edit.toPlainText()

        self.process_btn.setEnabled(False)
        self.statusBar().showMessage("AI dang xu ly anh, vui long cho...")
        self._edit_worker = EditWorker(editor, self.selected_photo_path, style_key, extra)
        self._edit_worker.finished_ok.connect(self._on_edit_ok)
        self._edit_worker.failed.connect(self._on_edit_failed)
        self._edit_worker.start()

    def _on_edit_ok(self, pil_image, source_path: str):
        self.process_btn.setEnabled(True)
        self.statusBar().showMessage("Xu ly xong.", 5000)
        self.last_edited_image = pil_image

        pixmap = self._pil_to_pixmap(pil_image).scaled(
            self.after_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.after_label.setPixmap(pixmap)
        self.save_btn.setEnabled(True)

    def _on_edit_failed(self, message: str):
        self.process_btn.setEnabled(True)
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "Loi xu ly AI", message)

    def on_save_clicked(self):
        if self.last_edited_image is None or not self.selected_photo_path:
            return
        output_folder = Path(self.cfg["output_folder"])
        output_folder.mkdir(parents=True, exist_ok=True)
        src_name = Path(self.selected_photo_path).stem
        style_key = self.style_combo.currentData()
        out_path = output_folder / f"{src_name}_{style_key}.jpg"
        self.last_edited_image.convert("RGB").save(out_path, quality=95)
        QMessageBox.information(self, "Da luu", f"Anh da duoc luu tai:\n{out_path}")

    @staticmethod
    def _pil_to_pixmap(pil_image):
        pil_image = pil_image.convert("RGB")
        data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(data, pil_image.width, pil_image.height, pil_image.width * 3, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qimage)
