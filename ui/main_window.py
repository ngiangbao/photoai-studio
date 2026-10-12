"""
ui/main_window.py - Cua so chinh: dieu phoi 4 trang (Thu vien / Chinh AI / Chinh tay / Cai dat)
qua thanh dieu huong duoi, phong cach giong app chinh anh di dong, than thien cam ung.
"""
from pathlib import Path
from typing import Optional

from PIL import Image
from PySide6.QtCore import Qt, QThread, Signal, QFileSystemWatcher
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMessageBox

from config import load_config, save_config, APP_NAME, APP_VERSION
from camera.digicam import DigiCamController, DigiCamError
from ai.gemini_editor import GeminiEditor, GeminiEditError
from ai.manual_edit import ManualAdjustments, apply_adjustments, blend_with_original
from ui.theme import QSS
from ui.widgets import BottomNavBar, NavItem
from ui.pages import LibraryPage, AIEditPage, ManualEditPage, SettingsPage
from i18n import t, set_language

MANUAL_PREVIEW_MAX = 900  # px, de keo slider muot tren anh lon


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
    finished_ok = Signal(object)  # PIL Image (anh AI goc, chua blend)
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
            self.finished_ok.emit(result)
        except GeminiEditError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"{t('error.gemini_api_call', error=exc)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        set_language(self.cfg.get("language", "vi"))

        self.setWindowTitle(f"{APP_NAME} ({APP_VERSION})")
        self.resize(420, 780)
        self.setMinimumSize(380, 640)
        self.setStyleSheet(QSS)

        self.selected_photo_path: Optional[str] = None
        self.original_image: Optional[Image.Image] = None      # anh goc, full-res
        self.ai_raw_result: Optional[Image.Image] = None        # ket qua AI chua blend
        self.ai_final_result: Optional[Image.Image] = None      # ket qua AI da blend theo cuong do
        self.manual_result: Optional[Image.Image] = None        # ket qua chinh tay, full-res
        self._manual_preview_source: Optional[Image.Image] = None
        self._manual_rotation = 0
        self._capture_worker = None
        self._edit_worker = None

        self._build_ui()
        self._init_camera()
        self._init_watcher()
        self.library_page.refresh(self.cfg["capture_folder"])
        self.settings_page.load_from_config(self.cfg, APP_NAME, APP_VERSION)

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.stack = QStackedWidget()
        self.library_page = LibraryPage()
        self.ai_page = AIEditPage()
        self.manual_page = ManualEditPage()
        self.settings_page = SettingsPage()

        for page in (self.library_page, self.ai_page, self.manual_page, self.settings_page):
            self.stack.addWidget(page)

        root.addWidget(self.stack, stretch=1)

        self.nav = BottomNavBar([
            NavItem("library", "nav.library", "🖼️"),
            NavItem("ai", "nav.ai", "✨"),
            NavItem("manual", "nav.manual", "🎚️"),
            NavItem("settings", "nav.settings", "⚙️"),
        ])
        self.nav.tabChanged.connect(self._on_tab_changed)
        root.addWidget(self.nav)

        self.library_page.captureRequested.connect(self.on_capture_clicked)
        self.library_page.photoSelected.connect(self.on_photo_selected)
        self.ai_page.processRequested.connect(self.on_ai_process_requested)
        self.ai_page.save_btn.clicked.connect(self.on_ai_save_clicked)
        self.manual_page.adjustmentsChanged.connect(self.on_manual_adjustments_changed)
        self.manual_page.rotateRequested.connect(self.on_manual_rotate)
        self.manual_page.resetRequested.connect(self.on_manual_reset)
        self.manual_page.saveRequested.connect(self.on_manual_save_clicked)
        self.settings_page.settingsSaved.connect(self.on_settings_saved)
        self.settings_page.languageChanged.connect(self.on_language_changed)

        self.statusBar().showMessage(t("status.ready"))

    def _on_tab_changed(self, key: str):
        index = {"library": 0, "ai": 1, "manual": 2, "settings": 3}.get(key, 0)
        self.stack.setCurrentIndex(index)

    def _init_camera(self):
        self.digicam = DigiCamController(self.cfg["digicam_cmd_path"], self.cfg["capture_folder"])

    def _init_watcher(self):
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(self.cfg["capture_folder"])
        self.watcher.directoryChanged.connect(
            lambda: self.library_page.refresh(self.cfg["capture_folder"])
        )

    # ------------------------------------------------------------------
    # Chup anh
    # ------------------------------------------------------------------
    def on_capture_clicked(self):
        if not self.digicam.is_available():
            QMessageBox.warning(
                self, t("dialog.missing_digicam_title"),
                t("dialog.missing_digicam_message"),
            )
            return
        self.library_page.capture_btn.setEnabled(False)
        self.statusBar().showMessage(t("status.capturing"))
        self._capture_worker = CaptureWorker(self.digicam)
        self._capture_worker.finished_ok.connect(self._on_capture_ok)
        self._capture_worker.failed.connect(self._on_capture_failed)
        self._capture_worker.start()

    def _on_capture_ok(self, path: str):
        self.library_page.capture_btn.setEnabled(True)
        self.statusBar().showMessage(t("status.captured", name=Path(path).name), 5000)
        self.library_page.refresh(self.cfg["capture_folder"])

    def _on_capture_failed(self, message: str):
        self.library_page.capture_btn.setEnabled(True)
        self.statusBar().clearMessage()
        QMessageBox.critical(self, t("dialog.capture_error_title"), message)

    # ------------------------------------------------------------------
    # Chon anh
    # ------------------------------------------------------------------
    def on_photo_selected(self, path: str):
        self.selected_photo_path = path
        try:
            self.original_image = Image.open(path)
            self.original_image.load()
        except Exception as exc:
            QMessageBox.critical(self, t("dialog.open_image_error_title"), t("dialog.open_image_error_message", error=exc))
            return

        self.ai_raw_result = None
        self.ai_final_result = None
        self.manual_result = None
        self._manual_rotation = 0

        preview = self.original_image.copy()
        preview.thumbnail((MANUAL_PREVIEW_MAX, MANUAL_PREVIEW_MAX))
        self._manual_preview_source = preview

        self.ai_page.set_before_image(self.original_image)
        self.manual_page.set_preview(self._manual_preview_source)
        for slider in self.manual_page.sliders.values():
            slider.blockSignals(True)
            slider.setValue(100)
            slider.blockSignals(False)

    # ------------------------------------------------------------------
    # Chinh sua AI
    # ------------------------------------------------------------------
    def on_ai_process_requested(self, style_key: str, intensity: float, extra: str):
        if not self.selected_photo_path:
            QMessageBox.information(self, t("dialog.no_photo_selected_title"), t("dialog.no_photo_selected_message"))
            return
        if not self.cfg.get("gemini_api_key"):
            QMessageBox.warning(self, t("dialog.missing_api_key_title"), t("dialog.missing_api_key_message"))
            return

        try:
            editor = GeminiEditor(self.cfg["gemini_api_key"], self.cfg["gemini_model"])
        except GeminiEditError as exc:
            QMessageBox.critical(self, t("dialog.config_error_title"), str(exc))
            return

        self._pending_intensity = intensity
        self.ai_page.process_btn.setEnabled(False)
        self.statusBar().showMessage(t("status.ai_processing"))
        self._edit_worker = EditWorker(editor, self.selected_photo_path, style_key, extra)
        self._edit_worker.finished_ok.connect(self._on_ai_edit_ok)
        self._edit_worker.failed.connect(self._on_ai_edit_failed)
        self._edit_worker.start()

    def _on_ai_edit_ok(self, pil_image: Image.Image):
        self.ai_page.process_btn.setEnabled(True)
        self.statusBar().showMessage(t("status.ai_done"), 5000)
        self.ai_raw_result = pil_image
        self.ai_final_result = blend_with_original(self.original_image, pil_image, self._pending_intensity)
        self.ai_page.set_after_image(self.ai_final_result)

    def _on_ai_edit_failed(self, message: str):
        self.ai_page.process_btn.setEnabled(True)
        self.statusBar().clearMessage()
        QMessageBox.critical(self, t("dialog.ai_error_title"), message)

    def on_ai_save_clicked(self):
        if self.ai_final_result is None or not self.selected_photo_path:
            return
        self._save_result(self.ai_final_result, suffix="ai")

    # ------------------------------------------------------------------
    # Chinh tay
    # ------------------------------------------------------------------
    def on_manual_adjustments_changed(self, adj: ManualAdjustments):
        if self._manual_preview_source is None:
            return
        adj.rotation = self._manual_rotation
        preview_result = apply_adjustments(self._manual_preview_source, adj)
        self.manual_page.set_preview(preview_result)
        self._last_manual_adj = adj

    def on_manual_rotate(self, delta: int):
        self._manual_rotation = (self._manual_rotation + delta) % 360
        adj = getattr(self, "_last_manual_adj", ManualAdjustments())
        adj.rotation = self._manual_rotation
        self.on_manual_adjustments_changed(adj)

    def on_manual_reset(self):
        self._manual_rotation = 0

    def on_manual_save_clicked(self):
        if self.original_image is None or not self.selected_photo_path:
            return
        adj = getattr(self, "_last_manual_adj", ManualAdjustments())
        adj.rotation = self._manual_rotation
        full_result = apply_adjustments(self.original_image, adj)
        self.manual_result = full_result
        self._save_result(full_result, suffix="manual")

    # ------------------------------------------------------------------
    # Luu file dung chung
    # ------------------------------------------------------------------
    def _save_result(self, image: Image.Image, suffix: str):
        output_folder = Path(self.cfg["output_folder"])
        output_folder.mkdir(parents=True, exist_ok=True)
        src_name = Path(self.selected_photo_path).stem
        out_path = output_folder / f"{src_name}_{suffix}.jpg"
        image.convert("RGB").save(out_path, quality=95)
        QMessageBox.information(self, t("dialog.saved_title"), t("dialog.saved_message", path=out_path))

    # ------------------------------------------------------------------
    # Cai dat
    # ------------------------------------------------------------------
    def on_settings_saved(self, new_cfg: dict):
        self.cfg.update(new_cfg)
        save_config(self.cfg)
        self._init_camera()
        self.watcher.removePaths(self.watcher.directories())
        self.watcher.addPath(self.cfg["capture_folder"])
        self.library_page.refresh(self.cfg["capture_folder"])
        self.statusBar().showMessage(t("settings.saved_status"), 3000)

    def on_language_changed(self, lang_code: str):
        """Doi ngon ngu ngay trong app, khong can khoi dong lai."""
        set_language(lang_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(f"{APP_NAME} ({APP_VERSION})")
        self.nav.retranslate()
        self.library_page.retranslate()
        self.ai_page.retranslate()
        self.manual_page.retranslate()
        self.settings_page.retranslate()
        self.statusBar().showMessage(t("status.ready"))
