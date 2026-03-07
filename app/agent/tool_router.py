from loguru import logger
from app.tools.rag_search import search_docs
from app.tools.db_query import get_document_stats
from app.tools.summarizer import summarize_text
from app.tools.email_writer import write_email


async def route_tool(tool_name: str, query: str, db=None) -> dict:
    """
    Dispatch to the correct tool based on agent decision.
    Returns a standardized result dict.
    """
    logger.info(f"[ToolRouter] Routing to: {tool_name} | query: '{query[:80]}'")

    if tool_name == "rag_search":
        return await search_docs(query)

    elif tool_name == "db_query":
        if db is None:
            return {"tool": "db_query", "context": "No database connection available."}
        return await get_document_stats(db)

    elif tool_name == "summarizer":
        return await summarize_text(query)

    elif tool_name == "email_writer":
        return await write_email(topic=query)

    elif tool_name == "direct_answer":
        return {"tool": "direct_answer", "context": None}  # LLM answers directly

    else:
        logger.warning(f"[ToolRouter] Unknown tool: {tool_name}, falling back to direct_answer")
        return {"tool": "direct_answer", "context": None}
