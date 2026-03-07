from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.response_models import HistoryResponse, HistoryMessage
from app.database.crud import get_session_messages
from app.database.session import get_db

router = APIRouter()


@router.get("/history/{session_id}", response_model=HistoryResponse, tags=["History"])
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    """Return full message history for a session."""
    messages = await get_session_messages(db, session_id)

    if not messages:
        raise HTTPException(404, detail=f"No history found for session '{session_id}'")

    history_msgs = [
        HistoryMessage(
            message_id=msg.id,
            role=msg.role,
            content=msg.content,
            tool_used=msg.tool_used,
            timestamp=msg.timestamp,
        )
        for msg in messages
    ]

    return HistoryResponse(
        session_id=session_id,
        messages=history_msgs,
        total=len(history_msgs),
    )
