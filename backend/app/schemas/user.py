from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1\d{10}$")
    password: str = Field(..., min_length=6, max_length=16)
    nickname: str = Field("", max_length=16)
    company_name: str = Field("", max_length=32)


class LoginRequest(BaseModel):
    phone: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    id: int
    phone: str
    nickname: str
    avatar: str
    gender: int
    company_name: str
    role: str
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    avatar: str | None = None
    gender: int | None = Field(None, ge=0, le=2)
    company_name: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=16)


class SmsCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1\d{10}$")


class SmsCodeResponse(BaseModel):
    code: str
    message: str
