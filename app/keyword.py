from rank_bm25 import BM25Okapi

def tokenize(text: str) -> list[str]:
    return [t.lower() for t in text.split() if t.strip()]

class BM25Index:
    def __init__(self, chunks: list[str]):
        self.chunks = chunks
        self.corpus = [tokenize(c) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus)

    def scores(self, query: str) -> list[float]:
        q = tokenize(query)
        return list(self.bm25.get_scores(q))
