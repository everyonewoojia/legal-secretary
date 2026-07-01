import json
from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI | None:
    global _client
    if _client is None and settings.LLM_API_KEY:
        _client = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)
    return _client


async def chat_stream(messages: list[dict], temperature: float | None = None) -> AsyncGenerator[str, None]:
    client = _get_client()
    if client is None:
        from app.services.ai_mock_data import mock_stream
        async for chunk in mock_stream(messages):
            yield chunk
        return
    kwargs = dict(model=settings.LLM_MODEL_NAME, messages=messages, stream=True)
    if temperature is not None:
        kwargs["temperature"] = temperature
    response = await client.chat.completions.create(**kwargs)
    async for chunk in response:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content


async def chat_once(messages: list[dict]) -> str:
    client = _get_client()
    if client is None:
        from app.services.ai_mock_data import mock_chat
        return mock_chat(messages)
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL_NAME, messages=messages,
    )
    return response.choices[0].message.content or ""


async def chat_once_json(messages: list[dict]) -> dict:
    raw = await chat_once(messages)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("\n", 1)[0]
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    return json.loads(raw)
