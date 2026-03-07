from app.database.crud import get_session_messages
from app.database.session import AsyncSessionLocal


async def build_message_history(session_id: str, max_messages: int = 10) -> list[dict]:
    """
    Load recent messages from DB and format for LLM context window.
    """
    async with AsyncSessionLocal() as db:
        messages = await get_session_messages(db, session_id)

    # Take last N messages to avoid context overflow
    recent = messages[-max_messages:]

    history = []
    for msg in recent:
        history.append({
            "role": msg.role,
            "content": msg.content,
        })
    return history
