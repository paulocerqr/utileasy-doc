from collections.abc import Callable

from app.modules.comments.application.unit_of_work import CommentUnitOfWork
from app.modules.comments.domain.entities import Comment, NewComment


class CommentValidationError(ValueError):
    """O comentário ou o nome informado é inválido."""


class DocumentNotFoundError(LookupError):
    """O documento solicitado não existe."""


class ManageComments:
    def __init__(self, units: Callable[[], CommentUnitOfWork]) -> None:
        self._units = units

    def create(self, document_id: int, content: str, author_name: str | None) -> Comment:
        normalized_content = content.strip()
        normalized_author = author_name.strip() if author_name is not None else "Anônimo"
        if not 1 <= len(normalized_content) <= 2000:
            raise CommentValidationError("Comentário deve ter entre 1 e 2000 caracteres.")
        if not 1 <= len(normalized_author) <= 100:
            raise CommentValidationError("Nome deve ter entre 1 e 100 caracteres.")

        with self._units() as unit:
            if unit.documents.get_by_id(document_id) is None:
                raise DocumentNotFoundError("Documento não encontrado.")
            comment = unit.comments.create(
                NewComment(
                    document_id=document_id,
                    content=normalized_content,
                    author_name=normalized_author,
                )
            )
            unit.commit()
            return comment

    def list(self, document_id: int, limit: int, offset: int) -> list[Comment]:
        with self._units() as unit:
            if unit.documents.get_by_id(document_id) is None:
                raise DocumentNotFoundError("Documento não encontrado.")
            return unit.comments.list_for_document(document_id, limit=limit, offset=offset)
