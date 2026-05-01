"""Language detection and translation via langdetect + HuggingFace."""

from __future__ import annotations

import os

import httpx
from langdetect import LangDetectException, detect

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
_HF_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-V3"


def _get_headers() -> dict:
    return {"Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY', '')}"}


def detect_language(text: str) -> str:
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
    if source_lang == "en":
        return text
    lang_name = SUPPORTED_LANGUAGES.get(source_lang, source_lang)
    prompt = (
        f"Translate the following {lang_name} text to English.\n"
        "Return ONLY the translated text, no explanation, no preamble:\n\n"
        f"{text}"
    )
    try:
        return await _hf_translate(prompt)
    except Exception:  # noqa: BLE001
        return text


async def translate_from_english(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text

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
        translated_body = await _hf_translate(prompt)
        return translated_body + footer
    except Exception:  # noqa: BLE001
        return text + "\n[Translation unavailable]"


async def _hf_translate(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            _HF_URL,
            headers=_get_headers(),
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 256,
                    "return_full_text": False,
                },
            },
        )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "").strip()
        return str(result).strip()