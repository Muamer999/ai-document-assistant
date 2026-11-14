# AI Document Assistant

A Python application for asking questions about documents using
retrieval-augmented generation (RAG).

## Project status

Work in progress. TXT and PDF extraction, automated tests and CI are
implemented. Retrieval and answer generation are planned.

### Implemented

- FastAPI application with a `/health` endpoint
- Interactive API documentation
- Automated API test with pytest
- Dependency management with uv and a committed lockfile
- UTF-8 text extraction with validation for blank and invalid content
- TXT and PDF uploads with typed responses and input validation
- Code quality checks with Ruff and continuous integration with GitHub Actions
- PDF text extraction with preserved page numbers
- Validation for unreadable, encrypted and textless PDFs
- Configurable PDF page limit

### Planned

- PDF upload support
- Text chunking and local embeddings
- Semantic retrieval with ChromaDB
- LLM-generated answers with source references
- Web interface and Docker Compose setup

## Development setup

The following instructions use Windows PowerShell and Python 3.13.

### Installation

```powershell
git clone https://github.com/Muamer999/ai-document-assistant.git
cd ai-document-assistant
py -3.13 -m pip install --user uv
py -3.13 -m uv sync --locked
```

### Run the application

```powershell
py -3.13 -m uv run --locked uvicorn document_assistant.main:app --reload
```

- Health endpoint: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs

Stop the development server with Ctrl+C.

### Run tests

```powershell
py -3.13 -m uv run --locked pytest -v
```

## Document extraction

Upload a UTF-8 `.txt` file using `POST /documents/extract`.
The multipart form field is named `file`.

You can try the endpoint through the interactive documentation at
http://127.0.0.1:8000/docs.

The maximum accepted file content size is 10 MiB.

Example response:

```json
{
  "filename": "test.txt",
  "text": "Hallo, das ist ein Test!",
  "character_count": 24
}
```

| Status | Meaning |
|---|---|
| 200 | Text extracted successfully |
| 413 | File exceeds the configured size limit |
| 415 | Unsupported file extension |
| 422 | Missing file, blank content or invalid UTF-8 |

Files are currently processed for extraction only.
Persistent document storage and indexing are planned.

## PDF extraction

PDF processing is available through the internal Python function
`extract_pdf(content: bytes)`.

It returns a list of `ExtractedPage` objects containing:

- `page_number`: the original page position, starting at 1
- `text`: the extracted text of that page

Individual blank pages are preserved. Documents without extractable
text, encrypted PDFs and documents exceeding the page limit are rejected.

The page limit is defined by `MAX_PDF_PAGES`, currently set to 50.

The HTTP upload endpoint currently accepts TXT files.
PDF upload integration is the next development step.

A synthetic three-page PDF in `tests/fixtures/sample_document.pdf`
provides known text on pages 1 and 3, with a blank page in between.

## Project structure

- `src/document_assistant/`: application code
- `tests/`: automated tests
- `pyproject.toml`: project metadata, dependencies and tool configuration
- `uv.lock`: resolved dependency versions