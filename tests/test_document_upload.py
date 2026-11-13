import pytest
from fastapi.testclient import TestClient

from document_assistant.api import documents
from document_assistant.main import app


def test_extract_document_returns_text() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={
                "file": (
                    "test.txt",
                    b"Hallo, das ist ein Test!",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "filename": "test.txt",
        "text": "Hallo, das ist ein Test!",
        "character_count": 24,
    }


def test_extract_document_rejects_unsupported_file_type() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.pdf", b"Hello", "application/pdf")},
        )

    assert response.status_code == 415
    assert response.json()["detail"] == "Only .txt files are supported."


@pytest.mark.parametrize(
    "content",
    [b"", b" \n\t"],
    ids=["empty", "whitespace"],
)
def test_extract_document_rejects_blank_content(content: bytes) -> None:
    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.txt", content, "text/plain")},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Document contains no text."


def test_extract_document_rejects_invalid_utf8() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.txt", b"\xff", "text/plain")},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "File must be UTF-8 encoded."


def test_extract_document_requires_file() -> None:
    with TestClient(app) as client:
        response = client.post("/documents/extract")

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("size", "expected_status"),
    [(9, 200), (10, 200), (11, 413)],
    ids=["below-limit", "at-limit", "above-limit"],
)
def test_extract_document_enforces_size_limit(
    size: int,
    expected_status: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(documents, "MAX_UPLOAD_BYTES", 10)

    with TestClient(app) as client:
        response = client.post(
            "/documents/extract",
            files={"file": ("test.txt", b"a" * size, "text/plain")},
        )

    assert response.status_code == expected_status
