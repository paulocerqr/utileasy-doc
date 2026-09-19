from types import TracebackType
from typing import Protocol, Self

from app.modules.documents.domain.repositories import DocumentRepository


class DocumentUnitOfWork(Protocol):
    documents: DocumentRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
