from types import TracebackType
from typing import Protocol, Self

from app.modules.comments.domain.repositories import CommentRepository
from app.modules.documents.domain.repositories import DocumentRepository


class CommentUnitOfWork(Protocol):
    comments: CommentRepository
    documents: DocumentRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...
