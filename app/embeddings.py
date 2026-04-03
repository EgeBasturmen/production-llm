import hashlib
from typing import List
from .config import settings

def fake_embedding(text: str) -> List[float]:
    h = hashlib.md5(text.encode("utf-8")).hexdigest()  # 32 hex char
    # 16 boyutlu, 0-1 arası deterministik vektör
    return [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]

def embed(text: str) -> List[float]:
    if not settings.use_real_embeddings:
        return fake_embedding(text)

    # Real embedding (OpenAI) - API key şart
    from openai import OpenAI
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY missing but USE_REAL_EMBEDDINGS=true")

    client = OpenAI(api_key=settings.openai_api_key)
    resp = client.embeddings.create(
        model=settings.openai_embed_model,
        input=text
    )
    return resp.data[0].embedding