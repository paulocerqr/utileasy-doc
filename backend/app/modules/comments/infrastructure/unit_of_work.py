from types import TracebackType

from sqlalchemy.orm import Session, sessionmaker

from app.modules.comments.domain.repositories import CommentRepository
from app.modules.comments.infrastructure.sqlalchemy_repository import SqlAlchemyCommentRepository
from app.modules.documents.domain.repositories import DocumentRepository
from app.modules.documents.infrastructure.sqlalchemy_repository import SqlAlchemyDocumentRepository


class SqlAlchemyCommentUnitOfWork:
    comments: CommentRepository
    documents: DocumentRepository

    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def __enter__(self) -> "SqlAlchemyCommentUnitOfWork":
        self._session = self._sessions()
        self.comments = SqlAlchemyCommentRepository(self._session)
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
