from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Stocks Tracker API")

class HealthResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")