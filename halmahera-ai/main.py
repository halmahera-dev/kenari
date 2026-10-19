from fastapi import FastAPI
from api.routes import router
from core.database import db_client

app = FastAPI(title="Scholarship Search API (All Fields)")

@app.on_event("startup")
async def startup_event():
    await db_client.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await db_client.disconnect()

app.include_router(router)