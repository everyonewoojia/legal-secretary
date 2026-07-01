from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models.risk import RiskAssessment
from app.schemas.negotiation import CounterArgumentResponse
from app.services.dialogue_service import analyze_risks, generate_counter_argument
from app.services.rag_service import RagService


class NegotiationService:
    def __init__(self, db: Session):
        self.db = db

    def get_risks(self, contract_id: int) -> list[RiskAssessment]:
        risk_order = case(
            (RiskAssessment.risk_level == 'high', 3),
            (RiskAssessment.risk_level == 'medium', 2),
            (RiskAssessment.risk_level == 'low', 1),
            else_=0
        )
        return (
            self.db.query(RiskAssessment)
            .filter(RiskAssessment.contract_id == contract_id)
            .order_by(risk_order.desc(), RiskAssessment.id.asc())
            .all()
        )

    def save_risk(
        self, contract_id: int, clause_location: str, risk_type: str,
        risk_level: str, description: str, suggestion: str = "", legal_basis: str = "",
    ) -> RiskAssessment:
        risk = RiskAssessment(
            contract_id=contract_id,
            clause_location=clause_location,
            risk_type=risk_type,
            risk_level=risk_level,
            description=description,
            suggestion=suggestion,
            legal_basis=legal_basis,
        )
        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)
        return risk

    async def ai_analyze_risks(self, contract_id: int, original: str, modified: str) -> list[dict]:
        # 获取合同类型，用于 RAG 搜索
        from app.models.contract import Contract
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        rag = RagService(self.db)
        law_context = ""
        if contract:
            from app.models.contract_type import ContractType
            ct = self.db.query(ContractType).filter(ContractType.id == contract.type_id).first()
            if ct:
                docs = rag.search_all(f"{ct.name} 法律风险 违约责任 法律规定", "", top_k=5)
                parts = [f"[{d.get('source', '知识库')}] {d.get('content', '')[:300]}" for d in docs if d.get('content')]
                if parts:
                    law_context = "\n\n".join(parts)

        results = await analyze_risks(original, modified, law_context)
        saved = []
        for r in results:
            risk = self.save_risk(
                contract_id=contract_id,
                clause_location=r.get("clause_location", ""),
                risk_type=r.get("risk_type", ""),
                risk_level=r.get("risk_level", "medium"),
                description=r.get("description", ""),
                suggestion=r.get("suggestion", ""),
                legal_basis=r.get("legal_basis", ""),
            )
            saved.append({
                "id": risk.id,
                "clause_location": risk.clause_location,
                "risk_type": risk.risk_type,
                "risk_level": risk.risk_level,
                "description": risk.description,
                "suggestion": risk.suggestion,
                "legal_basis": risk.legal_basis,
            })
        return saved

    async def generate_counter_argument(self, risk_id: int, style: str = "balanced") -> CounterArgumentResponse:
        risk = self.db.query(RiskAssessment).filter(RiskAssessment.id == risk_id).first()
        if not risk:
            return CounterArgumentResponse(
                plan_a="未找到对应的风险条款信息。",
                plan_b="请重新选择风险条款。",
            )
        risk_info = {
            "clause_location": risk.clause_location,
            "risk_type": risk.risk_type,
            "risk_level": risk.risk_level,
            "description": risk.description,
            "suggestion": risk.suggestion,
            "legal_basis": risk.legal_basis,
        }
        result = await generate_counter_argument(risk_info, style)
        return CounterArgumentResponse(
            plan_a=result.get("plan_a", "【强硬方案】建议坚持原条款，必要时咨询专业律师。"),
            plan_b=result.get("plan_b", "【折中方案】建议在双方可接受的范围内进行适当调整。"),
        )
