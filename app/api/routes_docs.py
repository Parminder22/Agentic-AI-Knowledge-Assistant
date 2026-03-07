from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.response_models import UploadResponse
from app.ingestion.loader import load_document
from app.ingestion.cleaner import clean_text
from app.ingestion.chunker import chunk_text
from app.services.embedding_service import embed_texts
from app.services.faiss_index import add_vectors
from app.database.crud import save_document
from app.database.session import get_db
from app.config import get_settings
from loguru import logger
import uuid

router = APIRouter()
settings = get_settings()

ALLOWED_TYPES = {".pdf", ".txt", ".docx"}


@router.post("/upload_docs", response_model=UploadResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(None),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    # ── Validate ──────────────────────────────────────────────────────────
    filename = file.filename or "unknown"
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if suffix not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type '{suffix}' not supported. Use: {ALLOWED_TYPES}")

    content = await file.read()

    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(413, f"File too large. Max {settings.max_upload_size_mb}MB.")

    logger.info(f"Uploading: {filename} ({len(content)/1024:.1f}KB)")

    # ── Extract → Clean → Chunk ──────────────────────────────────────────
    raw_text = await load_document(content, filename)
    clean = clean_text(raw_text)
    chunks = chunk_text(clean)

    if not chunks:
        raise HTTPException(422, "Could not extract any text from this document.")

    logger.info(f"Created {len(chunks)} chunks from {filename}")

    # ── Embed → Store in FAISS ───────────────────────────────────────────
    vectors = await embed_texts(chunks)
    metadata = [
        {"text": chunk, "source": filename, "chunk_id": i}
        for i, chunk in enumerate(chunks)
    ]
    add_vectors(vectors, metadata)

    # ── Save to DB ────────────────────────────────────────────────────────
    doc = await save_document(
        db, filename=filename, chunks_count=len(chunks),
        session_id=session_id, description=description,
    )

    return UploadResponse(
        success=True,
        filename=filename,
        chunks_created=len(chunks),
        doc_id=doc.id,
        message=f"Document ingested successfully into {len(chunks)} searchable chunks.",
    )
