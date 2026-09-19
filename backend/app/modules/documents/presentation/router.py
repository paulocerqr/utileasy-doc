from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from app.config.settings import get_settings
from app.infrastructure.database.session import SessionFactory
from app.infrastructure.storage.local import LocalFileStorage
from app.modules.documents.application.create_document import CreateDocument
from app.modules.documents.domain.storage import InvalidUploadError
from app.modules.documents.infrastructure.unit_of_work import SqlAlchemyDocumentUnitOfWork
from app.modules.documents.presentation.schemas import DocumentResponse, UploadDocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


def get_create_document() -> CreateDocument:
    settings = get_settings()
    storage = LocalFileStorage(
        settings.upload_directory,
        max_size_bytes=settings.max_upload_size_mb * 1024 * 1024,
    )
    return CreateDocument(lambda: SqlAlchemyDocumentUnitOfWork(SessionFactory), storage)


@router.post("", response_model=UploadDocumentResponse, status_code=201)
async def upload_document(
    response: Response,
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    use_case: Annotated[CreateDocument, Depends(get_create_document)],
    description: Annotated[str | None, Form()] = None,
) -> UploadDocumentResponse:
    try:
        result = await run_in_threadpool(
            use_case.execute,
            stream=file.file,
            filename=file.filename,
            content_type=file.content_type,
            title=title,
            description=description,
        )
    except InvalidUploadError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    finally:
        await file.close()

    document = result.document
    response.status_code = 200 if result.already_exists else 201
    return UploadDocumentResponse(
        **DocumentResponse.from_document(document).model_dump(),
        already_exists=result.already_exists,
    )
