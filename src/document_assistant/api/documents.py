from fastapi import APIRouter, HTTPException, UploadFile

from document_assistant.api.schemas import ExtractionResponse
from document_assistant.config import MAX_UPLOAD_BYTES
from document_assistant.ingestion.extractors import extract_txt

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/extract", response_model=ExtractionResponse)
def extract_document(file: UploadFile) -> ExtractionResponse:
    filename = file.filename or ""

    if not filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=415,
            detail="Only .txt files are supported.",
        )

    content = file.file.read(MAX_UPLOAD_BYTES + 1)

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the configured size limit.",
        )

    try:
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
    )
