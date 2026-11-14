from fastapi import APIRouter, HTTPException, UploadFile

from document_assistant.api.schemas import ExtractionResponse, PageResponse
from document_assistant.config import MAX_UPLOAD_BYTES
from document_assistant.ingestion.extractors import extract_pdf, extract_txt

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/extract", response_model=ExtractionResponse)
def extract_document(file: UploadFile) -> ExtractionResponse:
    filename = file.filename or ""
    normalized_name = filename.lower()

    if not normalized_name.endswith((".txt", ".pdf")):
        raise HTTPException(
            status_code=415,
            detail="Only .txt and .pdf files are supported.",
        )

    content = file.file.read(MAX_UPLOAD_BYTES + 1)

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the configured size limit.",
        )

    pages: list[PageResponse] = []

    try:
        if normalized_name.endswith(".pdf"):
            extracted_pages = extract_pdf(content)
            text = "\n\n".join(page.text for page in extracted_pages)
            pages = [
                PageResponse(
                    page_number=page.page_number,
                    text=page.text,
                )
                for page in extracted_pages
            ]
        else:
            text = extract_txt(content)

    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail="File must be UTF-8 encoded.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    return ExtractionResponse(
        filename=filename,
        text=text,
        character_count=len(text),
        pages=pages,
    )
