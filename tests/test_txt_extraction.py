import pytest

from document_assistant.ingestion.extractors import extract_txt


def test_extract_txt_preserves_text() -> None:
    expected = "  Grüße aus Wien.\nZweite Zeile.\n"
    content = expected.encode("utf-8")

    assert extract_txt(content) == expected


@pytest.mark.parametrize(
    "content",
    [b"", b" \n\t"],
    ids=["empty", "whitespace"],
)
def test_extract_txt_rejects_blank_content(content: bytes) -> None:
    with pytest.raises(ValueError, match="Document contains no text"):
        extract_txt(content)


def test_extract_txt_rejects_invalid_utf8() -> None:
    with pytest.raises(UnicodeDecodeError):
        extract_txt(b"\xff")
