def extract_txt(content: bytes) -> str:
    """Decode a UTF-8 text document and reject blank content."""
    text = content.decode("utf-8")

    if not text.strip():
        raise ValueError("Document contains no text.")

    return text
