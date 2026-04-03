import json
from typing import Any, Dict

from google import genai
from google.genai import types

from .config import settings
from .logger import logger


def fake_llm(_: str) -> str:
    return json.dumps({
        "answer": "FAKE_LLM: This is a placeholder answer.",
        "confidence": 0.2,
        "sources": ["docs.txt"],
    })


def repair_json_if_needed(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()
    return raw


#  Gemini JSON Schema
RAG_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "sources": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["answer", "confidence", "sources"],
}


def call_llm(prompt: str) -> str:
    logger.info(
        f"llm_provider={settings.llm_provider} "
        f"llm_mode={'real' if settings.use_real_llm else 'fake'} "
        f"key_set={bool(settings.google_api_key)} "
        f"model={settings.gemini_model}"
    )

    if not settings.use_real_llm:
        return fake_llm(prompt)

    if settings.llm_provider != "gemini":
        raise RuntimeError("Only Gemini is enabled in this setup")

    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY missing but USE_REAL_LLM=true")

    client = genai.Client(api_key=settings.google_api_key)

    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=RAG_JSON_SCHEMA,
    )

    resp = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=cfg,
    )

    return repair_json_if_needed(resp.text)
