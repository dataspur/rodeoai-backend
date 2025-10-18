import os
from typing import Dict, Any

FOUNDATION_MODELS: Dict[str, Dict[str, Any]] = {
    "scamper": {
        "name": "Scamper",
        "description": "Fast, efficient, instant answers",
        "openai_model": "gpt-4o-mini",
        "icon": "⚡",
        "color": "#008B8B",
        "tagline": "Lightning-fast rodeo answers",
        "max_tokens": 1000,
        "temperature": 0.7
    },
    "gold-buckle": {
        "name": "Gold Buckle",
        "description": "Balanced, everyday workhorse",
        "openai_model": "gpt-4o",
        "icon": "🏆",
        "color": "#DAA520",
        "tagline": "Your champion companion",
        "max_tokens": 2000,
        "temperature": 0.7
    },
    "bodacious": {
        "name": "Bodacious",
        "description": "Maximum power, deep reasoning, complex analysis",
        "openai_model": "gpt-4-turbo",
        "icon": "🐂",
        "color": "#8B0000",
        "tagline": "Unstoppable intelligence",
        "max_tokens": 4000,
        "temperature": 0.7
    }
}

TIER_LIMITS: Dict[str, Dict[str, Any]] = {
    "free": {
        "daily_queries": 10,
        "models": {
            "scamper": {"queries_per_day": 10},
            "gold-buckle": {"queries_per_day": 5}
        }
    },
    "basic": {
        "daily_queries": -1,
        "models": {
            "scamper": {"queries_per_day": -1},
            "gold-buckle": {"queries_per_day": -1}
        }
    },
    "pro": {
        "daily_queries": -1,
        "models": {
            "scamper": {"queries_per_day": -1},
            "gold-buckle": {"queries_per_day": -1},
            "bodacious": {"queries_per_day": -1}
        }
    }
}

RODEO_SYSTEM_PROMPT = """You are RodeoAI, an expert rodeo assistant with deep knowledge of:
- Team roping, Bull riding, Barrel racing
- Rodeo schedules and events
- Equipment and gear recommendations
- Competition strategy and NFR preparation
- Western lifestyle and ranch life

Provide practical, specific advice based on real rodeo expertise. Be conversational, helpful, and use rodeo terminology naturally."""

# Database - use SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./rodeoai.db")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-please-use-a-secure-random-key")
