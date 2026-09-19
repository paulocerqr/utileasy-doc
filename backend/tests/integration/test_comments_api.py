import hashlib
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.modules.comments.application.manage_comments import ManageComments
from app.modules.comments.infrastructure.unit_of_work import SqlAlchemyCommentUnitOfWork
from app.modules.comments.presentation.router import get_manage_comments
from app.modules.documents.domain.entities import NewDocument
from app.modules.documents.infrastructure.sqlalchemy_repository import SqlAlchemyDocumentRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_comment_routes_persist_history(database_session: Session) -> None:
    suffix = uuid4().hex
    document = SqlAlchemyDocumentRepository(database_session).create(
        NewDocument(
            title="Documento comentado",
            description=None,
            original_filename="documento.pdf",
            stored_filename=f"{suffix}.pdf",
            mime_type="application/pdf",
            size_bytes=10,
            sha256=hashlib.sha256(suffix.encode()).hexdigest(),
        )
    )
    sessions = sessionmaker(bind=database_session.connection(), expire_on_commit=False)
    service = ManageComments(lambda: SqlAlchemyCommentUnitOfWork(sessions))
    app.dependency_overrides[get_manage_comments] = lambda: service

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post(
                f"/api/documents/{document.id}/comments",
                json={"content": "  Comentário persistido  "},
            )
            history = await client.get(f"/api/documents/{document.id}/comments")
            missing = await client.get("/api/documents/999999/comments")

        assert created.status_code == 201
        assert created.json()["content"] == "Comentário persistido"
        assert created.json()["document_id"] == document.id
        assert history.status_code == 200
        assert [item["id"] for item in history.json()] == [created.json()["id"]]
        assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()
