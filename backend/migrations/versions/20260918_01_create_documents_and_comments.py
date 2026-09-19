"""Cria as tabelas de documentos e comentários."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260918_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(btrim(title)) BETWEEN 1 AND 255",
            name="title_not_blank",
        ),
        sa.CheckConstraint(
            "char_length(btrim(original_filename)) BETWEEN 1 AND 255",
            name="original_filename_not_blank",
        ),
        sa.CheckConstraint(
            "char_length(btrim(stored_filename)) BETWEEN 1 AND 255",
            name="stored_filename_not_blank",
        ),
        sa.CheckConstraint(
            "mime_type IN ('application/pdf', 'image/jpeg', 'image/png')",
            name="mime_type_allowed",
        ),
        sa.CheckConstraint("size_bytes > 0", name="size_bytes_positive"),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
        sa.UniqueConstraint("stored_filename", name="uq_documents_stored_filename"),
    )
    op.create_index(
        "ix_documents_uploaded_at",
        "documents",
        [sa.literal_column("uploaded_at DESC"), sa.literal_column("id DESC")],
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("document_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "author_name",
            sa.String(length=100),
            server_default=sa.text("'Anônimo'"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "char_length(btrim(author_name)) BETWEEN 1 AND 100",
            name="author_name_not_blank",
        ),
        sa.CheckConstraint(
            "char_length(btrim(content)) BETWEEN 1 AND 2000",
            name="content_length",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name="fk_comments_document_id_documents",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_comments"),
    )
    op.create_index(
        "ix_comments_document_created_at",
        "comments",
        ["document_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_comments_document_created_at", table_name="comments")
    op.drop_table("comments")
    op.drop_index("ix_documents_uploaded_at", table_name="documents")
    op.drop_table("documents")
