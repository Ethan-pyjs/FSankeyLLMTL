# FastAPI app entry point
from fastapi import FastAPI
from routes import process

app = FastAPI()

app.include_router(process.router, prefix="/api")