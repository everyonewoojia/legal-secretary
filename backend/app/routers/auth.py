from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import Response
from app.schemas.user import (
    LoginRequest,
    RegisterRequest,
    SmsCodeRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=Response)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    svc = AuthService(db)
    user = svc.register(req)
    token = svc.login(req.phone, req.password)
    return Response(data={"user_id": user.id, "token": TokenResponse(access_token=token).model_dump()})


@router.post("/login", response_model=Response)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    svc = AuthService(db)
    token = svc.login(req.phone, req.password)
    return Response(data=TokenResponse(access_token=token))


@router.post("/sms-code", response_model=Response)
def send_sms_code(req: SmsCodeRequest):
    return Response(data={"message": "验证码已发送（演示模式），验证码：123456"})
