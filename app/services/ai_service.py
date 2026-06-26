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


async def chat_stream(messages: list[dict]) -> AsyncGenerator[str, None]:
    client = _get_client()
    if client is None:
        for chunk in _mock_stream(messages):
            yield chunk
        return
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL_NAME, messages=messages, stream=True,
    )
    async for chunk in response:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content


async def chat_once(messages: list[dict]) -> str:
    client = _get_client()
    if client is None:
        return _mock_chat(messages)
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


async def _mock_stream(messages: list[dict]) -> AsyncGenerator[str, None]:
    text = _mock_chat(messages)
    for char in text:
        yield char


def _mock_chat(messages: list[dict]) -> str:
    last = messages[-1]["content"] if messages else ""
    if "生成合同" in last or "generate" in last.lower():
        return _mock_generate_contract()
    if "风险" in last or "risk" in last.lower():
        return _mock_risk_analysis()
    return _mock_dialogue_reply(last)


def _mock_dialogue_reply(user_input: str) -> str:
    return (
        "您好！我是法务小秘的 AI 助手。请问您希望起草什么类型的合同？"
        "目前我们支持：技术服务合同、采购合同、劳动合同、合作协议、保密协议。\n\n"
        "请告诉我您需要起草的合同类型，我将引导您逐步完成关键条款的填写。"
    )


def _mock_generate_contract() -> str:
    return """# 技术服务合同

**甲方：** [甲方公司名称]
**乙方：** [乙方公司名称]

**第一条 服务内容**
甲方委托乙方提供以下技术服务：[服务内容描述]

**第二条 服务期限**
本合同服务期限自 [开始日期] 起至 [结束日期] 止。

**第三条 服务费用及支付方式**
1. 本合同服务费用总额为人民币 [金额] 元（大写：[大写金额]）。
2. 支付方式：[支付方式描述]

**第四条 双方权利义务**
（此处为合同条款模板，请根据实际情况调整）

**第五条 违约责任**
任何一方违反本合同约定，应向对方支付合同总金额 [比例]% 的违约金。

**第六条 争议解决**
因本合同引起的争议，双方应友好协商解决；协商不成的，提交 [管辖法院] 法院诉讼解决。

**第七条 其他**
本合同一式两份，甲乙双方各执一份，具有同等法律效力。

甲方（盖章）：          乙方（盖章）：
签字日期：              签字日期："""


def _mock_risk_analysis() -> str:
    return json.dumps([
        {
            "clause_location": "第七条 违约责任",
            "risk_type": "违约金比例上调",
            "risk_level": "high",
            "description": "对方将违约金比例从每日0.05%上调至每日0.1%，增加幅度达100%，显著加重了我方违约责任。",
            "suggestion": "建议将违约金比例恢复至每日0.05%，或调整为每日0.08%作为折中方案。",
            "legal_basis": "《民法典》第585条：约定的违约金过分高于造成的损失的，人民法院或者仲裁机构可以根据当事人的请求予以适当减少。",
        },
        {
            "clause_location": "第十条 争议解决",
            "risk_type": "管辖法院变更",
            "risk_level": "high",
            "description": "对方将争议管辖法院由甲方所在地法院变更为乙方所在地法院，将大幅增加我方诉讼成本。",
            "suggestion": "建议维持原条款，约定由甲方所在地法院管辖，或变更为合同履行地法院。",
            "legal_basis": "《民事诉讼法》第34条：合同或者其他财产权益纠纷的当事人可以书面协议选择被告住所地、合同履行地、合同签订地、原告住所地、标的物所在地等与争议有实际联系的地点的人民法院管辖。",
        },
    ], ensure_ascii=False)
