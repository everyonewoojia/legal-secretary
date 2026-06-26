from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UpdateProfileRequest


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def update_profile(self, user_id: int, req: UpdateProfileRequest) -> User | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        update_data = req.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user
