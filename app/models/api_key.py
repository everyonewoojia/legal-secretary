from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ApiKeyConfig(TimestampMixin, Base):
    __tablename__ = "api_key_configs"

    provider: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    api_key: Mapped[str] = mapped_column(String(256), nullable=False)
    base_url: Mapped[str] = mapped_column(String(256), default="", server_default="")
    model_name: Mapped[str] = mapped_column(String(64), default="", server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    remark: Mapped[str] = mapped_column(Text, default="", server_default="")
