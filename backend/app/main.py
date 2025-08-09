from fastapi import FastAPI
from app.routers import respond

app = FastAPI(title="Fahad Live")

app.include_router(respond.router, prefix="/api")

@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok"}
