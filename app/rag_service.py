from pathlib import Path
from typing import Optional
import time
import hashlib
from pydantic import ValidationError

from .chunking import chunk_text
from .vector_store import InMemoryVectorStore
from .retriever import HybridRetriever
from .llm_client import call_llm, repair_json_if_needed
from .schemas import RAGAnswer
from .config import settings
from .metrics import METRICS
from .cache import TTLCache
from .logger import logger
from .canary import choose_variant

from .prompts import (
    RAG_PROMPT_STABLE,
    RAG_PROMPT_CANARY,
    PROMPT_VERSION_STABLE,
    PROMPT_VERSION_CANARY,
)


DOC_PATH = Path(__file__).resolve().parent / "data" / "docs.txt"


class RAGService:
    def __init__(self):
        self.store = InMemoryVectorStore()
        self.chunks: list[str] = []
        self.retriever: Optional[HybridRetriever] = None
        self.cache = TTLCache(ttl_seconds=300)

    def build_index(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.chunks = chunk_text(text)
        self.store.add_chunks(self.chunks, source="docs.txt")
        self.retriever = HybridRetriever(self.store, self.chunks)

    def ask(self, question: str, request_id: str = "-") -> RAGAnswer:
        if self.retriever is None:
            self.build_index()

        #  deterministik canary
        variant = choose_variant(request_id, canary_percent=settings.canary_percent)

        #  variant'e göre prompt seçimi
        if variant == "canary":
            prompt_tpl = RAG_PROMPT_CANARY
            prompt_version = PROMPT_VERSION_CANARY
        else:
            prompt_tpl = RAG_PROMPT_STABLE
            prompt_version = PROMPT_VERSION_STABLE


        llm_mode = "real" if settings.use_real_llm else "fake"
        cache_fingerprint = (
            f"{prompt_version}|llm={llm_mode}|topk={settings.top_k}|a={settings.alpha}|b={settings.beta}|ctx={settings.max_context_chars}"
        )
        raw_key = f"{question.strip().lower()}|{cache_fingerprint}"
        qkey = hashlib.md5(raw_key.encode("utf-8")).hexdigest()

        cached = self.cache.get(qkey)
        if cached:
            METRICS.requests_total += 1
            METRICS.cache_hits += 1

            if variant == "canary":
                METRICS.canary_requests += 1
            else:
                METRICS.stable_requests += 1

            cached.variant = variant

            logger.info(
                f"request_id={request_id} variant={variant} cache_hit=true question_hash={qkey} prompt_v={prompt_version}"
            )
            return cached

        # cache miss
        METRICS.requests_total += 1
        METRICS.cache_misses += 1
        if variant == "canary":
            METRICS.canary_requests += 1
        else:
            METRICS.stable_requests += 1

        t0 = time.time()

        hits = self.retriever.retrieve(question, top_k=settings.top_k)

        context = "\n\n".join([h["text"] for h in hits])[: settings.max_context_chars]
        prompt = prompt_tpl.format(context=context, question=question)

        # LLM çağrısı hata verirse sistem patlamasın
        try:
            raw = call_llm(prompt)
        except Exception as e:
            METRICS.errors_total += 1
            if variant == "canary":
                METRICS.canary_errors += 1
            else:
                METRICS.stable_errors += 1

            logger.exception(
                f"request_id={request_id} variant={variant} llm_call_failed=true err={type(e).__name__}"
            )

            latency_ms = int((time.time() - t0) * 1000)
            METRICS.last_latency_ms = latency_ms

            # LLM yoksa: retrieval-only fallback (200 dönsün)
            ans = RAGAnswer(
                answer="LLM is temporarily unavailable (quota/rate limit). Returning retrieval-only context.",
                confidence=0.0,
                sources=["docs.txt"],
                used_chunks=[h["id"] for h in hits],
                used_chunks_text=[h["text"] for h in hits],
                variant=variant,
            )
            return ans

        # JSON repair + validate
        try:
            fixed = repair_json_if_needed(raw)
            ans = RAGAnswer.model_validate_json(fixed)
        except (ValidationError, ValueError) as e:
            METRICS.errors_total += 1
            if variant == "canary":
                METRICS.canary_errors += 1
            else:
                METRICS.stable_errors += 1

            logger.info(
                f"request_id={request_id} variant={variant} json_parse_error=true err={type(e).__name__}"
            )
            ans = RAGAnswer(
                answer="I couldn't parse a structured response. Please try again.",
                confidence=0.0,
                sources=["docs.txt"],
                used_chunks=[],
                used_chunks_text=[],
            )

        # hangi chunklar kullanıldı
        ans.used_chunks = [h["id"] for h in hits]
        ans.used_chunks_text = [h["text"] for h in hits]

        ans.variant = variant

        latency_ms = int((time.time() - t0) * 1000)
        METRICS.last_latency_ms = latency_ms

        logger.info(
            f"request_id={request_id} variant={variant} cache_hit=false latency_ms={latency_ms} question_hash={qkey} prompt_v={prompt_version}"
        )

        # LLM başarılı olduysa cache'e yaz
        self.cache.set(qkey, ans)
        return ans
