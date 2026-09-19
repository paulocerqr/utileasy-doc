from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.comments.domain.entities import Comment


class CreateCommentRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    author_name: str | None = Field(default=None, max_length=100)


class CommentResponse(BaseModel):
    id: int
    document_id: int
    author_name: str
    content: str
    created_at: datetime

    @classmethod
    def from_comment(cls, comment: Comment) -> "CommentResponse":
        return cls(
            id=comment.id,
            document_id=comment.document_id,
            author_name=comment.author_name,
            content=comment.content,
            created_at=comment.created_at,
        )
