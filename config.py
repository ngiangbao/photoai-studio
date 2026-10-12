"""
config.py - Cau hinh chung cho ung dung
"""
import os
import json
from pathlib import Path

APP_NAME = "PhotoAI Studio"
APP_VERSION = "alpha-001"

CONFIG_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "PhotoAIStudio"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "gemini_model": "gemini-2.5-flash-image",
    "digicam_cmd_path": r"C:\Program Files\digiCamControl\CameraControlCmd.exe",
    "capture_folder": str(Path.home() / "Pictures" / "PhotoAIStudio" / "RawCaptures"),
    "output_folder": str(Path.home() / "Pictures" / "PhotoAIStudio" / "Edited"),
}


def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(data)
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
