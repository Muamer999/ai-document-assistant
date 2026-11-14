from io import BytesIO
from pathlib import Path

import pytest
from pypdf import PdfWriter

from document_assistant.ingestion import extractors
from document_assistant.ingestion.extractors import extract_pdf

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_extract_pdf_preserves_page_numbers_and_text() -> None:
    content = (FIXTURE_DIR / "sample_document.pdf").read_bytes()

    pages = extract_pdf(content)

    assert [page.page_number for page in pages] == [1, 2, 3]
    assert pages[0].text.strip() == "First page content."
    assert pages[1].text.strip() == ""
    assert pages[2].text.strip() == "Third page content."


@pytest.mark.parametrize(
    "content",
    [b"", b"not a PDF"],
    ids=["empty-file", "invalid-pdf"],
)
def test_extract_pdf_rejects_invalid_content(content: bytes) -> None:
    with pytest.raises(ValueError, match="Could not read PDF document"):
        extract_pdf(content)


def test_extract_pdf_rejects_document_without_text() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)

    with BytesIO() as stream:
        writer.write(stream)
        content = stream.getvalue()

    with pytest.raises(ValueError, match="PDF contains no extractable text"):
        extract_pdf(content)


def test_extract_pdf_rejects_encrypted_document() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.encrypt("test-password", algorithm="RC4-128")

    with BytesIO() as stream:
        writer.write(stream)
        content = stream.getvalue()

    with pytest.raises(ValueError, match="Encrypted PDFs are not supported"):
        extract_pdf(content)


@pytest.mark.parametrize(
    "page_limit",
    [3, 4],
    ids=["at-limit", "below-limit"],
)
def test_extract_pdf_accepts_document_within_page_limit(
    page_limit: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(extractors, "MAX_PDF_PAGES", page_limit)
    content = (FIXTURE_DIR / "sample_document.pdf").read_bytes()

    pages = extract_pdf(content)

    assert len(pages) == 3


def test_extract_pdf_rejects_document_above_page_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(extractors, "MAX_PDF_PAGES", 2)
    content = (FIXTURE_DIR / "sample_document.pdf").read_bytes()

    with pytest.raises(ValueError, match="PDF exceeds the configured page limit"):
        extract_pdf(content)
