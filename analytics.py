"""
Simple analytics logging router.

This module defines an endpoint that accepts analytics log entries from
the frontend and appends them to a newline-delimited JSON file.  It
records the client's IP and a human-readable timestamp for easy
analysis.  In production, consider piping these logs to a proper
database or analytics service instead of a flat file.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
import datetime
import json
import os


router = APIRouter()


class AnalyticsLog(BaseModel):
    """Schema for incoming analytics log entries."""

    chatId: int
    model: str
    prompt: str
    response: str
    timestamp: int


@router.post("/log")
async def log_analytics(log: AnalyticsLog, request: Request) -> dict:
    """
    Append a log entry to the analytics log file.

    The log file location can be customized via the `ANALYTICS_LOG`
    environment variable; it defaults to `analytics.log` in the current
    working directory.  Each line in the file is a JSON object.
    """
    data = log.dict()
    data["ip"] = request.client.host
    data["ts_readable"] = datetime.datetime.fromtimestamp(data["timestamp"] / 1000).isoformat()
    log_path = os.environ.get("ANALYTICS_LOG", "analytics.log")
    with open(log_path, "a") as f:
        f.write(json.dumps(data) + "\n")
    return {"status": "ok"}
