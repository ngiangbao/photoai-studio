"""
ai/gemini_editor.py - Goi Gemini API de chinh sua anh theo phong cach da chon
"""
from io import BytesIO
from pathlib import Path

from google import genai
from PIL import Image

from .styles import STYLES_BY_KEY


class GeminiEditError(Exception):
    pass


class GeminiEditor:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image"):
        if not api_key:
            raise GeminiEditError("Chua co Gemini API key. Vao Cai dat de nhap key.")
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def edit_image(self, image_path: str, style_key: str, extra_instruction: str = "") -> Image.Image:
        """Gui anh + prompt theo phong cach toi Gemini va tra ve anh da chinh sua (PIL Image)."""
        style = STYLES_BY_KEY.get(style_key)
        if style is None:
            raise GeminiEditError(f"Khong tim thay phong cach: {style_key}")

        prompt = style.prompt
        if extra_instruction.strip():
            prompt += f"\n\nYeu cau them tu nguoi dung: {extra_instruction.strip()}"

        source_image = Image.open(image_path)
        source_image.thumbnail((2048, 2048))

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[prompt, source_image],
            )
        except Exception as exc:
            raise GeminiEditError(f"Loi khi goi Gemini API: {exc}") from exc

        if not response.candidates:
            raise GeminiEditError("Gemini khong tra ve ket qua nao.")

        finish_reason = getattr(response.candidates[0], "finish_reason", None)
        if finish_reason is not None and getattr(finish_reason, "name", "") == "PROHIBITED_CONTENT":
            raise GeminiEditError("Noi dung anh bi chan boi bo loc an toan cua Gemini.")

        content = response.candidates[0].content
        if content is None:
            raise GeminiEditError("Gemini khong tra ve noi dung anh.")

        for part in content.parts:
            if getattr(part, "inline_data", None) is not None:
                return Image.open(BytesIO(part.inline_data.data))

        raise GeminiEditError("Khong tim thay du lieu anh trong phan hoi cua Gemini.")

    def save_result(self, image: Image.Image, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(output_path, quality=95)
