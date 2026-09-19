from collections.abc import Callable
from dataclasses import dataclass
from typing import BinaryIO

from app.modules.documents.application.unit_of_work import DocumentUnitOfWork
from app.modules.documents.domain.entities import Document, NewDocument
from app.modules.documents.domain.storage import FileStorage, InvalidUploadError


@dataclass(frozen=True, slots=True)
class UploadResult:
    document: Document
    already_exists: bool


class CreateDocument:
    def __init__(self, units: Callable[[], DocumentUnitOfWork], storage: FileStorage) -> None:
        self._units = units
        self._storage = storage

    def execute(
        self,
        *,
        stream: BinaryIO,
        filename: str | None,
        content_type: str | None,
        title: str,
        description: str | None,
    ) -> UploadResult:
        normalized_title = title.strip()
        normalized_description = description.strip() if description else None
        if not 1 <= len(normalized_title) <= 255:
            raise InvalidUploadError("Título deve ter entre 1 e 255 caracteres.")
        if normalized_description and len(normalized_description) > 5000:
            raise InvalidUploadError("Descrição deve ter no máximo 5000 caracteres.")

        staged = self._storage.stage(stream, filename, content_type)
        published = False
        try:
            with self._units() as unit:
                repository = unit.documents
                repository.lock_hash(staged.sha256)
                existing = repository.get_by_hash(staged.sha256)
                if existing is not None:
                    self._storage.publish(staged)
                    unit.rollback()
                    return UploadResult(existing, already_exists=True)

                published = self._storage.publish(staged)
                document = repository.create(
                    NewDocument(
                        title=normalized_title,
                        description=normalized_description or None,
                        original_filename=filename or "",
                        stored_filename=staged.stored_filename,
                        mime_type=staged.mime_type,
                        size_bytes=staged.size_bytes,
                        sha256=staged.sha256,
                    )
                )
                unit.commit()
                return UploadResult(document, already_exists=False)
        except BaseException:
            if published:
                self._storage.remove_published(staged)
            raise
        finally:
            self._storage.discard(staged)
