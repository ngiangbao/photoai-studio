"""
updater.py - Tu dong kiem tra & tai ban cap nhat moi tu GitHub Releases cua repo
ngiangbao/photoai-studio. Khong dung thu vien ngoai (chi urllib chuan cua Python) de
khong lam nang them installer.

Luong su dung (xem ui/main_window.py):
    1. check_for_update(APP_VERSION) -> dict thong tin ban moi, hoac None neu dang moi nhat.
    2. Nguoi dung xac nhan -> download_installer(asset_url, dest_path).
    3. Mo file .exe vua tai (subprocess) -> dong ung dung hien tai de nguoi dung cai de.
"""
import json
import re
from pathlib import Path
from typing import Callable, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

GITHUB_REPO = "ngiangbao/photoai-studio"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"

_REQUEST_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "PhotoAIStudio-Updater",
}


class UpdateCheckError(Exception):
    """Khong goi duoc GitHub Releases API (mang, timeout, rate limit, phan hoi la)."""


def _version_tuple(version: str) -> tuple:
    """Chuyen chuoi phien ban dang 'alpha-003' thanh (0, 3) de so sanh thu tu.
    Chi lay so o cuoi chuoi; neu khong doc duoc thi coi nhu phien ban thap nhat (0, 0),
    de tranh bao nham la 'co ban moi' khi khong chac chan."""
    match = re.search(r"(\d+)\s*$", version.strip())
    if not match:
        return (0, 0)
    return (0, int(match.group(1)))


def is_newer(remote_version: str, current_version: str) -> bool:
    """True neu remote_version moi hon current_version theo quy uoc 'alpha-NNN'."""
    return _version_tuple(remote_version) > _version_tuple(current_version)


def check_for_update(current_version: str, timeout: int = 10) -> Optional[dict]:
    """Goi GitHub Releases API (endpoint /releases/latest).

    Tra ve None neu ban hien tai da la moi nhat (hoac moi hon ban release tren GitHub).
    Tra ve dict {"version", "notes_url", "body", "asset_url", "asset_name"} neu co ban moi.
    Nem UpdateCheckError neu khong kiem tra duoc (mang loi, API tra loi, v.v.) - noi goi
    nen bat loi nay va im lang bo qua khi kiem tra tu dong, chi bao loi khi nguoi dung
    bam kiem tra thu cong.
    """
    request = Request(RELEASES_API_URL, headers=_REQUEST_HEADERS)
    try:
        with urlopen(request, timeout=timeout) as resp:
            raw = resp.read()
    except (URLError, OSError, TimeoutError) as exc:
        raise UpdateCheckError(str(exc)) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise UpdateCheckError(str(exc)) from exc

    remote_version = str(data.get("tag_name") or data.get("name") or "").strip()
    if not remote_version:
        raise UpdateCheckError("Phan hoi GitHub Releases khong co tag_name/name")

    if not is_newer(remote_version, current_version):
        return None

    asset_url = None
    asset_name = None
    for asset in data.get("assets", []) or []:
        name = asset.get("name", "")
        if name.lower().endswith(".exe"):
            asset_url = asset.get("browser_download_url")
            asset_name = name
            break

    return {
        "version": remote_version,
        "notes_url": data.get("html_url") or RELEASES_PAGE_URL,
        "body": data.get("body") or "",
        "asset_url": asset_url,
        "asset_name": asset_name or f"PhotoAIStudio-Setup-{remote_version}.exe",
    }


def download_installer(
    asset_url: str,
    dest_path: Path,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    timeout: int = 30,
) -> Path:
    """Tai file installer (.exe) ve dest_path. Goi progress_callback(da_tai, tong_so_byte)
    sau moi khoi du lieu nhan duoc (tong_so_byte = 0 neu server khong tra Content-Length)."""
    request = Request(asset_url, headers=_REQUEST_HEADERS)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(request, timeout=timeout) as resp:
        try:
            total = int(resp.headers.get("Content-Length", 0) or 0)
        except (TypeError, ValueError):
            total = 0
        downloaded = 0
        chunk_size = 256 * 1024
        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback is not None:
                    progress_callback(downloaded, total)

    return dest_path
