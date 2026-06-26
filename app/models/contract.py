from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Contract(TimestampMixin, Base):
    __tablename__ = "contracts"

    title: Mapped[str] = mapped_column(String(128), default="", server_default="")
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("contract_types.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="draft", server_default="draft", index=True)
    content: Mapped[str] = mapped_column(Text, default="", server_default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="contracts")
    contract_type = relationship("ContractType", back_populates="contracts")
    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="contract", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_contracts_owner_status", "owner_id", "status"),
    )


class ContractVersion(TimestampMixin, Base):
    __tablename__ = "contract_versions"

    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, default="", server_default="")
    uploader: Mapped[str] = mapped_column(String(16), default="ours", server_default="ours")

    contract = relationship("Contract", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("contract_id", "version_number", name="uq_contract_version"),
        Index("idx_version_contract_id", "contract_id"),
    )
