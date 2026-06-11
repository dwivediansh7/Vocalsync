from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models.database import init_db
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="VocalSync AI",
    description="Multilingual video dubbing platform with speaker diarization",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"name": "VocalSync AI", "status": "running"}

@app.get("/health")
def health():
    return {"status": "All operations working smoothly"} 