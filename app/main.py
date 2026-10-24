from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.api.stocks import router
from app.services.finnhub import create_finnhub_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = create_finnhub_client()
    app.state.finnhub_client = client
    try:
        yield
    finally:
        await client.close()


app = FastAPI(title="Stocks Tracker API", lifespan=lifespan)
app.include_router(router)

class HealthResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")

@app.get("/home")
async def home():
    return FileResponse("frontend/index.html")
