from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.api_key import ApiKeyConfig
from app.models.audit import AuditLog
from app.models.contract import Contract
from app.models.knowledge_base import LawArticle
from app.models.user import User


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(self, page: int = 1, page_size: int = 20):
        q = self.db.query(User)
        total = q.count()
        users = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return users, total

    def _log(self, admin_id: int, action: str, resource: str, detail: str = ""):
        self.db.add(AuditLog(user_id=admin_id, action=action, resource=resource, detail=detail))

    def toggle_user_active(self, user_id: int, admin_id: int = 0) -> User | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        user.is_active = not user.is_active
        self._log(admin_id, "toggle_user_active", f"user:{user_id}", f"is_active={user.is_active}")
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_user_role(self, user_id: int, role: str, admin_id: int = 0) -> User | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        old_role = user.role
        user.role = role
        self._log(admin_id, "change_user_role", f"user:{user_id}", f"{old_role} -> {role}")
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_api_keys(self) -> list[ApiKeyConfig]:
        return self.db.query(ApiKeyConfig).all()

    def update_api_key(self, key_id: int, admin_id: int = 0, api_key: str | None = None,
                       base_url: str | None = None, model_name: str | None = None,
                       is_active: bool | None = None) -> ApiKeyConfig | None:
        key = self.db.query(ApiKeyConfig).filter(ApiKeyConfig.id == key_id).first()
        if not key:
            return None
        if api_key is not None:
            key.api_key = api_key
        if base_url is not None:
            key.base_url = base_url
        if model_name is not None:
            key.model_name = model_name
        if is_active is not None:
            key.is_active = is_active
        self._log(admin_id, "update_api_key", f"apikey:{key_id}")
        self.db.commit()
        self.db.refresh(key)
        return key

    def list_logs(self, action: str | None = None, page: int = 1, page_size: int = 50):
        q = self.db.query(AuditLog)
        if action:
            q = q.filter(AuditLog.action == action)
        total = q.count()
        logs = q.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return logs, total

    def get_stats(self) -> dict:
        return {
            "users": self.db.query(func.count(User.id)).scalar() or 0,
            "contracts": self.db.query(func.count(Contract.id)).scalar() or 0,
            "laws": self.db.query(func.count(LawArticle.id)).scalar() or 0,
        }
