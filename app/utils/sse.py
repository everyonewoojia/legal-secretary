import json
from typing import AsyncGenerator


async def sse_format(data_generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    async for chunk in data_generator:
        yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"
