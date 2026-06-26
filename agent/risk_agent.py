"""风险分析Agent：差异分析、风险分类（不包含话术生成，话术统一由 NegotiationAgent 负责）"""

import json

from backend.app.core.llm import llm_complete
from agent.prompts import load_prompt


class RiskAgent:
    RISK_KEYWORDS = {
        "jurisdiction": ["管辖", "法院", "仲裁", "诉讼"],
        "penalty": ["违约金", "赔偿", "罚金", "损失"],
        "confidentiality": ["保密", "机密", "商业秘密"],
        "liability_limit": ["责任限制", "免责", "不承担责任", "上限"],
        "payment_term": ["付款", "支付", "对价", "结算"],
        "force_majeure": ["不可抗力", "免责情形", "异常事件"],
        "term_change": ["期限", "有效期", "终止", "续约"],
        "indemnification": ["赔偿", "补偿", " indemnify"],
    }

    async def run(self, context: dict) -> dict:
        diff_text = context.get("diff_text", "")
        contract_type = context.get("contract_type", "")
        original_text = context.get("original_text", "")
        modified_text = context.get("modified_text", "")
        bottom_line_rules = context.get("bottom_line_rules", "")

        system_prompt = load_prompt("risk_analysis")

        user_prompt = (
            f"合同类型：{contract_type}\n\n"
            f"原始合同文本：\n{original_text[:2000]}\n\n"
            f"对方修改后文本：\n{modified_text[:2000]}\n\n"
            f"文本差异（JSON）：\n{diff_text}\n\n"
            f"我方底线策略：\n{bottom_line_rules if bottom_line_rules else '（未配置特定底线策略）'}\n\n"
            f"请按以下JSON格式输出分析结果（纯JSON数组，不要包含其他文字）：\n"
            f'[\n'
            f'  {{\n'
            f'    "clause_title": "条款名称（如：管辖权条款）",\n'
            f'    "risk_level": "high|medium|low",\n'
            f'    "risk_desc": "风险详细描述（说明对方做了什么修改、对我方有何不利影响）",\n'
            f'    "legal_basis": "相关法律依据（引用具体法条）",\n'
            f'    "advice": "应对建议（建议接受、拒绝或折中修改）",\n'
            f'    "original": "原条款内容",\n'
            f'    "modified": "对方修改后内容"\n'
            f'  }}\n'
            f']'
        )

        result_str = await llm_complete(user_prompt, system_prompt)

        try:
            risks = json.loads(result_str)
        except json.JSONDecodeError:
            risks = [{
                "clause_title": "AI解析异常",
                "risk_level": "unknown",
                "risk_desc": "大模型返回格式不符合预期，请人工审查修改内容",
                "legal_basis": "",
                "advice": "请人工逐条审查合同修改内容",
                "original": "",
                "modified": "",
            }]

        return {
            "intent": "risk_analysis",
            "risk_items": risks,
        }

    @staticmethod
    def classify_preliminary_risk(diff_json: str) -> list[dict]:
        """基于关键词的初步风险分类（快速扫描，不依赖大模型）"""
        try:
            changes = json.loads(diff_json)
        except (json.JSONDecodeError, TypeError):
            return []

        risks = []
        for change in changes:
            text = change.get("text", "")
            change_type = change.get("type", "")

            if change_type == "delete":
                continue

            for risk_type, keywords in RiskAgent.RISK_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in text:
                        risks.append({
                            "type": risk_type,
                            "text": text[:100],
                            "preliminary_level": "high",
                        })
                        break

        return risks
