"""风险分析Agent：差异分析、风险分类、反驳话术生成"""

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

    async def generate_reply(self, risk_item: dict, context: dict) -> dict:
        system_prompt = (
            "你是一名经验丰富的中国商务律师，擅长合同谈判。\n"
            "你的任务是根据风险分析结果，为企业业务人员生成可以直接在谈判中使用的反驳话术。\n"
            "话术应专业、有礼、有力，同时保持商务沟通的得体性。"
        )

        user_prompt = (
            f"请为以下风险条款生成谈判反驳话术：\n\n"
            f"条款名称：{risk_item.get('clause_title', '未知条款')}\n"
            f"风险等级：{risk_item.get('risk_level', 'low')}\n"
            f"风险描述：{risk_item.get('risk_desc', '无')}\n"
            f"法律依据：{risk_item.get('legal_basis', '无')}\n"
            f"原条款：{risk_item.get('original', '无')}\n"
            f"对方修改为：{risk_item.get('modified', '无')}\n\n"
            f"合同类型：{context.get('contract_type', '未知')}\n"
            f"我方立场描述：{context.get('position', '未指定')}\n\n"
            f"请按以下JSON格式输出（纯JSON，不要包含其他文字）：\n"
            f"{{\n"
            f'  "strategy_a": {{\n'
            f'    "title": "方案一：强硬立场",\n'
            f'    "content": "完整的反驳话术（可直接复制使用，包含法条引用）",\n'
            f'    "适用场景": "对方让步空间较大或我方处于优势地位时"\n'
            f'  }},\n'
            f'  "strategy_b": {{\n'
            f'    "title": "方案二：折中妥协",\n'
            f'    "content": "完整的妥协方案话术（包含替代条款建议）",\n'
            f'    "适用场景": "双方关系重要，需要平衡利益时"\n'
            f'  }},\n'
            f'  "bottom_line": "我方底线（不可退让的内容）"\n'
            f"}}"
        )

        result_str = await llm_complete(user_prompt, system_prompt)

        try:
            reply = json.loads(result_str)
        except json.JSONDecodeError:
            reply = {
                "strategy_a": {"title": "方案一：强硬立场", "content": "无法自动生成话术，请人工处理。"},
                "strategy_b": {"title": "方案二：折中妥协", "content": "无法自动生成话术，请人工处理。"},
                "bottom_line": "请根据实际情况判断底线。",
            }

        return {
            "intent": "negotiation_reply",
            "reply": reply,
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
