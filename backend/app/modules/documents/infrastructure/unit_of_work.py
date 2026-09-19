from types import TracebackType

from sqlalchemy.orm import Session, sessionmaker

from app.modules.documents.domain.repositories import DocumentRepository
from app.modules.documents.infrastructure.sqlalchemy_repository import SqlAlchemyDocumentRepository


class SqlAlchemyDocumentUnitOfWork:
    documents: DocumentRepository

    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def __enter__(self) -> "SqlAlchemyDocumentUnitOfWork":
        self._session = self._sessions()
        self.documents = SqlAlchemyDocumentRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
