""""谈判反驳话术生成Agent：基于风险项生成商务谈判话术"""

import json

from backend.app.core.llm import llm_complete


class NegotiationAgent:
    def __init__(self):
        self.system_prompt = (
            "你是一名经验丰富的中国商务律师，擅长合同谈判。\n"
            "根据风险评估结果，为企业业务人员生成可直接使用的谈判话术。\n"
            "话术要求：专业得体、有理有据、策略灵活。"
        )

    async def run(self, context: dict) -> dict:
        risk_items = context.get("risk_items", [])
        contract_type = context.get("contract_type", "")
        company_position = context.get("position", "维护我方合法权益")
        bottom_line = context.get("bottom_line_rules", "")

        if not risk_items:
            return {"intent": "no_risk", "reply": None}

        replies = []
        for item in risk_items:
            reply = await self._generate_single(item, contract_type, company_position, bottom_line)
            replies.append(reply)

        return {"intent": "negotiation_replies", "replies": replies}

    async def _generate_single(
        self,
        risk_item: dict,
        contract_type: str,
        position: str,
        bottom_line: str,
    ) -> dict:
        prompt = (
            f"合同类型：{contract_type}\n"
            f"我方立场：{position}\n\n"
            f"风险条款：{risk_item.get('clause_title', '未知')}\n"
            f"风险等级：{risk_item.get('risk_level', 'low')}\n"
            f"风险描述：{risk_item.get('risk_desc', '无')}\n"
            f"法律依据：{risk_item.get('legal_basis', '无')}\n"
            f"原条款：{risk_item.get('original', '无')}\n"
            f"对方修改为：{risk_item.get('modified', '无')}\n"
            f"我方底线策略：{bottom_line}\n\n"
            f"请严格按照以下JSON格式输出谈判话术（务必使用纯英文键名，不要包含其他文字）：\n"
            f"{{\n"
            f'  "title": "条款简称",\n'
            f'  "strategy_a": {{\n'
            f'    "title": "方案一：据理力争",\n'
            f'    "usage": "适用于我方谈判地位较强时",\n'
            f'    "content": "可直接复制使用的完整话术，包含法条引用"\n'
            f'  }},\n'
            f'  "strategy_b": {{\n'
            f'    "title": "方案二：折中方案",\n'
            f'    "usage": "适用于需要维护合作关系时",\n'
            f'    "content": "包含替代条款建议的完整话术"\n'
            f'  }},\n'
            f'  "bottom_line": "我方在此条款上的底线说明"\n'
            f"}}"
        )

        result_str = await llm_complete(prompt, self.system_prompt)

        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {
                "title": risk_item.get("clause_title", "未知条款"),
                "strategy_a": {
                    "title": "方案一：据理力争",
                    "usage": "适用于我方谈判地位较强时",
                    "content": "无法自动生成话术，请咨询专业律师。",
                },
                "strategy_b": {
                    "title": "方案二：折中方案",
                    "usage": "适用于需要维护合作关系时",
                    "content": "无法自动生成话术，请咨询专业律师。",
                },
                "bottom_line": "请根据实际情况判断。",
            }
