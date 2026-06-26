from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import Response
from app.schemas.negotiation import CounterArgumentRequest, DiffResponse, RiskItem
from app.services.contract_service import ContractService
from app.services.file_service import FileService
from app.services.negotiation_service import NegotiationService
from app.utils.text_diff import compute_diff

router = APIRouter()


@router.post("/upload/{contract_id}", response_model=Response)
async def upload_revision(
    contract_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract_svc = ContractService(db)
    contract = contract_svc.get_contract(contract_id)
    if not contract or contract.owner_id != current_user.id:
        return Response(code=404, message="合同不存在")
    path = await FileService.save_upload(file)
    text = FileService.extract_text(path)
    contract_svc.add_version(contract_id, content=text, uploader="counterparty")
    return Response(data={"text_length": len(text), "message": "对方修改稿已上传并解析"})


@router.get("/diff/{contract_id}", response_model=Response)
def get_diff(
    contract_id: int,
    version_a: int | None = None,
    version_b: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract_svc = ContractService(db)
    contract = contract_svc.get_contract(contract_id)
    if not contract or contract.owner_id != current_user.id:
        return Response(code=404, message="合同不存在")
    versions = contract_svc.get_versions(contract_id)
    if len(versions) < 2:
        return Response(code=400, message="版本数不足，无法对比")
    v_a = versions[version_a] if version_a is not None else versions[-2]
    v_b = versions[version_b] if version_b is not None else versions[-1]
    changes = compute_diff(v_a["content"], v_b["content"])
    return Response(data=DiffResponse(original_text=v_a["content"], modified_text=v_b["content"], changes=changes))


@router.post("/ai-analyze/{contract_id}", response_model=Response)
async def ai_analyze_risks(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract_svc = ContractService(db)
    contract = contract_svc.get_contract(contract_id)
    if not contract or contract.owner_id != current_user.id:
        return Response(code=404, message="合同不存在")
    versions = contract_svc.get_versions(contract_id)
    if len(versions) < 2:
        return Response(code=400, message="版本数不足，无法分析")
    original = versions[-2]["content"]
    modified = versions[-1]["content"]
    svc = NegotiationService(db)
    results = await svc.ai_analyze_risks(contract_id, original, modified)
    return Response(data=results)


@router.get("/risks/{contract_id}", response_model=Response)
def list_risks(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = NegotiationService(db)
    risks = svc.get_risks(contract_id)
    return Response(data=[RiskItem.model_validate(r) for r in risks])


@router.post("/counter-argument", response_model=Response)
async def generate_counter_argument(
    req: CounterArgumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = NegotiationService(db)
    result = await svc.generate_counter_argument(req.risk_id, req.negotiation_style)
    return Response(data=result)
