from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    phone: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(32), default="", server_default="")
    avatar: Mapped[str] = mapped_column(String(256), default="", server_default="")
    gender: Mapped[int] = mapped_column(default=0, server_default="0")
    company_name: Mapped[str] = mapped_column(String(64), default="", server_default="")
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    role: Mapped[str] = mapped_column(String(16), default="user", server_default="user", index=True)

    contracts = relationship("Contract", back_populates="owner", cascade="all, delete-orphan")
