from app.config import get_settings

settings = get_settings()


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    """
    Split text into overlapping chunks by word count.
    This is simple and effective — no external library needed.
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap  # slide window with overlap

    return chunks
