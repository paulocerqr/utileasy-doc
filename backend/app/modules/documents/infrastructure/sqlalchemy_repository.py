from typing import cast

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.modules.documents.domain.entities import AllowedMimeType, Document, NewDocument
from app.modules.documents.infrastructure.models import DocumentModel


class SqlAlchemyDocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, document: NewDocument) -> Document:
        model = DocumentModel(
            title=document.title,
            description=document.description,
            original_filename=document.original_filename,
            stored_filename=document.stored_filename,
            mime_type=document.mime_type,
            size_bytes=document.size_bytes,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)

    def get_by_id(self, document_id: int) -> Document | None:
        model = self._session.get(DocumentModel, document_id)
        return self._to_entity(model) if model is not None else None

    def list_all(self, search: str | None = None) -> list[Document]:
        statement: Select[tuple[DocumentModel]] = select(DocumentModel)

        if search and (normalized_search := search.strip()):
            statement = statement.where(
                DocumentModel.title.icontains(normalized_search, autoescape=True)
                | DocumentModel.description.icontains(normalized_search, autoescape=True)
            )

        statement = statement.order_by(DocumentModel.uploaded_at.desc(), DocumentModel.id.desc())
        return [self._to_entity(model) for model in self._session.scalars(statement)]

    @staticmethod
    def _to_entity(model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            title=model.title,
            description=model.description,
            original_filename=model.original_filename,
            stored_filename=model.stored_filename,
            mime_type=cast(AllowedMimeType, model.mime_type),
            size_bytes=model.size_bytes,
            uploaded_at=model.uploaded_at,
        )
