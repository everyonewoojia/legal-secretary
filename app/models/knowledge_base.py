from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LawArticle(TimestampMixin, Base):
    __tablename__ = "law_articles"

    title: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(64), default="", server_default="")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(32), default="", server_default="", index=True)

    __table_args__ = (
        Index("idx_law_source_category", "source", "category"),
    )
