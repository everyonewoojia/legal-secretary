from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.admin import AdminUserResponse, ApiKeyResponse, AuditLogResponse
from app.schemas.common import Response
from app.schemas.rag import LawArticleResponse, TemplateResponse
from app.services.admin_service import AdminService

router = APIRouter()


def require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise PermissionError


@router.get("/users", response_model=Response)
def list_users(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Response(code=403, message="无权限")
    svc = AdminService(db)
    users, total = svc.list_users(page, page_size)
    return Response(data={"items": [AdminUserResponse.model_validate(u) for u in users], "total": total})


@router.put("/users/{user_id}/toggle-active", response_model=Response)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Response(code=403, message="无权限")
    svc = AdminService(db)
    user = svc.toggle_user_active(user_id)
    if not user:
        return Response(code=404, message="用户不存在")
    return Response(data={"is_active": user.is_active})


@router.put("/users/{user_id}/role", response_model=Response)
def change_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Response(code=403, message="无权限")
    svc = AdminService(db)
    user = svc.change_user_role(user_id, role)
    if not user:
        return Response(code=404, message="用户不存在")
    return Response(data={"role": user.role})


@router.get("/api-keys", response_model=Response)
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Response(code=403, message="无权限")
    svc = AdminService(db)
    keys = svc.list_api_keys()
    return Response(data=[ApiKeyResponse.model_validate(k) for k in keys])


@router.put("/api-keys/{key_id}", response_model=Response)
def update_api_key(
    key_id: int,
    api_key: str | None = None,
    base_url: str | None = None,
    model_name: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Response(code=403, message="无权限")
    svc = AdminService(db)
    key = svc.update_api_key(key_id, api_key, base_url, model_name, is_active)
    if not key:
        return Response(code=404, message="API Key 不存在")
    return Response(data=ApiKeyResponse.model_validate(key))


@router.get("/logs", response_model=Response)
def list_logs(
    action: str | None = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Response(code=403, message="无权限")
    svc = AdminService(db)
    logs, total = svc.list_logs(action, page, page_size)
    return Response(data={"items": [AuditLogResponse.model_validate(l) for l in logs], "total": total})


@router.get("/stats", response_model=Response)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        return Response(code=403, message="无权限")
    svc = AdminService(db)
    return Response(data=svc.get_stats())
