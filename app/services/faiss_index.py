import os
import json
import numpy as np
import faiss
from loguru import logger
from app.config import get_settings

settings = get_settings()

_index: faiss.IndexFlatL2 = None
_metadata: list[dict] = []
_dimension: int = 384   # matches all-MiniLM-L6-v2


def _ensure_dir():
    os.makedirs(os.path.dirname(settings.faiss_index_path), exist_ok=True)


def get_index() -> faiss.IndexFlatL2:
    global _index
    if _index is None:
        _index = faiss.IndexFlatL2(_dimension)
        logger.info("Created fresh FAISS index")
    return _index


def add_vectors(vectors: list[list[float]], metadata: list[dict]):
    global _metadata
    index = get_index()
    matrix = np.array(vectors, dtype=np.float32)
    index.add(matrix)
    _metadata.extend(metadata)
    logger.info(f"Added {len(vectors)} vectors. Total: {index.ntotal}")
    _save()


def search_vectors(query_vector: list[float], top_k: int = 5) -> list[dict]:
    index = get_index()
    if index.ntotal == 0:
        return []
    q = np.array([query_vector], dtype=np.float32)
    distances, indices = index.search(q, min(top_k, index.ntotal))
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0:
            continue
        meta = _metadata[idx].copy()
        meta["score"] = float(dist)
        results.append(meta)
    return results


def _save():
    try:
        _ensure_dir()
        faiss.write_index(get_index(), settings.faiss_index_path)
        with open(settings.faiss_meta_path, "w") as f:
            json.dump(_metadata, f)
    except Exception as e:
        logger.warning(f"Could not save FAISS index: {e}")


def load_from_disk():
    global _index, _metadata
    try:
        if os.path.exists(settings.faiss_index_path):
            _index = faiss.read_index(settings.faiss_index_path)
            with open(settings.faiss_meta_path) as f:
                _metadata = json.load(f)
            logger.info(f"Loaded FAISS index with {_index.ntotal} vectors")
        else:
            logger.info("No existing FAISS index found, starting fresh")
    except Exception as e:
        logger.warning(f"Could not load FAISS index: {e}")


def index_stats() -> dict:
    return {"total_vectors": get_index().ntotal, "dimension": _dimension}