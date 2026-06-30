from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import RegisterRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, req: RegisterRequest) -> User:
        existing = self.db.query(User).filter(User.phone == req.phone).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该手机号已注册")
        user = User(
            phone=req.phone,
            nickname=req.nickname or f"用户{req.phone[-4:]}",
            company_name=req.company_name,
            hashed_password=hash_password(req.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, phone: str, password: str) -> str:
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="手机号或密码错误")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被停用")
        return create_access_token({"sub": user.id})

    def change_password(self, user: User, old_password: str, new_password: str) -> None:
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
        user.hashed_password = hash_password(new_password)
        self.db.commit()
