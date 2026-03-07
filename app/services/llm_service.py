from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import get_settings
from loguru import logger

settings = get_settings()

_client: AsyncGroq = None


def get_groq_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.groq_api_key)
    return _client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def chat_completion(
    messages: list[dict],
    model: str = None,
    temperature: float = 0.2,
    max_tokens: int = 1500,
    tools: list[dict] = None,
) -> object:
    """Call Groq chat completion."""
    client = get_groq_client()
    model = model or settings.groq_model

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    logger.debug(f"LLM call | model={model} | messages={len(messages)}")
    response = await client.chat.completions.create(**kwargs)
    return response