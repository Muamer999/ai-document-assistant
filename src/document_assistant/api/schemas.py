from pydantic import BaseModel


class ExtractionResponse(BaseModel):
    """Response containing text extracted from an uploaded document."""

    filename: str
    text: str
    character_count: int
