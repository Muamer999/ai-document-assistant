from fastapi import FastAPI

app = FastAPI(title="AI Document Assistant")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}