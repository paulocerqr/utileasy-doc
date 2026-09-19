import hashlib
from io import BytesIO

import pytest
from PIL import Image

from app.infrastructure.storage.local import LocalFileStorage
from app.modules.documents.domain.storage import InvalidUploadError


def image_bytes(format_name: str) -> bytes:
    output = BytesIO()
    Image.new("RGB", (2, 2), "red").save(output, format=format_name)
    return output.getvalue()


@pytest.mark.parametrize(
    ("filename", "mime_type", "format_name"),
    [
        ("foto.jpg", "image/jpeg", "JPEG"),
        ("foto.jpeg", "image/jpeg", "JPEG"),
        ("imagem.png", "image/png", "PNG"),
    ],
)
def test_stages_valid_images(tmp_path, filename: str, mime_type: str, format_name: str) -> None:
    storage = LocalFileStorage(tmp_path / "uploads", max_size_bytes=1024 * 1024)
    content = image_bytes(format_name)

    staged = storage.stage(BytesIO(content), filename, mime_type)

    assert staged.sha256 == hashlib.sha256(content).hexdigest()
    assert staged.size_bytes == len(content)
    assert storage.publish(staged) is True
    assert storage.publish(staged) is False
    storage.discard(staged)
    assert (storage.directory / staged.stored_filename).read_bytes() == content


def test_stages_pdf(tmp_path) -> None:
    storage = LocalFileStorage(tmp_path / "uploads", max_size_bytes=1024)
    staged = storage.stage(BytesIO(b"%PDF-1.7\nbody\n%%EOF\n"), "documento.pdf", "application/pdf")

    assert staged.mime_type == "application/pdf"
    assert staged.stored_filename.endswith(".pdf")
    storage.discard(staged)


@pytest.mark.parametrize(
    ("content", "filename", "mime_type", "max_size_bytes"),
    [
        (b"", "vazio.pdf", "application/pdf", 1024),
        (b"<script>alert(1)</script>", "falso.pdf", "application/pdf", 1024),
        (b"%PDF-1.7\n%%EOF", "falso.png", "image/png", 1024),
        (b"%PDF-1.7\n%%EOF", "../evasao.pdf", "application/pdf", 1024),
        (b"%PDF-1.7\n%%EOF", "grande.pdf", "application/pdf", 4),
        (
            b"\x89PNG\r\n\x1a\n" + b"0" * 8 + b"\x00\x00\x00\x00IEND\xaeB`\x82",
            "falso.png",
            "image/png",
            1024,
        ),
    ],
)
def test_rejects_invalid_upload_and_removes_temporary_file(
    tmp_path, content: bytes, filename: str, mime_type: str, max_size_bytes: int
) -> None:
    storage = LocalFileStorage(tmp_path / "uploads", max_size_bytes=max_size_bytes)

    with pytest.raises(InvalidUploadError):
        storage.stage(BytesIO(content), filename, mime_type)

    pending = storage.directory / ".incoming"
    assert not pending.exists() or list(pending.iterdir()) == []
