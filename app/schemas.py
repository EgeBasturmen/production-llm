from pydantic import BaseModel, Field
from typing import List

class AskRequest(BaseModel):
    question: str = Field(min_length=1)

class RAGAnswer(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    sources: List[str]
    used_chunks: List[str] = Field(default_factory=list)
    used_chunks_text: List[str] = Field(default_factory=list)
    variant: str = "stable"


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=20)


class RetrievedChunk(BaseModel):
    id: str
    source: str
    text: str
    vec_score: float = Field(ge=0, le=1)
    kw_score: float = Field(ge=0, le=1)
    hybrid_score: float = Field(ge=0, le=1)


class RetrieveResponse(BaseModel):
    query: str
    top_k: int
    chunks: List[RetrievedChunk]
