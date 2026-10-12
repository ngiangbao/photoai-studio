"""
ai/styles.py - Danh sach cac phong cach chinh sua + prompt song ngu (vi/en) gui cho Gemini.
Nhan hien thi (label) lay tu i18n.py (key style.<key>); file nay chi giu prompt ky thuat.
"""
from dataclasses import dataclass, field

from i18n import t, get_language, LANG_VI, LANG_EN


@dataclass(frozen=True)
class EditStyle:
    key: str
    prompts: dict = field(default_factory=dict)  # {"vi": "...", "en": "..."}

    @property
    def label(self) -> str:
        return t(f"style.{self.key}")

    @property
    def prompt(self) -> str:
        lang = get_language()
        return self.prompts.get(lang) or self.prompts.get(LANG_VI, "")


STYLES = [
    EditStyle(
        key="portrait",
        prompts={
            LANG_VI: (
                "Hãy chỉnh sửa ảnh chân dung này một cách chuyên nghiệp: làm mịn da tự nhiên "
                "(không làm mất kết cấu da thật), cân bằng tông màu da, làm nổi bật đôi mắt, "
                "tăng nhẹ độ sắc nét ở khuôn mặt, làm mờ nhẹ hậu cảnh theo kiểu chụp ống kính "
                "khẩu độ lớn (bokeh) nếu phù hợp, ánh sáng ấm và dễ chịu. Giữ nguyên danh tính "
                "và đặc điểm khuôn mặt của người trong ảnh, không thay đổi cấu trúc gương mặt."
            ),
            LANG_EN: (
                "Professionally retouch this portrait photo: smooth the skin naturally "
                "(without losing real skin texture), even out skin tone, make the eyes stand "
                "out, slightly sharpen the face, add a soft background blur (bokeh) if "
                "appropriate, warm and pleasant lighting. Keep the person's identity and facial "
                "features unchanged — do not alter face structure."
            ),
        },
    ),
    EditStyle(
        key="outdoor",
        prompts={
            LANG_VI: (
                "Hãy chỉnh sửa ảnh chụp ngoại cảnh này: cân bằng sáng/tối tự nhiên, tăng nhẹ độ "
                "rực rỡ của bầu trời và cây cối một cách chân thực (không quá đà), điều chỉnh "
                "cân bằng trắng cho đúng với ánh sáng tự nhiên, tạo cảm giác điện ảnh nhẹ nhàng "
                "nhưng vẫn tự nhiên, giữ nguyên bố cục và chủ thể trong ảnh."
            ),
            LANG_EN: (
                "Edit this outdoor/location photo: balance light and shadow naturally, "
                "slightly boost the vibrance of the sky and foliage realistically (not "
                "overdone), correct white balance for natural daylight, give it a subtle "
                "cinematic feel while staying natural, keep the composition and subject "
                "unchanged."
            ),
        },
    ),
    EditStyle(
        key="landscape",
        prompts={
            LANG_VI: (
                "Hãy chỉnh sửa ảnh phong cảnh này theo phong cách nhiếp ảnh thiên nhiên chuyên "
                "nghiệp: tăng dải tương phản động (dynamic range), làm bầu trời và mây rõ nét "
                "hơn, tăng độ sâu màu sắc một cách chân thực, làm nổi bật chi tiết ở tiền cảnh "
                "và hậu cảnh, sắc nét vừa phải, không chỉnh sửa quá mức làm mất tính tự nhiên."
            ),
            LANG_EN: (
                "Edit this landscape photo in a professional nature-photography style: "
                "increase dynamic range, make the sky and clouds crisper, deepen color "
                "realistically, bring out foreground and background detail, moderate "
                "sharpening, without over-editing to the point of looking unnatural."
            ),
        },
    ),
    EditStyle(
        key="people",
        prompts={
            LANG_VI: (
                "Hãy chỉnh sửa ảnh chụp người này theo phong cách tự nhiên, đời thường: cân "
                "bằng màu da chuẩn với nhiều người trong ảnh, chỉnh sáng đều, giữ màu sắc trung "
                "thực, làm sạch nhẹ các chi tiết gây xao nhãng ở hậu cảnh nếu có, giữ nguyên "
                "biểu cảm và dáng đứng tự nhiên của mọi người."
            ),
            LANG_EN: (
                "Edit this people/candid photo in a natural, everyday style: even out skin "
                "tones across multiple people, balance lighting, keep colors true to life, "
                "lightly clean up distracting background details if any, keep everyone's "
                "natural expressions and poses unchanged."
            ),
        },
    ),
    EditStyle(
        key="graduation",
        prompts={
            LANG_VI: (
                "Hãy chỉnh sửa ảnh kỷ yếu/tốt nghiệp này: tông màu tươi sáng, rực rỡ, vui tươi, "
                "đồng nhất về tông màu để phù hợp khi ghép chung với các ảnh kỷ yếu khác, làm "
                "nổi bật nụ cười và ánh sáng trên khuôn mặt, màu sắc đồng phục/áo cử nhân rõ "
                "nét, có thể thêm chút vignette nhẹ ở viền ảnh cho nổi bật chủ thể."
            ),
            LANG_EN: (
                "Edit this graduation/yearbook photo: bright, vivid, cheerful tones, "
                "consistent color grading so it matches other yearbook photos, make smiles "
                "and facial lighting stand out, crisp colors on uniforms/gowns, a subtle "
                "vignette at the edges is fine to draw focus to the subject."
            ),
        },
    ),
    EditStyle(
        key="cleanup",
        prompts={
            LANG_VI: (
                "Hãy loại bỏ người lạ, vật thể hoặc chi tiết gây xao nhãng ở hậu cảnh của ảnh "
                "này, sau đó phục hồi (inpaint) lại phần hậu cảnh một cách tự nhiên và liền "
                "mạch, không để lại viền lạ, vết mờ hay hoa văn lặp lại bất thường. Giữ nguyên "
                "hoàn toàn chủ thể chính, bố cục, màu sắc và ánh sáng tổng thể của ảnh. Nếu "
                "người dùng có ghi chú thêm mô tả cụ thể vật/người cần xoá, hãy ưu tiên xoá "
                "đúng đối tượng đó."
            ),
            LANG_EN: (
                "Remove any distracting strangers, objects, or background clutter from this "
                "photo, then inpaint the background naturally and seamlessly, with no stray "
                "edges, blur artifacts, or repeating patterns. Keep the main subject, "
                "composition, colors, and overall lighting completely unchanged. If the user "
                "gives an extra note describing a specific object or person to remove, "
                "prioritize removing exactly that."
            ),
        },
    ),
]

STYLES_BY_KEY = {s.key: s for s in STYLES}
