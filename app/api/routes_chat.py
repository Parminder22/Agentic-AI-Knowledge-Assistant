from fastapi import APIRouter, HTTPException
from app.schemas.request_models import ChatRequest
from app.schemas.response_models import ChatResponse
from app.agent.orchestrator import run_agent
from app.utils.helpers import generate_session_id
from loguru import logger
import uuid

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Agent decides whether to search docs, query DB, summarize, etc.
    """
    logger.info(f"[/chat] session={request.session_id} | msg='{request.message[:60]}'")

    try:
        result = await run_agent(
            session_id=request.session_id,
            user_message=request.message,
            user_id=request.user_id,
        )
    except Exception as e:
        logger.exception(f"Agent error: {e}")
        raise HTTPException(500, detail=f"Agent failed: {str(e)}")

    return ChatResponse(
        session_id=request.session_id,
        message_id=result["message_id"],
        answer=result["answer"],
        tool_used=result.get("tool_used"),
        sources=result.get("sources"),
    )
