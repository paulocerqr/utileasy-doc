from typing import Protocol

from app.modules.comments.domain.entities import Comment, NewComment


class CommentRepository(Protocol):
    def create(self, comment: NewComment) -> Comment: ...

    def list_for_document(self, document_id: int) -> list[Comment]: ...
