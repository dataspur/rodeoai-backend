import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path for module imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from auth import router as auth_router
from chat import router as chat_router
from analytics import router as analytics_router

app = FastAPI()

# Configure CORS for all origins (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(analytics_router)

@app.get("/")
async def root():
    return {"message": "Rodeo AI backend is running"}
