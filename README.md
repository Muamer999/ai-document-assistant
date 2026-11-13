# AI Document Assistant

A Python application for asking questions about documents using
retrieval-augmented generation (RAG).

## Project status

Work in progress. The initial API and development setup are implemented.

### Implemented

- FastAPI application with a `/health` endpoint
- Interactive API documentation
- Automated API test with pytest
- Dependency management with uv and a committed lockfile
- UTF-8 text extraction with validation for blank and invalid content
- TXT upload endpoint with typed responses and input validation
- Code quality checks with Ruff and continuous integration with GitHub Actions

### Planned

- PDF and text document ingestion
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

## Project structure

- `src/document_assistant/`: application code
- `tests/`: automated tests
- `pyproject.toml`: project metadata, dependencies and tool configuration
- `uv.lock`: resolved dependency versions