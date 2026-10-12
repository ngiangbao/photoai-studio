"""
ai/one_tap.py - Cac cong cu "1 cham" xu ly cuc bo (khong goi AI, khong them dependency
ngoai Pillow): can bang trang kieu gray-world, tu dong can sang/mau/tuong phan.
Lay cam hung tu cac nut "mot cham" cua 醒图 (XingTu) ban desktop.
"""
from PIL import Image, ImageStat, ImageOps, ImageEnhance


def auto_white_balance(image: Image.Image) -> Image.Image:
    """Can bang trang kieu 'gray world': dua trung binh 3 kenh mau ve gan nhau de
    khu sac anh bi lech mau (vi du vang do den flash, xanh do bong cay)."""
    rgb = image.convert("RGB")
    r_mean, g_mean, b_mean = ImageStat.Stat(rgb).mean
    gray = (r_mean + g_mean + b_mean) / 3.0

    def _factor(mean_val: float) -> float:
        if mean_val <= 1:
            return 1.0
        # Gioi han he so de tranh chinh qua tay gay anh bi ngả mau la.
        return max(0.7, min(1.4, gray / mean_val))

    r_factor, g_factor, b_factor = _factor(r_mean), _factor(g_mean), _factor(b_mean)
    r, g, b = rgb.split()
    r = r.point(lambda v, f=r_factor: min(255, round(v * f)))
    g = g.point(lambda v, f=g_factor: min(255, round(v * f)))
    b = b.point(lambda v, f=b_factor: min(255, round(v * f)))
    return Image.merge("RGB", (r, g, b))


def smart_auto_adjust(image: Image.Image) -> Image.Image:
    """Tu dong keo dai dai sang (autocontrast) + tang nhe do rang va tuong phan de
    anh ro net, sinh dong hon ma van tu nhien."""
    rgb = image.convert("RGB")
    result = ImageOps.autocontrast(rgb, cutoff=1)
    result = ImageEnhance.Color(result).enhance(1.12)
    result = ImageEnhance.Contrast(result).enhance(1.05)
    return result
