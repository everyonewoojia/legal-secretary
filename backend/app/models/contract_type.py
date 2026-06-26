from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ContractType(TimestampMixin, Base):
    __tablename__ = "contract_types"

    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")

    templates = relationship("ContractTemplate", back_populates="contract_type")
    contracts = relationship("Contract", back_populates="contract_type")
