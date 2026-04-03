from .config import settings
from .keyword import BM25Index
from .vector_store import InMemoryVectorStore
from typing import Optional

def normalize(scores: list[float]) -> list[float]:
    if not scores:
        return scores
    mn, mx = min(scores), max(scores)
    if mx - mn < 1e-9:
        return [0.0 for _ in scores]
    return [(s - mn) / (mx - mn) for s in scores]

class HybridRetriever:
    def __init__(self, store: InMemoryVectorStore, chunks: list[str]):
        self.store = store
        self.bm25 = BM25Index(chunks)

    def retrieve(self, query: str, top_k: Optional[int] = None) -> list[dict]:
        top_k = top_k or settings.top_k

        # ham skorlar
        vec_raw = self.store.vector_scores(query)
        kw_raw = self.bm25.scores(query)

        # normalize (0-1)
        vec_scores = normalize(vec_raw)
        kw_scores = normalize(kw_raw)

        combined = []
        for i, item in enumerate(self.store.items):
            hybrid = settings.alpha * vec_scores[i] + settings.beta * kw_scores[i]
            combined.append((hybrid, i, item))

        combined.sort(key=lambda x: x[0], reverse=True)
        picks = combined[:top_k]

        results = []
        for hybrid, i, item in picks:
            results.append({
                "id": item.id,
                "source": item.source,
                "text": item.text,
                "vec_score": float(vec_scores[i]),
                "kw_score": float(kw_scores[i]),
                "hybrid_score": float(hybrid),
            })

        return results
