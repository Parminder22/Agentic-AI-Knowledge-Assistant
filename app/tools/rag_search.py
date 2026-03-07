from app.services.embedding_service import embed_query
from app.services.faiss_index import search_vectors
from app.config import get_settings
from loguru import logger

settings = get_settings()


async def search_docs(query: str, top_k: int = None) -> dict:
    """
    Tool: search uploaded documents using RAG.
    Returns relevant text chunks.
    """
    top_k = top_k or settings.top_k_results
    logger.info(f"[RAG] Searching: '{query}' (top_k={top_k})")

    query_vector = await embed_query(query)
    results = search_vectors(query_vector, top_k=top_k)

    if not results:
        return {
            "tool": "rag_search",
            "found": False,
            "results": [],
            "context": "No relevant documents found.",
        }

    # Build a readable context block for the LLM
    context_parts = []
    for i, r in enumerate(results):
        context_parts.append(f"[Source {i+1}: {r.get('source', 'unknown')}]\n{r['text']}")

    context = "\n\n---\n\n".join(context_parts)
    sources = list({r.get("source", "unknown") for r in results})

    logger.info(f"[RAG] Found {len(results)} chunks from {len(sources)} source(s)")

    return {
        "tool": "rag_search",
        "found": True,
        "results": results,
        "context": context,
        "sources": sources,
    }
