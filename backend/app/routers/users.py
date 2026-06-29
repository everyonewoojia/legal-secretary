import os
from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.common import Response
from app.schemas.user import ChangePasswordRequest, UpdateProfileRequest, UserInfo
from app.services.user_service import UserService

router = APIRouter()

AVATAR_DIR = os.path.join(settings.UPLOAD_DIR, "avatars")


@router.get("/me", response_model=Response)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return Response(data=UserInfo.model_validate(current_user))


@router.put("/me", response_model=Response)
def update_my_profile(
    req: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    svc = UserService(db)
    user = svc.update_profile(current_user.id, req)
    return Response(data=UserInfo.model_validate(user))


@router.post("/me/avatar", response_model=Response)
async def upload_avatar(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    content = await file.read()
    os.makedirs(AVATAR_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or ".jpg")[1] or ".jpg"
    avatar_path = os.path.join(AVATAR_DIR, f"{current_user.id}{ext}")
    with open(avatar_path, "wb") as f:
        f.write(content)
    avatar_url = f"/static/avatars/{current_user.id}{ext}"
    current_user.avatar = avatar_url
    db.commit()
    return Response(data={"avatar": avatar_url})


@router.post("/me/change-password", response_model=Response)
def change_my_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(req.old_password, current_user.hashed_password):
        return Response(code=400, message="原密码错误")
    current_user.hashed_password = hash_password(req.new_password)
    db.commit()
    return Response()
