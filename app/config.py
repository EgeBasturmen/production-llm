from pydantic import BaseModel
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Optional

# ✅
ENV_PATH = Path(__file__).resolve().parent.parent / ".env.example"
load_dotenv(dotenv_path=ENV_PATH, override=True)

class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")

    # 🔥 LLM switch
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini | openai
    use_real_llm: bool = os.getenv("USE_REAL_LLM", "false").lower() == "true"
    use_real_embeddings: bool = os.getenv("USE_REAL_EMBEDDINGS", "false").lower() == "true"

    canary_percent: int = int(os.getenv("CANARY_PERCENT", "10"))

    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_chat_model_stable: str = os.getenv("OPENAI_CHAT_MODEL_STABLE", "gpt-4.1-mini")
    openai_embed_model: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

    #  Gemini
    google_api_key: Optional[str] = (
        os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    )
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "4"))
    alpha: float = float(os.getenv("HYBRID_ALPHA", "0.7"))
    beta: float = float(os.getenv("HYBRID_BETA", "0.3"))
    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", "4000"))

settings = Settings()

# 🔍 DEBUG
print("ENV_PATH:", ENV_PATH)
print("USE_REAL_LLM:", settings.use_real_llm)
print("LLM_PROVIDER:", settings.llm_provider)
print("GOOGLE_API_KEY set:", bool(settings.google_api_key))
