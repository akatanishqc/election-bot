"""Language detection and translation via langdetect + Gemini.

Translation calls count against the 1,000 RPD free tier limit.
Each non-English query consumes up to 2 extra LLM calls (query + response).
Monitor daily usage in Google AI Studio.
"""

from __future__ import annotations

import asyncio

import google.generativeai as genai
from langdetect import LangDetectException, detect

from ..dependencies import get_gemini_model

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "bn": "Bengali",
    "te": "Telugu",
    "ml": "Malayalam",
    "as": "Assamese",
}

_FALLBACK = "en"
_MIN_DETECT_LENGTH = 10


def detect_language(text: str) -> str:
    """
    Detects language using langdetect. Returns ISO 639-1 code.
    Falls back to 'en' if text is too short, language is unsupported, or on any error.
    """
    if len(text.strip()) < _MIN_DETECT_LENGTH:
        return _FALLBACK
    try:
        code = detect(text)
        return code if code in SUPPORTED_LANGUAGES else _FALLBACK
    except LangDetectException:
        return _FALLBACK
    except Exception:  # noqa: BLE001
        return _FALLBACK


async def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translates text to English. Returns unchanged text if already English.
    On any failure, returns original text (graceful degradation).
    """
    if source_lang == "en":
        return text

    lang_name = SUPPORTED_LANGUAGES.get(source_lang, source_lang)
    prompt = (
        f"Translate the following {lang_name} text to English.\n"
        "Return ONLY the translated text, no explanation, no preamble:\n\n"
        f"{text}"
    )
    try:
        return await _gemini_translate(prompt)
    except Exception:  # noqa: BLE001
        return text


async def translate_from_english(text: str, target_lang: str) -> str:
    """
    Translates an English response to the target language.
    - Preserves source citations (lines containing 'Source:') exactly.
    - Preserves the compliance footer ([AI-Generated] block) exactly.
    - Falls back to English + notice on any failure.
    """
    if target_lang == "en":
        return text

    # Split off the footer to protect it from translation
    footer_marker = "\n\n---\n"
    if footer_marker in text:
        body, footer = text.split(footer_marker, 1)
        footer = footer_marker + footer
    else:
        body, footer = text, ""

    lang_name = SUPPORTED_LANGUAGES.get(target_lang, target_lang)
    prompt = (
        f"Translate the following English text to {lang_name}.\n"
        "Rules:\n"
        "1. Return ONLY the translated text, no explanation.\n"
        "2. Preserve any lines that start with '(Source:' exactly as-is.\n"
        "3. Do not translate proper nouns like 'ECI', 'Form 6', 'EPIC'.\n\n"
        f"{body}"
    )
    try:
        translated_body = await _gemini_translate(prompt)
        return translated_body + footer
    except Exception:  # noqa: BLE001
        return text + "\n[Translation unavailable]"


async def _gemini_translate(prompt: str) -> str:
    """Runs a translation prompt through Gemini 2.5 Flash-Lite."""
    model = get_gemini_model()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: model.generate_content(prompt),
    )
    return response.text.strip()