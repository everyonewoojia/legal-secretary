from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.app.core.database import get_db
from backend.app.core.response import success, error
from backend.app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    phone: str
    password: str


class RegisterRequest(BaseModel):
    phone: str
    password: str
    nickname: str = ""
    company: str = ""


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.phone == req.phone))
    if result.scalar_one_or_none():
        return error(40001, "该手机号已注册")
    from passlib.hash import bcrypt
    user = User(
        phone=req.phone,
        password_hash=bcrypt.hash(req.password),
        nickname=req.nickname or req.phone,
        company=req.company,
    )
    db.add(user)
    await db.commit()
    return success({"user_id": user.id}, "注册成功")


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from passlib.hash import bcrypt
    from datetime import datetime, timedelta
    from jose import jwt
    from backend.app.core.config import settings

    result = await db.execute(select(User).where(User.phone == req.phone))
    user = result.scalar_one_or_none()
    if not user or not bcrypt.verify(req.password, user.password_hash):
        return error(40001, "手机号或密码错误")
    token = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now() + timedelta(hours=8)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return success({
        "token": token,
        "user": {
            "id": user.id,
            "nickname": user.nickname,
            "phone": user.phone,
            "company": user.company,
            "role": user.role,
            "status": user.status,
        },
    })
