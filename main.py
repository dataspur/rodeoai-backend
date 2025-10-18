"""
Entry point for the RodeoAI backend.

This FastAPI application wires together authentication, chat, and
analytics endpoints.  CORS is configured to allow requests from any
origin by default; update the `allow_origins` list in production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router  # type: ignore
from chat import router as chat_router  # type: ignore
from analytics import router as analytics_router  # type: ignore


app = FastAPI(title="RodeoAI Backend", version="1.0.0")

# In production, restrict allowed origins to your frontend URL(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under appropriate prefixes.
app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")
app.include_router(analytics_router, prefix="/analytics")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "RodeoAI backend live"}
