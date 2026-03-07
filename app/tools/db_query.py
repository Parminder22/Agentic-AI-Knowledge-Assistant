from loguru import logger


async def get_document_stats(db) -> dict:
    """
    Tool: query the database for document/session stats.
    In a real app you'd run SQL here. This is a clean example.
    """
    from sqlalchemy import select, func
    from app.database.models import Document, Message, Session

    logger.info("[DB] Querying document stats")

    try:
        # Count documents
        doc_result = await db.execute(select(func.count()).select_from(Document))
        doc_count = doc_result.scalar()

        # Count sessions
        session_result = await db.execute(select(func.count()).select_from(Session))
        session_count = session_result.scalar()

        # Count messages
        msg_result = await db.execute(select(func.count()).select_from(Message))
        msg_count = msg_result.scalar()

        return {
            "tool": "db_query",
            "data": {
                "total_documents": doc_count,
                "total_sessions": session_count,
                "total_messages": msg_count,
            },
            "context": (
                f"System stats: {doc_count} documents uploaded, "
                f"{session_count} sessions, {msg_count} messages exchanged."
            ),
        }
    except Exception as e:
        logger.error(f"[DB] Query failed: {e}")
        return {"tool": "db_query", "error": str(e), "context": "Database query failed."}
