from dataclasses import dataclass
from typing import List, Dict, Any
from .embeddings import embed
import math

def dot(a: List[float], b: List[float]) -> float:
    return sum(x*y for x, y in zip(a, b))

def norm(a: List[float]) -> float:
    return math.sqrt(sum(x*x for x in a)) or 1.0

def cosine(a: List[float], b: List[float]) -> float:
    return dot(a, b) / (norm(a) * norm(b))

@dataclass
class DocChunk:
    id: str
    text: str
    source: str
    vector: List[float]

class InMemoryVectorStore:
    def __init__(self):
        self.items: List[DocChunk] = []

    def add_chunks(self, chunks: list[str], source: str):
        for idx, ch in enumerate(chunks):
            v = embed(ch)
            self.items.append(DocChunk(
                id=f"{source}#{idx}",
                text=ch,
                source=source,
                vector=v
            ))

    def vector_scores(self, query: str) -> list[float]:
        qv = embed(query)
        return [cosine(qv, item.vector) for item in self.items]
