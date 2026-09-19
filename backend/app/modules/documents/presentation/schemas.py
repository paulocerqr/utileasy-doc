from datetime import datetime

from pydantic import BaseModel

from app.modules.documents.domain.entities import AllowedMimeType


class UploadDocumentResponse(BaseModel):
    id: int
    title: str
    description: str | None
    original_filename: str
    mime_type: AllowedMimeType
    size_bytes: int
    sha256: str
    uploaded_at: datetime
    already_exists: bool
