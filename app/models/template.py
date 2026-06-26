from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ContractTemplate(TimestampMixin, Base):
    __tablename__ = "contract_templates"

    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contract_types.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    structure: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(16), default="V1.0", server_default="V1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    contract_type = relationship("ContractType", back_populates="templates")

    __table_args__ = (
        UniqueConstraint("type_id", "version", name="uq_template_type_version"),
    )
