"""
ai/manual_edit.py - Cac phep chinh tay (khong dung AI): sang, tuong phan, bao hoa, do net, xoay.
"""
from dataclasses import dataclass

from PIL import Image, ImageEnhance


@dataclass
class ManualAdjustments:
    brightness: float = 1.0   # 1.0 = khong doi
    contrast: float = 1.0
    saturation: float = 1.0
    sharpness: float = 1.0
    rotation: int = 0          # boi so cua 90, cong don

    def is_identity(self) -> bool:
        return (
            self.brightness == 1.0
            and self.contrast == 1.0
            and self.saturation == 1.0
            and self.sharpness == 1.0
            and self.rotation % 360 == 0
        )


def apply_adjustments(image: Image.Image, adj: ManualAdjustments) -> Image.Image:
    """Ap dung cac phep chinh tay len anh goc, tra ve anh moi (khong sua anh goc)."""
    result = image.copy()

    if adj.rotation % 360 != 0:
        result = result.rotate(-adj.rotation, expand=True)

    if adj.brightness != 1.0:
        result = ImageEnhance.Brightness(result).enhance(adj.brightness)
    if adj.contrast != 1.0:
        result = ImageEnhance.Contrast(result).enhance(adj.contrast)
    if adj.saturation != 1.0:
        result = ImageEnhance.Color(result).enhance(adj.saturation)
    if adj.sharpness != 1.0:
        result = ImageEnhance.Sharpness(result).enhance(adj.sharpness)

    return result


def blend_with_original(original: Image.Image, edited: Image.Image, intensity: float) -> Image.Image:
    """Tron anh da chinh AI voi anh goc theo cuong do (0.0 = giu anh goc, 1.0 = anh AI 100%)."""
    intensity = max(0.0, min(1.0, intensity))
    base = original.convert("RGB")
    edit = edited.convert("RGB")
    if edit.size != base.size:
        edit = edit.resize(base.size)
    return Image.blend(base, edit, intensity)
