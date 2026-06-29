from typing import AsyncGenerator

from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractVersion
from app.models.contract_type import ContractType
from app.models.template import ContractTemplate
from app.services.dialogue_service import DialogueService
from app.services.rag_service import RagService


class ContractService:
    def __init__(self, db: Session):
        self.db = db

    def list_types(self) -> list[ContractType]:
        return (
            self.db.query(ContractType)
            .filter(ContractType.is_active.is_(True))
            .order_by(ContractType.sort_order)
            .all()
        )

    def get_template(self, type_id: int) -> ContractTemplate | None:
        return (
            self.db.query(ContractTemplate)
            .filter(ContractTemplate.type_id == type_id, ContractTemplate.is_active.is_(True))
            .first()
        )

    def create_contract(self, owner_id: int, type_id: int, content: str, title: str = "") -> Contract:
        if not title:
            type_name = self.db.query(ContractType.name).filter(ContractType.id == type_id).scalar() or ""
            title = f"{type_name}_{owner_id}"
        contract = Contract(owner_id=owner_id, type_id=type_id, content=content, title=title)
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        self.add_version(contract.id, content=content, uploader="ai")
        return contract

    def get_user_contracts(self, owner_id: int, status: str | None = None) -> list[Contract]:
        q = self.db.query(Contract).filter(Contract.owner_id == owner_id)
        if status:
            q = q.filter(Contract.status == status)
        return q.order_by(Contract.created_at.desc()).all()

    def get_contract(self, contract_id: int) -> Contract | None:
        return self.db.query(Contract).filter(Contract.id == contract_id).first()

    def delete_contract(self, contract_id: int, owner_id: int) -> bool:
        contract = self.db.query(Contract).filter(
            Contract.id == contract_id, Contract.owner_id == owner_id
        ).first()
        if not contract:
            return False
        self.db.delete(contract)
        self.db.commit()
        return True

    def add_version(self, contract_id: int, content: str, uploader: str = "ours", change_summary: str = "") -> ContractVersion:
        latest = (
            self.db.query(ContractVersion.version_number)
            .filter(ContractVersion.contract_id == contract_id)
            .order_by(ContractVersion.version_number.desc())
            .first()
        )
        next_num = (latest[0] + 1) if latest else 1
        version = ContractVersion(
            contract_id=contract_id,
            version_number=next_num,
            content=content,
            uploader=uploader,
            change_summary=change_summary,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def get_versions(self, contract_id: int) -> list[dict]:
        versions = (
            self.db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id)
            .order_by(ContractVersion.version_number.asc())
            .all()
        )
        return [
            {
                "id": v.id,
                "version_number": v.version_number,
                "content": v.content,
                "change_summary": v.change_summary,
                "uploader": v.uploader,
                "created_at": str(v.created_at),
            }
            for v in versions
        ]

    async def ai_chat_stream(self, type_id: int, messages: list[dict]) -> AsyncGenerator[str, None]:
        dialog = DialogueService(type_id)
        async for chunk in dialog.chat(messages):
            yield chunk

    async def ai_generate_contract(self, type_id: int, collected_fields: dict) -> str:
        rag = RagService(self.db)
        law_context_parts = []

        # 对每个字段值做语义检索
        for val in collected_fields.values():
            results = rag.search_all(str(val), "", top_k=2)
            for r in results:
                content = r.get("content", "")
                if content and content not in law_context_parts:
                    law_context_parts.append(f"[{r.get('source', '知识库')}] {content[:300]}")

        # 对合同类型做一次综合检索
        type_name = {1: "技术服务合同", 2: "采购合同", 3: "劳动合同", 4: "合作协议", 5: "保密协议"}.get(type_id, "")
        if type_name:
            results = rag.search_all(type_name, "", top_k=3)
            for r in results:
                content = r.get("content", "")
                if content and content not in law_context_parts:
                    law_context_parts.append(f"[{r.get('source', '知识库')}] {content[:300]}")

        law_context = "\n\n".join(law_context_parts) if law_context_parts else ""
        dialog = DialogueService(type_id)
        contract = await dialog.generate_contract(collected_fields, law_context)
        return contract

    async def ai_generate_contract_stream(self, type_id: int, collected_fields: dict) -> AsyncGenerator[str, None]:
        dialog = DialogueService(type_id)
        async for chunk in dialog.generate_contract_stream(collected_fields):
            yield chunk
