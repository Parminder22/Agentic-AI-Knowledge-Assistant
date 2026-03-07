from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from app.database.models import Session, Message, Document, ToolLog
from datetime import datetime
import uuid


# ─── Sessions ─────────────────────────────────────────────────────────────────

async def get_or_create_session(db: AsyncSession, session_id: str, user_id: str = None) -> Session:
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        session = Session(id=session_id, user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
    return session


# ─── Messages ─────────────────────────────────────────────────────────────────

async def save_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    tool_used: str = None,
) -> Message:
    msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        role=role,
        content=content,
        tool_used=tool_used,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_session_messages(db: AsyncSession, session_id: str) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.timestamp)
    )
    return result.scalars().all()


# ─── Documents ────────────────────────────────────────────────────────────────

async def save_document(
    db: AsyncSession,
    filename: str,
    chunks_count: int,
    session_id: str = None,
    description: str = None,
) -> Document:
    doc = Document(
        id=str(uuid.uuid4()),
        filename=filename,
        chunks_count=chunks_count,
        session_id=session_id,
        description=description,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


# ─── Tool Logs ────────────────────────────────────────────────────────────────

async def log_tool_call(
    db: AsyncSession,
    session_id: str,
    tool_name: str,
    input_data: dict,
    output_summary: str,
    duration_ms: int,
    message_id: str = None,
) -> ToolLog:
    log = ToolLog(
        id=str(uuid.uuid4()),
        session_id=session_id,
        message_id=message_id,
        tool_name=tool_name,
        input_data=input_data,
        output_summary=output_summary,
        duration_ms=duration_ms,
    )
    db.add(log)
    await db.commit()
    return log
