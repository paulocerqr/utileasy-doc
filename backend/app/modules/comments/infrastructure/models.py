from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class CommentModel(Base):
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint(
            "char_length(btrim(author_name)) BETWEEN 1 AND 100",
            name="author_name_not_blank",
        ),
        CheckConstraint(
            "char_length(btrim(content)) BETWEEN 1 AND 2000",
            name="content_length",
        ),
        Index("ix_comments_document_created_at", "document_id", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documents.id", ondelete="CASCADE"),
    )
    author_name: Mapped[str] = mapped_column(
        String(100),
        server_default=text("'Anônimo'"),
    )
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
    )
