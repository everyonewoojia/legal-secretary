import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.schemas.contract import (
    ChatRequest,
    ContractListItem,
    ContractResponse,
    ContractTypeResponse,
    CreateContractRequest,
    GenerateRequest,
)
from app.schemas.negotiation import RiskItem
from app.services.contract_service import ContractService
from app.services.dialogue_service import DialogueService
from app.services.negotiation_service import NegotiationService
from app.utils.sse import sse_format

router = APIRouter()


@router.get("/types", response_model=Response)
def list_contract_types(db: Session = Depends(get_db)):
    svc = ContractService(db)
    types = svc.list_types()
    return Response(data=[ContractTypeResponse.model_validate(t) for t in types])


@router.post("/chat/{type_id}")
async def chat_stream(
    type_id: int,
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    messages = req.history + [{"role": "user", "content": req.message}]

    async def generate():
        async for chunk in svc.ai_chat_stream(type_id, messages):
            if isinstance(chunk, dict):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            else:
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/generate/{type_id}")
async def generate_contract(
    type_id: int,
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    contract_text = await svc.ai_generate_contract(type_id, req.collected_fields)
    contract = svc.create_contract(
        owner_id=current_user.id,
        type_id=type_id,
        content=contract_text,
        title=req.title or "",
    )
    return Response(data=ContractResponse.model_validate(contract))


@router.post("/plan/{type_id}", response_model=Response)
async def generate_contract_plan(
    type_id: int,
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    plan = await svc.ai_generate_plan(type_id, req.collected_fields)
    return Response(data={"plan": plan, "type_id": type_id})


@router.post("/generate-stream/{type_id}")
async def generate_contract_stream(
    type_id: int,
    req: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)

    async def generate():
        full_text = ""
        try:
            async for chunk in svc.ai_generate_contract_stream(type_id, req.collected_fields):
                full_text += chunk
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            contract = svc.create_contract(
                owner_id=current_user.id, type_id=type_id, content=full_text, title=req.title or "",
            )
            yield f"data: {json.dumps({'done': True, 'contract_id': contract.id}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)[:200]}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/", response_model=Response)
def create_contract(
    req: CreateContractRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    contract = svc.create_contract(owner_id=current_user.id, type_id=req.type_id, content=req.content, title=req.title)
    return Response(data=ContractResponse.model_validate(contract))


@router.get("/", response_model=Response)
def list_contracts(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    contracts = svc.get_user_contracts(current_user.id, status)
    return Response(data=[ContractListItem.model_validate(c) for c in contracts])


@router.get("/{contract_id}", response_model=Response)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    contract = svc.get_contract(contract_id)
    if not contract or contract.owner_id != current_user.id:
        return Response(code=404, message="合同不存在")
    return Response(data=ContractResponse.model_validate(contract))


@router.delete("/{contract_id}", response_model=Response)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    ok = svc.delete_contract(contract_id, current_user.id)
    if not ok:
        return Response(code=404, message="合同不存在")
    return Response()


@router.get("/{contract_id}/download", response_model=Response)
def download_contract(
    contract_id: int,
    fmt: str = "docx",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    contract = svc.get_contract(contract_id)
    if not contract or contract.owner_id != current_user.id:
        return Response(code=404, message="合同不存在")
    return Response(data={"content": contract.content, "title": contract.title, "format": fmt})


@router.get("/{contract_id}/versions", response_model=Response)
def list_versions(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = ContractService(db)
    versions = svc.get_versions(contract_id)
    return Response(data=versions)


@router.get("/{contract_id}/risks", response_model=Response)
def list_contract_risks(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = NegotiationService(db)
    risks = svc.get_risks(contract_id)
    return Response(data=[RiskItem.model_validate(r) for r in risks])
