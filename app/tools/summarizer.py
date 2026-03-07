from app.services.llm_service import chat_completion
from loguru import logger


async def summarize_text(text: str, instruction: str = "Summarize this clearly and concisely.") -> dict:
    """
    Tool: summarize a block of text using LLM.
    """
    logger.info(f"[Summarizer] Summarizing {len(text)} characters")

    messages = [
        {
            "role": "system",
            "content": "You are a concise summarization assistant. Extract key points clearly.",
        },
        {
            "role": "user",
            "content": f"{instruction}\n\nText:\n{text[:6000]}",  # safety truncation
        },
    ]

    response = await chat_completion(messages, temperature=0.2, max_tokens=800)
    summary = response.choices[0].message.content

    return {
        "tool": "summarizer",
        "summary": summary,
        "context": summary,
    }
