from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RiskAssessment(TimestampMixin, Base):
    __tablename__ = "risk_assessments"

    contract_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False
    )
    clause_location: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[str] = mapped_column(Text, default="", server_default="")
    legal_basis: Mapped[str] = mapped_column(Text, default="", server_default="")

    contract = relationship("Contract", back_populates="risk_assessments")

    __table_args__ = (
        Index("idx_risk_contract_level", "contract_id", "risk_level"),
    )
