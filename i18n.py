"""
i18n.py - He thong da ngon ngu nhe (khong dung Qt Linguist .ts/.qm de don gian hoa build).
Ho tro Tieng Viet (mac dinh) va English, chuyen doi ngay trong app khong can khoi dong lai.
"""
import locale as _locale

LANG_VI = "vi"
LANG_EN = "en"
SUPPORTED_LANGUAGES = [LANG_VI, LANG_EN]

LANGUAGE_NAMES = {
    LANG_VI: "Tiếng Việt",
    LANG_EN: "English",
}

_current_language = LANG_VI

STRINGS = {
    # ---- Dieu huong ----
    "nav.library": {"vi": "Thư viện", "en": "Library"},
    "nav.ai": {"vi": "Chỉnh AI", "en": "AI Edit"},
    "nav.manual": {"vi": "Chỉnh tay", "en": "Manual"},
    "nav.settings": {"vi": "Cài đặt", "en": "Settings"},

    # ---- Trang Thu vien ----
    "library.title": {"vi": "Thư viện", "en": "Library"},
    "library.capture_button": {"vi": "📷  Chụp ảnh mới", "en": "📷  New Capture"},
    "library.empty_hint": {
        "vi": "Chưa có ảnh nào. Cắm máy ảnh qua USB rồi bấm \"Chụp ảnh mới\".",
        "en": "No photos yet. Connect your camera via USB and tap \"New Capture\".",
    },
    "library.multi_select_button": {"vi": "☑️  Chọn nhiều", "en": "☑️  Select Multiple"},
    "library.batch_button": {"vi": "🧵  Xử lý hàng loạt ({count})", "en": "🧵  Batch Process ({count})"},

    # ---- Trang Chinh AI ----
    "ai.title": {"vi": "Chỉnh sửa bằng AI", "en": "AI Edit"},
    "ai.compare_hint": {
        "vi": "Kéo thanh trắng để so sánh ảnh gốc / kết quả AI.",
        "en": "Drag the white handle to compare the original and the AI result.",
    },
    "ai.choose_style": {"vi": "Chọn phong cách", "en": "Choose a style"},
    "ai.intensity": {"vi": "Cường độ hiệu ứng", "en": "Effect intensity"},
    "ai.extra_placeholder": {
        "vi": "Ghi chú thêm cho AI (tuỳ chọn)...",
        "en": "Extra note for the AI (optional)...",
    },
    "ai.process_button": {"vi": "✨  Áp dụng AI", "en": "✨  Apply AI"},
    "ai.save_button": {"vi": "💾  Lưu ảnh", "en": "💾  Save Photo"},
    "ai.save_preset_button": {"vi": "⭐  Lưu làm preset", "en": "⭐  Save as Preset"},
    "ai.save_preset_dialog_title": {"vi": "Lưu preset mới", "en": "Save new preset"},
    "ai.save_preset_dialog_label": {"vi": "Đặt tên cho preset này:", "en": "Name this preset:"},
    "ai.preset_delete_action": {"vi": "🗑️  Xoá preset này", "en": "🗑️  Delete this preset"},
    "compare.no_image": {"vi": "Chưa có ảnh", "en": "No image yet"},
    "compare.after_label": {"vi": "AI", "en": "AI"},
    "compare.before_label": {"vi": "Gốc", "en": "Original"},

    # ---- Phong cach (nhan hien thi; prompt gui Gemini nam o ai/styles.py) ----
    "style.portrait": {"vi": "Chân dung", "en": "Portrait"},
    "style.outdoor": {"vi": "Ngoại cảnh", "en": "Outdoor"},
    "style.landscape": {"vi": "Phong cảnh", "en": "Landscape"},
    "style.people": {"vi": "Chụp người / đời thường", "en": "People / Candid"},
    "style.graduation": {"vi": "Chụp kỷ yếu", "en": "Graduation"},
    "style.cleanup": {"vi": "Xoá vật thể", "en": "Remove Object"},

    # ---- Xu ly hang loat (batch) ----
    "batch.progress_title": {"vi": "Đang xử lý hàng loạt", "en": "Batch processing"},
    "batch.progress_label": {"vi": "Đang xử lý ảnh {current}/{total}...", "en": "Processing photo {current}/{total}..."},
    "batch.done_title": {"vi": "Hoàn tất", "en": "Done"},
    "batch.done_message": {
        "vi": "Đã xử lý xong {success} ảnh thành công, {failed} ảnh lỗi. Ảnh đã lưu vào thư mục ảnh đã chỉnh.",
        "en": "Finished: {success} photos succeeded, {failed} failed. Results were saved to the output folder.",
    },

    # ---- Trang Chinh tay ----
    "manual.title": {"vi": "Chỉnh tay", "en": "Manual Edit"},
    "manual.no_image": {"vi": "Chưa chọn ảnh", "en": "No photo selected"},
    "manual.brightness": {"vi": "Độ sáng", "en": "Brightness"},
    "manual.contrast": {"vi": "Tương phản", "en": "Contrast"},
    "manual.saturation": {"vi": "Bão hoà", "en": "Saturation"},
    "manual.sharpness": {"vi": "Độ nét", "en": "Sharpness"},
    "manual.reset_button": {"vi": "Đặt lại", "en": "Reset"},
    "manual.save_button": {"vi": "💾  Lưu ảnh", "en": "💾  Save Photo"},
    "manual.white_balance_button": {"vi": "🌈  Cân bằng trắng", "en": "🌈  White Balance"},
    "manual.auto_adjust_button": {"vi": "✨  Tự động chỉnh", "en": "✨  Smart Auto"},

    # ---- Trang Cai dat ----
    "settings.title": {"vi": "Cài đặt", "en": "Settings"},
    "settings.api_key_label": {"vi": "Gemini API key", "en": "Gemini API key"},
    "settings.model_label": {"vi": "Model Gemini", "en": "Gemini model"},
    "settings.digicam_label": {"vi": "CameraControlCmd.exe", "en": "CameraControlCmd.exe"},
    "settings.capture_folder_label": {"vi": "Thư mục ảnh chụp", "en": "Capture folder"},
    "settings.output_folder_label": {"vi": "Thư mục ảnh đã chỉnh", "en": "Output folder"},
    "settings.language_label": {"vi": "Ngôn ngữ", "en": "Language"},
    "settings.browse_button": {"vi": "Chọn...", "en": "Browse..."},
    "settings.save_button": {"vi": "💾  Lưu cài đặt", "en": "💾  Save Settings"},
    "settings.version_label": {"vi": "{app_name} • phiên bản {app_version}", "en": "{app_name} • version {app_version}"},
    "settings.dialog_digicam_title": {"vi": "Chọn CameraControlCmd.exe", "en": "Select CameraControlCmd.exe"},
    "settings.dialog_capture_title": {"vi": "Chọn thư mục ảnh chụp", "en": "Select capture folder"},
    "settings.dialog_output_title": {"vi": "Chọn thư mục ảnh đã chỉnh", "en": "Select output folder"},
    "settings.saved_status": {"vi": "Đã lưu cài đặt.", "en": "Settings saved."},
    "settings.auto_update_checkbox": {
        "vi": "Tự động kiểm tra cập nhật khi mở ứng dụng",
        "en": "Automatically check for updates on startup",
    },
    "settings.check_update_button": {"vi": "🔄  Kiểm tra cập nhật", "en": "🔄  Check for Updates"},
    "settings.update_checking": {"vi": "Đang kiểm tra cập nhật...", "en": "Checking for updates..."},
    "settings.update_uptodate": {"vi": "Bạn đang dùng bản mới nhất ({version}).", "en": "You're on the latest version ({version})."},
    "settings.update_available": {"vi": "Có bản mới: {version}", "en": "New version available: {version}"},
    "settings.update_check_failed": {"vi": "Không kiểm tra được cập nhật.", "en": "Couldn't check for updates."},

    # ---- Trang thai chung ----
    "status.ready": {"vi": "Sẵn sàng.", "en": "Ready."},
    "status.capturing": {"vi": "Đang chụp ảnh từ máy ảnh...", "en": "Capturing photo from camera..."},
    "status.captured": {"vi": "Đã chụp: {name}", "en": "Captured: {name}"},
    "status.ai_processing": {"vi": "AI đang xử lý ảnh, vui lòng chờ...", "en": "AI is processing the photo, please wait..."},
    "status.ai_done": {"vi": "Xử lý xong.", "en": "Done."},

    # ---- Hop thoai / loi ----
    "dialog.missing_digicam_title": {"vi": "Thiếu digiCamControl", "en": "digiCamControl missing"},
    "dialog.missing_digicam_message": {
        "vi": "Không tìm thấy CameraControlCmd.exe. Vào Cài đặt để chỉnh đường dẫn, hoặc cài digiCamControl tại digicamcontrol.com.",
        "en": "CameraControlCmd.exe was not found. Go to Settings to fix the path, or install digiCamControl from digicamcontrol.com.",
    },
    "dialog.capture_error_title": {"vi": "Lỗi chụp ảnh", "en": "Capture error"},
    "dialog.no_photo_selected_title": {"vi": "Chưa chọn ảnh", "en": "No photo selected"},
    "dialog.no_photo_selected_message": {
        "vi": "Hãy chọn một ảnh ở Thư viện trước.",
        "en": "Please pick a photo from the Library first.",
    },
    "dialog.missing_api_key_title": {"vi": "Thiếu API key", "en": "API key missing"},
    "dialog.missing_api_key_message": {
        "vi": "Hãy vào Cài đặt để nhập Gemini API key.",
        "en": "Please go to Settings and enter your Gemini API key.",
    },
    "dialog.config_error_title": {"vi": "Lỗi cấu hình", "en": "Configuration error"},
    "dialog.ai_error_title": {"vi": "Lỗi xử lý AI", "en": "AI processing error"},
    "dialog.open_image_error_title": {"vi": "Lỗi mở ảnh", "en": "Error opening image"},
    "dialog.open_image_error_message": {"vi": "Không thể mở ảnh:\n{error}", "en": "Could not open the image:\n{error}"},
    "dialog.saved_title": {"vi": "Đã lưu", "en": "Saved"},
    "dialog.saved_message": {"vi": "Ảnh đã được lưu tại:\n{path}", "en": "Photo saved to:\n{path}"},

    # ---- Loi digiCamControl (camera/digicam.py) ----
    "error.digicam_not_found": {
        "vi": "Không tìm thấy CameraControlCmd.exe tại: {path}\nHãy cài digiCamControl (digicamcontrol.com) và kiểm tra lại đường dẫn trong Cài đặt.",
        "en": "CameraControlCmd.exe was not found at: {path}\nInstall digiCamControl (digicamcontrol.com) and check the path in Settings.",
    },
    "error.digicam_timeout": {"vi": "Hết thời gian chờ máy ảnh chụp ảnh.", "en": "Timed out waiting for the camera to capture."},
    "error.digicam_cannot_run": {"vi": "Không thể chạy digiCamControl: {error}", "en": "Could not run digiCamControl: {error}"},
    "error.digicam_capture_failed": {
        "vi": "Chụp ảnh thất bại. Kiểm tra: máy ảnh đã bật & kết nối USB chưa, digiCamControl có đang mở sẵn không (phải tắt cửa sổ chính trước).\nChi tiết: {detail}",
        "en": "Capture failed. Check: is the camera on and connected via USB, and is digiCamControl's main window open (it must be closed first).\nDetails: {detail}",
    },

    # ---- Loi Gemini (ai/gemini_editor.py) ----
    "error.gemini_missing_key": {"vi": "Chưa có Gemini API key. Vào Cài đặt để nhập key.", "en": "No Gemini API key set. Go to Settings to enter one."},
    "error.gemini_unknown_style": {"vi": "Không tìm thấy phong cách: {style_key}", "en": "Style not found: {style_key}"},
    "error.gemini_api_call": {"vi": "Lỗi khi gọi Gemini API: {error}", "en": "Error calling the Gemini API: {error}"},
    "error.gemini_no_candidates": {"vi": "Gemini không trả về kết quả nào.", "en": "Gemini returned no result."},
    "error.gemini_blocked": {"vi": "Nội dung ảnh bị chặn bởi bộ lọc an toàn của Gemini.", "en": "The image was blocked by Gemini's safety filter."},
    "error.gemini_no_content": {"vi": "Gemini không trả về nội dung ảnh.", "en": "Gemini returned no image content."},
    "error.gemini_no_image_data": {"vi": "Không tìm thấy dữ liệu ảnh trong phản hồi của Gemini.", "en": "No image data found in Gemini's response."},
    "gemini.extra_note_prefix": {"vi": "Yêu cầu thêm từ người dùng:", "en": "Additional user request:"},

    # ---- Tu dong cap nhat (updater.py) ----
    "update.uptodate_title": {"vi": "Đã là bản mới nhất", "en": "You're up to date"},
    "update.uptodate_message": {"vi": "Bạn đang dùng phiên bản mới nhất.", "en": "You're already running the latest version."},
    "update.check_error_title": {"vi": "Không kiểm tra được cập nhật", "en": "Couldn't check for updates"},
    "update.check_error_message": {
        "vi": "Không thể kết nối tới GitHub để kiểm tra bản mới.\nChi tiết: {error}",
        "en": "Couldn't reach GitHub to check for updates.\nDetails: {error}",
    },
    "update.available_title": {"vi": "Có bản cập nhật mới", "en": "An update is available"},
    "update.available_message": {
        "vi": "Có phiên bản mới {version} (bạn đang dùng {current}).\nBạn có muốn tải về và cài đặt ngay không?",
        "en": "Version {version} is available (you're on {current}).\nDownload and install it now?",
    },
    "update.no_installer_title": {"vi": "Không tìm thấy file cài đặt", "en": "No installer found"},
    "update.no_installer_message": {
        "vi": "Bản phát hành mới không có file .exe đính kèm. Xem chi tiết tại:\n{url}",
        "en": "The new release has no .exe file attached. See details at:\n{url}",
    },
    "update.download_title": {"vi": "Đang tải bản cập nhật", "en": "Downloading update"},
    "update.downloading": {"vi": "Đang tải bản cập nhật...", "en": "Downloading the update..."},
    "update.ready_title": {"vi": "Đã tải xong", "en": "Download complete"},
    "update.ready_message": {
        "vi": "Đã tải xong bản cập nhật. Ứng dụng sẽ đóng để bạn chạy trình cài đặt. Tiếp tục?",
        "en": "The update has been downloaded. The app will close so you can run the installer. Continue?",
    },
    "update.saved_for_later": {
        "vi": "Đã lưu trình cài đặt tại: {path}",
        "en": "Installer saved to: {path}",
    },
    "update.download_error_title": {"vi": "Lỗi tải bản cập nhật", "en": "Update download error"},
}


def set_language(lang: str) -> None:
    global _current_language
    if lang in SUPPORTED_LANGUAGES:
        _current_language = lang


def get_language() -> str:
    return _current_language


def detect_system_language() -> str:
    """Doan ngon ngu he thong luc dau tien chay app (khong luu, chi goi ichi 1 lan khi tao config)."""
    try:
        code, _ = _locale.getlocale()
        if not code:
            code = _locale.getdefaultlocale()[0]
    except Exception:
        code = None
    if code and code.lower().startswith("vi"):
        return LANG_VI
    if code and code.lower().startswith("en"):
        return LANG_EN
    return LANG_VI


def t(key: str, **kwargs) -> str:
    """Tra ve chuoi da dich theo ngon ngu hien tai. Neu thieu key, tra ve chinh key do (an toan)."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_language) or entry.get(LANG_VI) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
