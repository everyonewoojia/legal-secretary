"""合同初稿生成Agent：模板匹配、条款填充、格式生成"""

import json

from backend.app.core.llm import llm_complete
from agent.prompts import load_prompt
from agent.rag_client import RagClient


class ContractAgent:
    async def run(self, session: dict) -> dict:
        contract_type = session["contract_type"]
        slots = session["slots"]

        type_name = self._get_type_name(contract_type)
        template = self._load_template(contract_type)
        slot_summary = self._format_slots(slots)
        rag_context = session.get("rag_context", "")

        # 如果没有 RAG 上下文，主动查询
        if not rag_context:
            try:
                rag = RagClient(db_session=session.get("db"))
                docs = rag.search(f"{type_name} 合同 法律 条款", contract_type, top_k=5)
                rag_context = "\n\n".join([d.get("content", "")[:400] for d in docs])
            except Exception:
                rag_context = ""

        system_prompt = load_prompt("contract_generation")

        user_prompt = (
            f"请生成一份{type_name}。\n\n"
            f"合同要素：\n{slot_summary}\n\n"
            f"合同模板结构：\n{json.dumps(template, ensure_ascii=False, indent=2)}\n\n"
            f"参考法律条文：\n{rag_context if rag_context else '（无）'}\n\n"
            f"请严格按照以下要求输出：\n"
            f"1. 使用模板中的条款结构，但根据用户提供的要素填充具体内容\n"
            f"2. 要素中未提供的字段用 [____] 占位\n"
            f"3. 合同首部包含合同编号（格式：LS-{contract_type}-YYYYMMDD-XXX）\n"
            f"4. 尾部包含签署栏：甲方（盖章）：[____]  乙方（盖章）：[____]\n"
            f"5. 签署日期：[____]年[____]月[____]日\n"
            f"6. 条款语言严谨规范，符合《中华人民共和国民法典》合同编要求\n"
            f"7. 底部添加免责声明：本合同由法务小秘AI自动生成，仅供初步参考，不替代专业律师出具的法律意见。"
        )

        contract_text = await llm_complete(user_prompt, system_prompt)

        return {
            "intent": "contract",
            "contract_text": contract_text,
            "title": f"{type_name}初稿",
            "slots": slots,
        }

    def _get_type_name(self, contract_type: str) -> str:
        names = {
            "tech_service": "技术服务合同",
            "procurement": "采购合同",
            "employment": "劳动合同",
            "cooperation": "合作协议",
            "non_disclosure": "保密协议",
        }
        return names.get(contract_type, "合同")

    def _get_missing_slots(self, contract_type: str, slots: dict) -> list[str]:
        from agent.orchestrator import AgentOrchestrator
        required = AgentOrchestrator.REQUIRED_SLOTS.get(contract_type, [])
        filled = {k for k, v in slots.items() if v}
        return [f for f in required if f not in filled]

    def _format_slots(self, slots: dict) -> str:
        mapping = {
            "party_a": "甲方（委托方）", "party_b": "乙方（受托方）",
            "subject": "合同标的/服务内容", "amount": "合同总金额",
            "term": "合同期限", "payment": "付款方式",
            "penalty": "违约金比例", "jurisdiction": "争议解决法院",
            "product": "采购产品", "quantity": "数量",
            "price": "单价", "delivery_date": "交货日期",
            "position": "职位名称", "location": "工作地点",
            "salary": "月工资", "contract_term": "合同期限类型",
            "work_hours": "工作时间", "project": "合作项目",
            "investment_a": "甲方投入", "investment_b": "乙方投入",
            "profit_split": "收益分配", "scope": "保密信息范围",
        }
        lines = []
        for key, value in slots.items():
            label = mapping.get(key, key)
            lines.append(f"- {label}：{value}")
        return "\n".join(lines)

    def _load_template(self, contract_type: str) -> list[dict]:
        import os, json as j
        path = f"knowledge_base/templates/{contract_type}.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = j.load(f)
                return data.get("clauses", [])
        return []
