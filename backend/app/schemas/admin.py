from datetime import datetime

from pydantic import BaseModel, Field


class AdminUserResponse(BaseModel):
    id: int
    phone: str
    nickname: str
    avatar: str
    role: str
    is_active: bool
    is_verified: bool
    company_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    provider: str = Field(..., max_length=32)
    api_key: str
    base_url: str = ""
    model_name: str = ""
    remark: str = ""


class ApiKeyUpdate(BaseModel):
    api_key: str | None = None
    base_url: str | None = None
    model_name: str | None = None
    is_active: bool | None = None
    remark: str | None = None


class ApiKeyResponse(BaseModel):
    id: int
    provider: str
    base_url: str
    model_name: str
    is_active: bool
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    resource: str
    detail: str
    ip_address: str
    created_at: datetime

    class Config:
        from_attributes = True
