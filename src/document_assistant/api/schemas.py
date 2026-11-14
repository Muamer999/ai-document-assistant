from pydantic import BaseModel, Field


class PageResponse(BaseModel):
    """Text and original page number of a PDF page."""

    page_number: int = Field(ge=1)
    text: str


class ExtractionResponse(BaseModel):
    """Response containing text extracted from an uploaded document."""

    filename: str
    text: str
    character_count: int
    pages: list[PageResponse] = Field(default_factory=list)
