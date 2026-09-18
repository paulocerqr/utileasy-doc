from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Identity, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class DocumentModel(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            "char_length(btrim(title)) BETWEEN 1 AND 255",
            name="title_not_blank",
        ),
        CheckConstraint(
            "char_length(btrim(original_filename)) BETWEEN 1 AND 255",
            name="original_filename_not_blank",
        ),
        CheckConstraint(
            "char_length(btrim(stored_filename)) BETWEEN 1 AND 255",
            name="stored_filename_not_blank",
        ),
        CheckConstraint(
            "mime_type IN ('application/pdf', 'image/jpeg', 'image/png')",
            name="mime_type_allowed",
        ),
        CheckConstraint("size_bytes > 0", name="size_bytes_positive"),
        Index("ix_documents_uploaded_at", text("uploaded_at DESC"), text("id DESC")),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
    )
