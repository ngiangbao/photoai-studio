"""
config.py - Cau hinh chung cho ung dung
"""
import os
import json
from pathlib import Path

from i18n import LANG_VI, detect_system_language

APP_NAME = "PhotoAI Studio"
APP_VERSION = "alpha-005"

CONFIG_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "PhotoAIStudio"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "gemini_model": "gemini-2.5-flash-image",
    "digicam_cmd_path": r"C:\Program Files\digiCamControl\CameraControlCmd.exe",
    "capture_folder": str(Path.home() / "Pictures" / "PhotoAIStudio" / "RawCaptures"),
    "output_folder": str(Path.home() / "Pictures" / "PhotoAIStudio" / "Edited"),
    "language": LANG_VI,  # duoc ghi de bang ngon ngu he thong khi tao config lan dau, xem below
    "custom_presets": [],  # [{"name":..., "base_style":..., "intensity":0..1, "extra_note":...}]
    "auto_check_updates": True,  # tu dong kiem tra ban moi tren GitHub Releases khi mo app
}


def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            # DEFAULT_CONFIG.copy() la shallow copy: ep tao list rieng cho custom_presets
            # de tranh nhieu config dung chung 1 list object voi DEFAULT_CONFIG.
            merged["custom_presets"] = list(merged.get("custom_presets") or [])
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    # Lan dau chay app (chua co config.json): doan ngon ngu theo he thong
    first_run_cfg = DEFAULT_CONFIG.copy()
    first_run_cfg["language"] = detect_system_language()
    first_run_cfg["custom_presets"] = []
    save_config(first_run_cfg)
    return first_run_cfg


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
