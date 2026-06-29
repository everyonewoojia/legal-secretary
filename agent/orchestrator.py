"""主控Agent：意图识别、上下文管理与任务路由"""

import json
from typing import Any

from backend.app.core.llm import llm_complete
from agent.rag_client import RagClient


class AgentOrchestrator:
    CONTRACT_TYPES = {
        "tech_service": "技术服务合同",
        "procurement": "采购合同",
        "employment": "劳动合同",
        "cooperation": "合作协议",
        "non_disclosure": "保密协议",
    }

    # 各合同类型必填槽位定义
    REQUIRED_SLOTS = {
        "tech_service": ["party_a", "party_b", "subject", "amount", "term", "payment", "penalty", "jurisdiction"],
        "procurement": ["party_a", "party_b", "product", "quantity", "price", "delivery_date", "payment", "penalty"],
        "employment": ["party_a", "party_b", "position", "location", "salary", "contract_term", "work_hours"],
        "cooperation": ["party_a", "party_b", "project", "investment_a", "investment_b", "profit_split", "term"],
        "non_disclosure": ["party_a", "party_b", "scope", "term", "penalty", "jurisdiction"],
    }

    # 各字段的中文提示映射
    SLOT_PROMPTS = {
        "party_a": "甲方（委托方/雇佣方）的全称是什么？",
        "party_b": "乙方（受托方/员工方）的全称是什么？",
        "subject": "合同标的（服务内容/项目名称）是什么？",
        "amount": "合同总金额是多少？",
        "term": "合同期限是多久？",
        "payment": "付款方式是什么？（如：分期付款、一次性付清等）",
        "penalty": "违约金比例如何约定？",
        "jurisdiction": "争议解决的管辖法院如何约定？",
        "product": "采购的产品名称及规格是什么？",
        "quantity": "采购数量是多少？",
        "price": "单价是多少？",
        "delivery_date": "交货日期是什么时候？",
        "position": "职位名称是什么？",
        "location": "工作地点在哪里？",
        "salary": "月工资是多少（税前）？",
        "contract_term": "合同期限类型是什么？（固定期限/无固定期限）",
        "work_hours": "工作时间制度是什么？（标准工时/综合工时/不定时）",
        "project": "合作项目名称是什么？",
        "investment_a": "甲方投入是什么？",
        "investment_b": "乙方投入是什么？",
        "profit_split": "收益分配方式是什么？",
        "scope": "保密信息的范围是什么？",
    }

    def __init__(self):
        self.sessions: dict[int, dict[str, Any]] = {}

    def get_or_create_session(self, session_id: int, contract_type: str = "") -> dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "contract_type": contract_type,
                "slots": {},
                "history": [],
                "step": 0,
                "completed": False,
            }
        return self.sessions[session_id]

    def get_missing_slots(self, session: dict) -> list[str]:
        contract_type = session["contract_type"]
        required = self.REQUIRED_SLOTS.get(contract_type, [])
        filled = {k for k, v in session["slots"].items() if v}
        return [s for s in required if s not in filled]

    def get_next_question(self, session: dict) -> str | None:
        missing = self.get_missing_slots(session)
        if not missing:
            return None
        return self.SLOT_PROMPTS.get(missing[0], f"请补充：{missing[0]}")

    async def classify_intent(self, message: str, session: dict) -> str:
        if session.get("completed"):
            return "generate"
        missing = self.get_missing_slots(session)
        if not missing:
            return "generate"
        return "dialogue"

    async def process(self, session_id: int, message: str, context: dict) -> dict:
        contract_type = context.get("contract_type", "")
        session = self.get_or_create_session(session_id, contract_type)

        if message:
            session["history"].append({"role": "user", "content": message})

        # ── RAG 增强：注入法律知识上下文 ──
        rag = RagClient(db_session=context.get("db"))
        rag_queries = []
        if contract_type:
            rag_queries.append(contract_type)
        if message and len(message) > 4:
            rag_queries.append(message[:200])

        rag_context_parts = []
        for q in rag_queries:
            results = rag.search(q, contract_type, top_k=3)
            for r in results:
                content = r.get("content", "")
                if content and len(content) > 30:
                    rag_context_parts.append(f"[{r.get('source', '知识库')}]\n{content[:500]}")
        session["rag_context"] = "\n\n---\n\n".join(rag_context_parts[:5]) if rag_context_parts else ""

        intent = await self.classify_intent(message, session)

        if intent == "dialogue":
            from agent.dialogue_agent import DialogueAgent
            agent = DialogueAgent()
            result = await agent.run(session, message)
            session["history"].append({"role": "ai", "content": result.get("reply", "")})
            return result

        elif intent == "generate":
            from agent.contract_agent import ContractAgent
            agent = ContractAgent()
            result = await agent.run(session)
            session["completed"] = True
            return result

        return {"intent": "unknown", "reply": "请先选择合同类型。"}

    async def process_risk_negotiation(self, context: dict) -> dict:
        from agent.risk_agent import RiskAgent
        from agent.negotiation_agent import NegotiationAgent

        # ── RAG 增强：注入法律知识上下文 ──
        rag = RagClient(db_session=context.get("db"))
        contract_type = context.get("contract_type", "")
        original = context.get("original_text", "")
        modified = context.get("modified_text", "")
        diff_text = context.get("diff_text", "")

        rag_query = (
            f"{' '.join(context.get('risk_keywords', []))} "
            f"{contract_type} 法律风险 法律规定"
        ) if context.get("risk_keywords") else f"{contract_type} 合同风险 违约责任 法律规定"

        rag_docs = rag.search(rag_query, contract_type, top_k=5)
        if not rag_docs:
            rag_docs = rag.search(f"{contract_type} 法律", contract_type, top_k=3)

        rag_context_parts = []
        for r in rag_docs:
            content = r.get("content", "")
            if content and len(content) > 30:
                rag_context_parts.append(f"[{r.get('source', '知识库')}]\n{content[:500]}")
        context["rag_context"] = "\n\n---\n\n".join(rag_context_parts[:5]) if rag_context_parts else ""

        risk_result = await RiskAgent().run(context)
        risk_items = risk_result.get("risk_items", [])

        if not risk_items:
            return {"intent": "no_risk", "reply": None}

        negotiation_context = {
            "risk_items": risk_items,
            "contract_type": context.get("contract_type", ""),
            "position": context.get("position", "维护我方合法权益"),
            "bottom_line_rules": context.get("bottom_line_rules", ""),
        }

        reply_result = await NegotiationAgent().run(negotiation_context)

        return {
            "intent": "risk_negotiation",
            "risk_items": risk_items,
            "replies": reply_result.get("replies", []),
        }
