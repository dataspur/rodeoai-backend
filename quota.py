from fastapi import HTTPException, status
from db_models import get_user_usage_today

MODEL_COSTS = {
    "bodacious": {"input": 0.000003, "output": 0.000015, "display_name": "Bodacious", "base_model": "gpt-4"},
    "gold-buckle": {"input": 0.0000025, "output": 0.00001, "display_name": "Gold Buckle", "base_model": "gpt-4o"},
    "scamper": {"input": 0.00000015, "output": 0.0000006, "display_name": "Scamper", "base_model": "gpt-4o-mini"}
}

TIER_LIMITS = {
    "free": {"daily_limit": 10000, "allowed_models": ["scamper"], "allowed_personas": ["general", "westdesperado"]},
    "pro": {"daily_limit": 500000, "allowed_models": ["scamper", "gold-buckle"], "allowed_personas": ["general", "wesley", "dale", "carlye", "ezekiel", "westdesperado"]},
    "champion": {"daily_limit": 2000000, "allowed_models": ["scamper", "gold-buckle", "bodacious"], "allowed_personas": ["general", "wesley", "dale", "carlye", "ezekiel", "westdesperado"]},
    "team": {"daily_limit": 10000000, "allowed_models": ["scamper", "gold-buckle", "bodacious"], "allowed_personas": ["general", "wesley", "dale", "carlye", "ezekiel", "westdesperado"]}
}

def check_quota(user: dict, model: str) -> None:
    tier = user.get("tier", "free")
    tier_config = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    if model not in tier_config["allowed_models"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Model '{model}' not available on {tier} tier. Upgrade to access.")
    current_usage = get_user_usage_today(user["id"])
    if current_usage >= tier_config["daily_limit"]:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Daily quota exceeded. Upgrade for more queries.")

def check_persona_access(user: dict, persona: str) -> None:
    tier = user.get("tier", "free")
    tier_config = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    if persona not in tier_config["allowed_personas"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Persona '{persona}' requires Pro tier or higher.")

def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    model_pricing = MODEL_COSTS.get(model, MODEL_COSTS["scamper"])
    return round((prompt_tokens * model_pricing["input"]) + (completion_tokens * model_pricing["output"]), 6)

def get_openai_model(rodeo_model: str) -> str:
    return MODEL_COSTS.get(rodeo_model, MODEL_COSTS["scamper"])["base_model"]
