from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.comments.application.manage_comments import (
    CommentValidationError,
    DocumentNotFoundError,
    ManageComments,
)
from app.modules.comments.domain.entities import Comment
from app.modules.comments.presentation.router import get_manage_comments


class FakeComments:
    def __init__(self) -> None:
        self.comments: list[Comment] = []

    def create(self, document_id: int, content: str, author_name: str | None) -> Comment:
        if document_id != 42:
            raise DocumentNotFoundError("Documento não encontrado.")
        normalized_content = content.strip()
        normalized_author = author_name.strip() if author_name else "Anônimo"
        if not normalized_content:
            raise CommentValidationError("Comentário vazio.")
        if not normalized_author:
            raise CommentValidationError("Nome vazio.")
        comment = Comment(
            id=len(self.comments) + 1,
            document_id=document_id,
            author_name=normalized_author,
            content=normalized_content,
            created_at=datetime.now(UTC),
        )
        self.comments.append(comment)
        return comment

    def list(self, document_id: int, limit: int, offset: int) -> list[Comment]:
        if document_id != 42:
            raise DocumentNotFoundError("Documento não encontrado.")
        return self.comments[offset : offset + limit]


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_comment_routes_create_list_and_validate() -> None:
    service = FakeComments()
    app.dependency_overrides[get_manage_comments] = lambda: service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            first = await client.post(
                "/api/documents/42/comments", json={"content": "  Primeiro  "}
            )
            second = await client.post(
                "/api/documents/42/comments",
                json={"content": "Segundo", "author_name": " Ana "},
            )
            history = await client.get("/api/documents/42/comments")
            page = await client.get("/api/documents/42/comments", params={"limit": 1, "offset": 1})
            missing_get = await client.get("/api/documents/99/comments")
            missing_post = await client.post(
                "/api/documents/99/comments", json={"content": "Teste"}
            )
            blank = await client.post("/api/documents/42/comments", json={"content": "   "})
            oversized = await client.post(
                "/api/documents/42/comments", json={"content": "x" * 2001}
            )
            invalid_page = await client.get("/api/documents/42/comments", params={"limit": 101})

        assert first.status_code == 201
        assert first.json()["author_name"] == "Anônimo"
        assert first.json()["content"] == "Primeiro"
        assert first.json()["created_at"]
        assert second.status_code == 201
        assert second.json()["author_name"] == "Ana"
        assert [item["id"] for item in history.json()] == [1, 2]
        assert [item["id"] for item in page.json()] == [2]
        assert missing_get.status_code == 404
        assert missing_post.status_code == 404
        assert blank.status_code == 422
        assert oversized.status_code == 422
        assert invalid_page.status_code == 422
    finally:
        app.dependency_overrides.clear()


class FakeDocumentsRepository:
    def get_by_id(self, document_id: int) -> object | None:
        return object() if document_id == 42 else None


class FakeCommentsRepository:
    def __init__(self) -> None:
        self.items: list[Comment] = []

    def create(self, comment) -> Comment:
        saved = Comment(
            id=len(self.items) + 1,
            document_id=comment.document_id,
            author_name=comment.author_name,
            content=comment.content,
            created_at=datetime.now(UTC),
        )
        self.items.append(saved)
        return saved

    def list_for_document(self, document_id: int, limit: int, offset: int) -> list[Comment]:
        return self.items[offset : offset + limit]


class FakeUnitOfWork:
    def __init__(self, comments: FakeCommentsRepository) -> None:
        self.documents = FakeDocumentsRepository()
        self.comments = comments
        self.committed = False

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True


def test_comment_use_case_normalizes_and_checks_document() -> None:
    repository = FakeCommentsRepository()
    unit = FakeUnitOfWork(repository)
    service = ManageComments(lambda: unit)

    created = service.create(42, "  Texto  ", None)

    assert created.content == "Texto"
    assert created.author_name == "Anônimo"
    assert unit.committed is True
    assert service.list(42, 100, 0) == [created]
    with pytest.raises(DocumentNotFoundError):
        service.create(99, "Texto", None)
    with pytest.raises(DocumentNotFoundError):
        service.list(99, 100, 0)
    with pytest.raises(CommentValidationError):
        service.create(42, "   ", None)
    with pytest.raises(CommentValidationError):
        service.create(42, "Texto", "   ")
