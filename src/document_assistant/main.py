from fastapi import FastAPI

from document_assistant.api.documents import router as documents_router

app = FastAPI(title="AI Document Assistant")
app.include_router(documents_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
