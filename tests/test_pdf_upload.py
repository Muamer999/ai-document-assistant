from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from document_assistant.api import documents
from document_assistant.ingestion import extractors
from document_assistant.main import app

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_pdf_upload_returns_text_and_pages() -> None:
    content = (FIXTURE_DIR / "sample_document.pdf").read_bytes()

    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("sample_document.pdf", content, "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "sample_document.pdf",
        "text": "First page content.\n\n\n\n\nThird page content.\n",
        "character_count": 44,
        "pages": [
            {
                "page_number": 1,
                "text": "First page content.\n",
            },
            {
                "page_number": 2,
                "text": "",
            },
            {
                "page_number": 3,
                "text": "Third page content.\n",
            },
        ],
    }


@pytest.mark.parametrize(
    "content",
    [b"", b"not a PDF"],
    ids=["empty-file", "invalid-pdf"],
)
def test_pdf_upload_rejects_invalid_content(content: bytes) -> None:
    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.pdf", content, "application/pdf")},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Could not read PDF document."


@pytest.mark.parametrize(
    ("encrypted", "expected_detail"),
    [
        (False, "PDF contains no extractable text."),
        (True, "Encrypted PDFs are not supported."),
    ],
    ids=["textless", "encrypted"],
)
def test_pdf_upload_rejects_unusable_document(
    encrypted: bool,
    expected_detail: str,
) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)

    if encrypted:
        writer.encrypt("test-password", algorithm="RC4-128")

    with BytesIO() as stream:
        writer.write(stream)
        content = stream.getvalue()

    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.pdf", content, "application/pdf")},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == expected_detail


def test_pdf_upload_rejects_document_above_page_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(extractors, "MAX_PDF_PAGES", 2)
    content = (FIXTURE_DIR / "sample_document.pdf").read_bytes()

    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.pdf", content, "application/pdf")},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "PDF exceeds the configured page limit."


def test_pdf_upload_rejects_file_above_size_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    content = (FIXTURE_DIR / "sample_document.pdf").read_bytes()
    monkeypatch.setattr(documents, "MAX_UPLOAD_BYTES", len(content) - 1)

    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.pdf", content, "application/pdf")},
        )

    assert response.status_code == 413
    assert response.json()["detail"] == "File exceeds the configured size limit."
