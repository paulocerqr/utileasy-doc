from typing import Protocol

from app.modules.documents.domain.entities import Document, NewDocument


class DocumentRepository(Protocol):
    def create(self, document: NewDocument) -> Document: ...

    def get_by_id(self, document_id: int) -> Document | None: ...

    def list_all(self, search: str | None = None) -> list[Document]: ...
