import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy import create_engine as create_sqlalchemy_engine
from sqlalchemy.orm import Session

from app.modules.comments.domain.entities import NewComment
from app.modules.comments.infrastructure.sqlalchemy_repository import (
    SqlAlchemyCommentRepository,
)
from app.modules.documents.domain.entities import NewDocument
from app.modules.documents.infrastructure.sqlalchemy_repository import (
    SqlAlchemyDocumentRepository,
)

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def postgres_engine() -> Generator[Engine]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if database_url is None:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests")

    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    command.upgrade(alembic_config, "head")

    engine = create_sqlalchemy_engine(database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def database_session(postgres_engine: Engine) -> Generator[Session]:
    connection = postgres_engine.connect()
    transaction = connection.begin()

    with Session(bind=connection, expire_on_commit=False) as session:
        yield session

    transaction.rollback()
    connection.close()


def create_document(repository: SqlAlchemyDocumentRepository, suffix: str) -> int:
    document = repository.create(
        NewDocument(
            title=f"Contrato {suffix}",
            description="Documento de teste",
            original_filename=f"contrato-{suffix}.pdf",
            stored_filename=f"stored-{suffix}.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
        )
    )
    return document.id


def test_document_repository_persists_and_searches_documents(
    database_session: Session,
) -> None:
    repository = SqlAlchemyDocumentRepository(database_session)

    first_id = create_document(repository, "primeiro")
    second_id = create_document(repository, "segundo")

    assert repository.get_by_id(first_id) is not None
    assert [document.id for document in repository.list_all()] == [second_id, first_id]
    assert [document.id for document in repository.list_all("SEGUNDO")] == [second_id]
    assert repository.get_by_id(999_999) is None


def test_comment_repository_lists_only_comments_from_requested_document(
    database_session: Session,
) -> None:
    document_repository = SqlAlchemyDocumentRepository(database_session)
    comment_repository = SqlAlchemyCommentRepository(database_session)
    first_document_id = create_document(document_repository, "comentado")
    second_document_id = create_document(document_repository, "isolado")

    first_comment = comment_repository.create(
        NewComment(
            document_id=first_document_id,
            author_name="Ana",
            content="Primeiro comentário",
        )
    )
    second_comment = comment_repository.create(
        NewComment(
            document_id=first_document_id,
            content="Segundo comentário",
        )
    )
    comment_repository.create(NewComment(document_id=second_document_id, content="Outro documento"))

    comments = comment_repository.list_for_document(first_document_id)

    assert [comment.id for comment in comments] == [first_comment.id, second_comment.id]
    assert comments[1].author_name == "Anônimo"
