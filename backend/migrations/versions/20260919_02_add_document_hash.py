"""Adiciona um hash SHA-256 único para deduplicar o conteúdo.

As versões anteriores não tinham uma API de upload, não há uma fonte confiável
para preencher o hash de registros preexistentes. A migração espera uma tabela vazia.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260919_02"
down_revision: str | None = "20260918_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("sha256", sa.String(length=64), nullable=False))
    op.create_check_constraint("sha256_valid", "documents", "sha256 ~ '^[0-9a-f]{64}$'")
    op.create_unique_constraint("uq_documents_sha256", "documents", ["sha256"])


def downgrade() -> None:
    op.drop_constraint("uq_documents_sha256", "documents", type_="unique")
    op.drop_constraint("ck_documents_sha256_valid", "documents", type_="check")
    op.drop_column("documents", "sha256")
