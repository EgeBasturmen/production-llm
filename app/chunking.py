def chunk_text(text: str, chunk_size_words: int = 120) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size_words):
        chunk = " ".join(words[i:i + chunk_size_words]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks