"""多轮对话引导Agent：槽位抽取、校验与下一轮提问"""

import json
import re

from backend.app.core.llm import llm_complete, llm_stream
from agent.prompts import load_prompt
from agent.rag_client import RagClient


class DialogueAgent:
    async def run(self, session: dict, message: str) -> dict:
        contract_type = session["contract_type"]
        slots = session["slots"]
        missing = self._get_missing_fields_for_type(contract_type, slots)

        if not missing:
            return {"intent": "complete", "slots": slots, "reply": None}

        current_field = missing[0]
        rag_context = session.get("rag_context", "")

        # 如果当前会话没有 RAG 上下文，尝试通过 RagClient 补充
        if not rag_context:
            try:
                rag = RagClient(db_session=session.get("db"))
                docs = rag.search(f"{contract_type} {current_field} 法律", contract_type, top_k=2)
                rag_context = "\n\n".join([d.get("content", "")[:300] for d in docs])
            except Exception:
                rag_context = ""

        system_prompt = load_prompt("dialogue_system")

        user_prompt = (
            f"当前合同类型：{contract_type}\n"
            f"已收集的合同要素：{json.dumps(slots, ensure_ascii=False)}\n"
            f"用户最新输入：{message}\n\n"
            f"参考法律知识：\n{rag_context if rag_context else '（无）'}\n\n"
            f"请执行以下任务（输出 JSON）：\n"
            f"1. 从用户输入中提取与「{current_field}」相关的信息\n"
            f"2. 如果信息明确，将提取值填入该字段\n"
            f"3. 判断下一个需要询问的缺失字段\n"
            f"4. 生成一个自然的追问问题，可结合参考法律知识给出提示\n\n"
            f"输出格式：{{\n"
            f'  "extracted": {{ "{current_field}": "提取的值或null" }},\n'
            f'  "next_field": "下一个字段名或null",\n'
            f'  "question": "对用户的追问（含法律提示）",\n'
            f'  "is_complete": false\n'
            f"}}"
        )

        result_str = await llm_complete(user_prompt, system_prompt)

        try:
            result = json.loads(result_str)
        except json.JSONDecodeError:
            result = {
                "extracted": {},
                "next_field": current_field,
                "question": "请更详细地描述相关信息。",
                "is_complete": False,
            }

        extracted = result.get("extracted", {})
        for key, value in extracted.items():
            if value and value != "null":
                slots[key] = value

        next_field = result.get("next_field")
        question = result.get("question")

        # 检查是否所有必填字段都已收集
        remaining = self._get_missing_fields_for_type(contract_type, slots)
        if not remaining:
            question = None
            result["is_complete"] = True
            return {"intent": "complete", "slots": slots, "reply": None}

        return {
            "intent": "continue",
            "slots": slots,
            "next_field": next_field,
            "reply": question,
            "missing": remaining,
        }

    def _get_missing_fields_for_type(self, contract_type: str, slots: dict) -> list[str]:
        from agent.orchestrator import AgentOrchestrator
        required = AgentOrchestrator.REQUIRED_SLOTS.get(contract_type, [])
        filled = {k for k, v in slots.items() if v}
        return [f for f in required if f not in filled]

    def get_slot_summary(self, slots: dict) -> str:
        summary = []
        mapping = {
            "party_a": "甲方", "party_b": "乙方", "subject": "合同标的",
            "amount": "合同金额", "term": "合同期限", "payment": "付款方式",
            "penalty": "违约金比例", "jurisdiction": "管辖法院",
            "product": "产品", "quantity": "数量", "price": "单价",
            "delivery_date": "交货日期", "position": "职位", "location": "工作地点",
            "salary": "工资", "contract_term": "合同期限类型",
            "work_hours": "工时制度", "project": "合作项目",
            "investment_a": "甲方投入", "investment_b": "乙方投入",
            "profit_split": "收益分配", "scope": "保密范围",
        }
        for key, value in slots.items():
            label = mapping.get(key, key)
            summary.append(f"{label}：{value}")
        return "\n".join(summary)
