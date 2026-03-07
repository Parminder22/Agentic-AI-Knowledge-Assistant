from fastembed import TextEmbedding
from app.config import get_settings
from loguru import logger

settings = get_settings()

_model: TextEmbedding = None


def get_embedding_model() -> TextEmbedding:
    """Load model once, reuse forever (lazy load)."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        logger.info("Embedding model loaded ✓")
    return _model


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts locally. Returns list of vectors."""
    model = get_embedding_model()
    logger.info(f"Embedding {len(texts)} chunks locally...")
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]


async def embed_query(query: str) -> list[float]:
    """Embed a single query string locally."""
    model = get_embedding_model()
    embeddings = list(model.embed([query]))
    return embeddings[0].tolist()