from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="RodeoAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from auth import router as auth_router
from chat import router as chat_router

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {"status": "RodeoAI backend running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
