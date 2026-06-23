from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from backend.app.core.database import get_db
from backend.app.core.response import success, error
from backend.app.schemas.contract import (
    CreateSessionRequest,
    ChatRequest,
    GenerateRequest,
    ExportRequest,
    NegotiateRequest,
)
from backend.app.models.contract import ContractSession, ChatMessage, ContractDraft, NegotiationCase, RiskItem

router = APIRouter(prefix="/api/v1/contract", tags=["contract"])


@router.post("/session")
async def create_session(req: CreateSessionRequest, db: AsyncSession = Depends(get_db)):
    session = ContractSession(contract_type=req.contract_type, user_id=1)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return success({
        "session_id": session.id,
        "contract_type": session.contract_type,
        "status": session.status,
        "next_question": f"请选择 {req.contract_type} 的相关信息",
    })


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        from backend.app.core.llm import llm_stream
        async for chunk in llm_stream(req.message):
            yield {"event": "message", "data": chunk}
        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(event_generator())


@router.post("/generate")
async def generate_contract(req: GenerateRequest, db: AsyncSession = Depends(get_db)):
    from backend.app.services.contract_generator import generate_draft
    draft = await generate_draft(db, req.session_id)
    if not draft:
        return error(40002, "必填字段不完整，请补充合同要素")
    return success({
        "draft_id": draft.id,
        "contract_text": draft.content,
    })


@router.get("/{draft_id}/export")
async def export_contract(draft_id: int, format: str = "docx", db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(ContractDraft).where(ContractDraft.id == draft_id))
    draft = result.scalar_one_or_none()
    if not draft:
        return error(40004, "合同不存在")
    from backend.app.services.export_service import export_docx
    file_path = await export_docx(draft.content, draft.title)
    return success({"download_url": file_path})


@router.post("/negotiate/analyze")
async def negotiate_analyze(req: NegotiateRequest, db: AsyncSession = Depends(get_db)):
    from backend.app.services.diff_service import diff_text
    from backend.app.services.risk_service import analyze_risks

    from sqlalchemy import select
    result = await db.execute(select(ContractDraft).where(ContractDraft.id == req.draft_id))
    draft = result.scalar_one_or_none()
    if not draft:
        return error(40004, "原合同不存在")

    diff_result = diff_text(draft.content, req.modified_text)
    case = NegotiationCase(draft_id=req.draft_id, modified_text=req.modified_text, diff_json=diff_result)
    db.add(case)
    await db.commit()
    await db.refresh(case)

    risks = await analyze_risks(db, case.id, diff_result, req.contract_type)
    return success({
        "case_id": case.id,
        "diff": diff_result,
        "risk_items": risks,
    })
