from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class NewComment:
    document_id: int
    content: str
    author_name: str = "Anônimo"


@dataclass(frozen=True, slots=True)
class Comment:
    id: int
    document_id: int
    author_name: str
    content: str
    created_at: datetime
