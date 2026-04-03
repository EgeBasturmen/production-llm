PROMPT_VERSION_STABLE = "v1"
PROMPT_VERSION_CANARY = "v1c"

RAG_PROMPT_STABLE = """You are an assistant.
Answer ONLY using the context below. If the context is insufficient, say so.

Context:
{context}

Question:
{question}

Return ONLY valid JSON:
{{
  "answer": string,
  "confidence": number between 0 and 1,
  "sources": array of strings
}}
"""

# Canary prompt: daha sıkı, daha kısa, daha disiplinli
RAG_PROMPT_CANARY = """You are an assistant.
Use ONLY the context. Do NOT add external facts.
If context is insufficient, set answer to "Insufficient context." and confidence to 0.

Context:
{context}

Question:
{question}

Return ONLY valid JSON (no extra text):
{{
  "answer": string,
  "confidence": number between 0 and 1,
  "sources": array of strings
}}
"""
