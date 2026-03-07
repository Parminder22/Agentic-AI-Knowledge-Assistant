import io
from pathlib import Path
from loguru import logger


async def load_document(file_bytes: bytes, filename: str) -> str:
    """
    Extract raw text from uploaded file.
    Supports: .pdf, .txt, .docx
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".txt":
        return _load_txt(file_bytes)
    elif suffix == ".pdf":
        return _load_pdf(file_bytes)
    elif suffix == ".docx":
        return _load_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use .txt, .pdf, or .docx")


def _load_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore")


def _load_pdf(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages)
        logger.info(f"Extracted {len(pages)} PDF pages")
        return text
    except Exception as e:
        raise RuntimeError(f"PDF parsing failed: {e}")


def _load_docx(data: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        logger.info(f"Extracted {len(paragraphs)} DOCX paragraphs")
        return text
    except Exception as e:
        raise RuntimeError(f"DOCX parsing failed: {e}")
