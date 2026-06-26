import json
from typing import AsyncGenerator

from app.services.ai_service import chat_once, chat_once_json, chat_stream

CONTRACT_TYPE_NAMES = {
    1: "技术服务合同",
    2: "采购合同",
    3: "劳动合同",
    4: "合作协议",
    5: "保密协议",
}

FIELDS_MAP = {
    1: ["甲方信息", "乙方信息", "服务内容", "服务期限", "服务费用", "付款方式", "违约责任", "争议解决"],
    2: ["买方信息", "卖方信息", "商品名称", "数量规格", "单价总价", "交货时间", "付款方式", "验收标准", "违约责任"],
    3: ["用人单位", "劳动者", "岗位职责", "工作地点", "合同期限", "薪酬福利", "工作时间", "解除条件"],
    4: ["甲方信息", "乙方信息", "合作内容", "合作期限", "利益分配", "退出机制", "保密义务"],
    5: ["披露方", "接收方", "保密范围", "保密期限", "违约责任", "例外条款"],
}

SYSTEM_PROMPT_TEMPLATE = """你是法务小秘的 AI 合同助手，专门负责引导用户起草【{contract_type}】。

你需要通过多轮对话收集以下信息：
{fields}

规则：
1. 每次只问一个问题，用自然的语气引导用户回答。
2. 从列表中提取用户已经提供的字段，标记为【已完成】。
3. 如果用户提供了多个字段的信息，可以一次性提取。
4. 所有字段收集完毕后，输出 JSON 格式的总结。
5. 保持专业、友好的语气。

输出格式参考：
- 提问时：正常对话文本
- 所有字段收集完成时，输出：
【收集完成】
{{"fields": {{"字段名": "值", ...}}, "contract_type": "{contract_type}"}}"""

GENERATION_PROMPT_TEMPLATE = """你是法务小秘的合同生成专家。

请根据以下收集的合同要素，生成一份完整的【{contract_type}】。

## 收集的要素
{fields_json}

## 参考法律依据
{law_context}

## 要求
1. 合同格式规范，条款完整，语言严谨。
2. 必须包含：合同主体信息、鉴于条款、定义、正文条款、签署页。
3. 正文条款至少包括：合同标的、双方权利义务、价款与支付、期限、保密、违约责任、争议解决。
4. 使用中文法律文书标准用语。
5. 生成纯文本格式即可，无需 Markdown 特殊格式。

请直接输出合同全文："""

RISK_ANALYSIS_PROMPT = """你是一位资深法务专家，正在审查合同修改稿。

## 原始条款
{original}

## 修改后的条款
{modified}

请对比分析以上修改，输出 JSON 数组格式的风险分析结果：
[
  {{
    "clause_location": "条款位置",
    "risk_type": "风险类型",
    "risk_level": "high/medium/low",
    "description": "风险描述",
    "suggestion": "修改建议",
    "legal_basis": "法律依据"
  }}
]

只输出 JSON 数组，不要其他文字。"""

COUNTER_ARGUMENT_PROMPT = """你是法务小秘的谈判助手，正在为我方业务人员生成谈判话术。

## 风险条款信息
{risk_info}

## 谈判风格：{style}

请生成两套谈判方案，以 JSON 格式输出：
{{
  "plan_a": "【强硬方案】...（附法条支持）",
  "plan_b": "【折中方案】...（双方可接受的妥协条款）"
}}

只输出 JSON，不要其他文字。"""


class DialogueService:
    def __init__(self, contract_type_id: int):
        self.contract_type_id = contract_type_id
        self.type_name = CONTRACT_TYPE_NAMES.get(contract_type_id, "合同")
        self.fields = FIELDS_MAP.get(contract_type_id, [])

    def build_system_prompt(self) -> str:
        fields_str = "\n".join(f"- {f}" for f in self.fields)
        return SYSTEM_PROMPT_TEMPLATE.format(contract_type=self.type_name, fields=fields_str)

    def build_generation_prompt(self, collected_fields: dict, law_context: str = "") -> str:
        return GENERATION_PROMPT_TEMPLATE.format(
            contract_type=self.type_name,
            fields_json=json.dumps(collected_fields, ensure_ascii=False, indent=2),
            law_context=law_context or "（无相关法条引用）",
        )

    async def chat(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        system_prompt = self.build_system_prompt()
        full_messages = [{"role": "system", "content": system_prompt}, *messages]
        async for chunk in chat_stream(full_messages):
            yield chunk

    async def extract_fields(self, messages: list[dict]) -> dict | None:
        system_prompt = self.build_system_prompt()
        full_messages = [
            {"role": "system", "content": system_prompt + "\n\n现在请检查所有字段是否都已收集。如果都已收集，输出【收集完成】+ JSON；否则继续提问。"},
            *messages,
        ]
        reply = await chat_once(full_messages)
        if "【收集完成】" in reply:
            try:
                json_str = reply.split("【收集完成】")[-1].strip()
                data = json.loads(json_str)
                return data.get("fields", {})
            except (json.JSONDecodeError, AttributeError):
                pass
        return None

    async def generate_contract(self, collected_fields: dict) -> str:
        return await chat_once([
            {"role": "system", "content": self.build_generation_prompt(collected_fields)},
        ])

    async def generate_contract_stream(self, collected_fields: dict) -> AsyncGenerator[str, None]:
        prompt = self.build_generation_prompt(collected_fields)
        async for chunk in chat_stream([{"role": "system", "content": prompt}]):
            yield chunk


async def analyze_risks(original: str, modified: str) -> list[dict]:
    result = await chat_once_json([
        {"role": "system", "content": RISK_ANALYSIS_PROMPT.format(original=original, modified=modified)},
    ])
    if isinstance(result, list):
        return result
    return []


async def generate_counter_argument(risk_info: dict, style: str = "balanced") -> dict:
    result = await chat_once_json([
        {"role": "system", "content": COUNTER_ARGUMENT_PROMPT.format(
            risk_info=json.dumps(risk_info, ensure_ascii=False),
            style=style,
        )},
    ])
    return result
