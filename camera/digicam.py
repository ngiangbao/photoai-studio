"""
camera/digicam.py - Wrapper quanh digiCamControl (CameraControlCmd.exe) de chup anh
tethering tu may anh qua USB.

Yeu cau: da cai digiCamControl (https://digicamcontrol.com) va may anh duoc digiCamControl
ho tro (xem danh sach tai digicamcontrol.com -> Supported camera list).

QUAN TRONG: KHONG duoc mo cua so chinh cua digiCamControl cung luc voi app nay, vi
CameraControlCmd.exe khong hoat dong khi ung dung digiCamControl (GUI) dang chay.
"""
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from i18n import t


class DigiCamError(Exception):
    pass


class DigiCamController:
    def __init__(self, cmd_exe_path: str, capture_folder: str):
        self.cmd_exe_path = cmd_exe_path
        self.capture_folder = Path(capture_folder)
        self.capture_folder.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        return Path(self.cmd_exe_path).exists()

    def capture_photo(self, filename: Optional[str] = None, timeout: int = 20) -> Path:
        """Kich hoat may anh chup 1 tam va luu vao capture_folder. Tra ve duong dan file anh."""
        if not self.is_available():
            raise DigiCamError(t("error.digicam_not_found", path=self.cmd_exe_path))

        if not filename:
            filename = f"IMG_{datetime.now():%Y%m%d_%H%M%S}.jpg"
        target_path = self.capture_folder / filename

        cmd = [self.cmd_exe_path, "/filename", str(target_path), "/capture"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise DigiCamError(t("error.digicam_timeout")) from exc
        except OSError as exc:
            raise DigiCamError(t("error.digicam_cannot_run", error=exc)) from exc

        if result.returncode != 0 or not target_path.exists():
            detail = (result.stderr or result.stdout or "").strip()
            raise DigiCamError(t("error.digicam_capture_failed", detail=detail))

        return target_path
