from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from document_assistant.config import MAX_PDF_PAGES
from document_assistant.ingestion.models import ExtractedPage


def extract_txt(content: bytes) -> str:
    """Decode a UTF-8 text document and reject blank content."""
    text = content.decode("utf-8")

    if not text.strip():
        raise ValueError("Document contains no text.")

    return text


def extract_pdf(content: bytes) -> list[ExtractedPage]:
    """Extract text per page while preserving original page numbers."""
    try:
        with BytesIO(content) as stream:
            reader = PdfReader(stream)

            if reader.is_encrypted:
                raise ValueError("Encrypted PDFs are not supported.")

            if len(reader.pages) > MAX_PDF_PAGES:
                raise ValueError("PDF exceeds the configured page limit.")

            pages: list[ExtractedPage] = []

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                pages.append(
                    ExtractedPage(
                        page_number=page_number,
                        text=text,
                    )
                )

    except PyPdfError as exc:
        raise ValueError("Could not read PDF document.") from exc

    if not any(page.text.strip() for page in pages):
        raise ValueError("PDF contains no extractable text.")

    return pages
