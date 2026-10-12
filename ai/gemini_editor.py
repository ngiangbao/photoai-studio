"""
ai/gemini_editor.py - Goi Gemini API de chinh sua anh theo phong cach da chon
"""
from io import BytesIO
from pathlib import Path

from google import genai
from PIL import Image

from .styles import STYLES_BY_KEY
from i18n import t


class GeminiEditError(Exception):
    pass


class GeminiEditor:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image"):
        if not api_key:
            raise GeminiEditError(t("error.gemini_missing_key"))
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def edit_image(self, image_path: str, style_key: str, extra_instruction: str = "") -> Image.Image:
        """Gui anh + prompt theo phong cach toi Gemini va tra ve anh da chinh sua (PIL Image)."""
        style = STYLES_BY_KEY.get(style_key)
        if style is None:
            raise GeminiEditError(t("error.gemini_unknown_style", style_key=style_key))

        prompt = style.prompt
        if extra_instruction.strip():
            prompt += f"\n\n{t('gemini.extra_note_prefix')} {extra_instruction.strip()}"

        source_image = Image.open(image_path)
        source_image.thumbnail((2048, 2048))

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[prompt, source_image],
            )
        except Exception as exc:
            raise GeminiEditError(t("error.gemini_api_call", error=exc)) from exc

        if not response.candidates:
            raise GeminiEditError(t("error.gemini_no_candidates"))

        finish_reason = getattr(response.candidates[0], "finish_reason", None)
        if finish_reason is not None and getattr(finish_reason, "name", "") == "PROHIBITED_CONTENT":
            raise GeminiEditError(t("error.gemini_blocked"))

        content = response.candidates[0].content
        if content is None:
            raise GeminiEditError(t("error.gemini_no_content"))

        for part in content.parts:
            if getattr(part, "inline_data", None) is not None:
                return Image.open(BytesIO(part.inline_data.data))

        raise GeminiEditError(t("error.gemini_no_image_data"))

    def save_result(self, image: Image.Image, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(output_path, quality=95)
