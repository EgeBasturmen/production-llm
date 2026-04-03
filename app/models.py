from pydantic import BaseModel, Field
from typing import List

class RAGAnswer(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    sources: List[str]


