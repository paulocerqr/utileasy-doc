from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.comments.domain.entities import Comment, NewComment
from app.modules.comments.infrastructure.models import CommentModel


class SqlAlchemyCommentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, comment: NewComment) -> Comment:
        model = CommentModel(
            document_id=comment.document_id,
            author_name=comment.author_name,
            content=comment.content,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_entity(model)

    def list_for_document(self, document_id: int) -> list[Comment]:
        statement = (
            select(CommentModel)
            .where(CommentModel.document_id == document_id)
            .order_by(CommentModel.created_at.asc(), CommentModel.id.asc())
        )
        return [self._to_entity(model) for model in self._session.scalars(statement)]

    @staticmethod
    def _to_entity(model: CommentModel) -> Comment:
        return Comment(
            id=model.id,
            document_id=model.document_id,
            author_name=model.author_name,
            content=model.content,
            created_at=model.created_at,
        )
