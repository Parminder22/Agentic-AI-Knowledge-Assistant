import json
import time
import uuid
from loguru import logger

from app.agent.prompts import SYSTEM_PROMPT, TOOL_DECISION_PROMPT
from app.agent.state_manager import build_message_history
from app.agent.tool_router import route_tool
from app.services.llm_service import chat_completion
from app.database.crud import save_message, log_tool_call, get_or_create_session
from app.database.session import AsyncSessionLocal


async def run_agent(session_id: str, user_message: str, user_id: str = None) -> dict:
    start_time = time.time()
    message_id = str(uuid.uuid4())

    # ── Step 1: Ensure session exists & save user message ──────────────────
    async with AsyncSessionLocal() as db:
        await get_or_create_session(db, session_id, user_id)
        await save_message(db, session_id, "user", user_message)

    # ── Step 2: Load conversation history ─────────────────────────────────
    history = await build_message_history(session_id)
    logger.info(f"[Orchestrator] Session {session_id} | {len(history)} history msgs")

    # ── Step 3: Ask LLM which tool to use ─────────────────────────────────
    tool_decision = await _decide_tool(user_message, history)
    tool_name = tool_decision.get("tool", "direct_answer")
    tool_query = tool_decision.get("query", user_message)
    logger.info(f"[Orchestrator] Tool chosen: {tool_name}")

    # ── Step 4: Execute tool (with RAG-first pipeline for summarizer) ──────
    tool_start = time.time()
    async with AsyncSessionLocal() as db:
        # If agent chose summarizer but query is about documents,
        # first retrieve the actual content via RAG, then summarize it
        if tool_name == "summarizer":
            rag_result = await route_tool("rag_search", tool_query, db=db)
            if rag_result.get("found") and rag_result.get("context"):
                # We have real content — now summarize it
                from app.tools.summarizer import summarize_text
                tool_result = await summarize_text(
                    text=rag_result["context"],
                    instruction=f"Summarize this content based on the user's request: {user_message}"
                )
                tool_result["sources"] = rag_result.get("sources")
                logger.info("[Orchestrator] RAG→Summarizer pipeline used")
            else:
                # No docs found, fall back to direct answer
                tool_name = "direct_answer"
                tool_result = {"tool": "direct_answer", "context": None}
        else:
            tool_result = await route_tool(tool_name, tool_query, db=db)

    tool_duration_ms = int((time.time() - tool_start) * 1000)

    # ── Step 5: Generate final answer ─────────────────────────────────────
    answer = await _generate_answer(
        user_message=user_message,
        history=history,
        tool_name=tool_name,
        tool_result=tool_result,
    )

    # ── Step 6: Save assistant message + tool log ─────────────────────────
    async with AsyncSessionLocal() as db:
        await save_message(db, session_id, "assistant", answer, tool_used=tool_name)
        await log_tool_call(
            db=db,
            session_id=session_id,
            message_id=message_id,
            tool_name=tool_name,
            input_data={"query": tool_query},
            output_summary=str(tool_result.get("context", ""))[:500],
            duration_ms=tool_duration_ms,
        )

    total_ms = int((time.time() - start_time) * 1000)
    logger.info(f"[Orchestrator] Done in {total_ms}ms | tool={tool_name}")

    return {
        "message_id": message_id,
        "answer": answer,
        "tool_used": tool_name if tool_name != "direct_answer" else None,
        "sources": tool_result.get("sources"),
    }


async def _decide_tool(user_message: str, history: list[dict]) -> dict:
    decision_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history[-4:],
        {
            "role": "user",
            "content": TOOL_DECISION_PROMPT.format(message=user_message),
        },
    ]

    try:
        response = await chat_completion(decision_messages, temperature=0.0, max_tokens=150)
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"Tool decision parse failed: {e}. Defaulting to direct_answer.")
        return {"tool": "direct_answer", "reason": "parse error", "query": user_message}


async def _generate_answer(
    user_message: str,
    history: list[dict],
    tool_name: str,
    tool_result: dict,
) -> str:
    context = tool_result.get("context")

    system_content = SYSTEM_PROMPT
    if context:
        system_content += f"\n\n--- Tool Result ({tool_name}) ---\n{context}"

    messages = [
        {"role": "system", "content": system_content},
        *history[-6:],
        {"role": "user", "content": user_message},
    ]

    response = await chat_completion(messages, temperature=0.3, max_tokens=1000)
    return response.choices[0].message.content