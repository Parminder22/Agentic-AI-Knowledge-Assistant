from app.services.llm_service import chat_completion
from loguru import logger


async def write_email(topic: str, tone: str = "professional", context: str = "") -> dict:
    """
    Tool: draft an email based on a topic and optional context.
    """
    logger.info(f"[EmailWriter] Writing email about: {topic}")

    messages = [
        {
            "role": "system",
            "content": f"You are an expert email writer. Write {tone} emails that are clear and actionable.",
        },
        {
            "role": "user",
            "content": (
                f"Write an email about: {topic}\n"
                + (f"\nContext:\n{context}" if context else "")
            ),
        },
    ]

    response = await chat_completion(messages, temperature=0.5, max_tokens=600)
    email_text = response.choices[0].message.content

    return {
        "tool": "email_writer",
        "email": email_text,
        "context": email_text,
    }
