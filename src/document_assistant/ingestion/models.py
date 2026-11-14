from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedPage:
    """Text extracted from a document page."""

    page_number: int
    text: str
