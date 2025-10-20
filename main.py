from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, AsyncGenerator
import openai
from openai import OpenAI
import os
import json
import asyncio

# Railway provides environment variables directly
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 3001))
SECRET_KEY = os.environ.get("SECRET_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="RodeoAI API")

# CORS configuration for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your actual frontend 
URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model configurations
RODEO_MODELS = {
    "scamper": {
        "name": "Scamper",
        "model": "gpt-4o-mini",  # Fast, efficient
        "description": "Lightning-fast answers",
        "emoji": "⚡",
        "system_prompt": """You are Scamper, RodeoAI's lightning-fast 
assistant named after Charmayne James' legendary barrel horse. 
        You provide quick, accurate rodeo information. Be concise and 
to-the-point. 
        You know rodeo schedules, rules, and basic information. Keep 
responses brief unless asked for details.""",
        "temperature": 0.7,
        "max_tokens": 500
    },
    "gold-buckle": {
        "name": "Gold Buckle",
        "model": "gpt-4o",  # Balanced
        "description": "Your champion companion",
        "emoji": "🏆",
        "system_prompt": """You are Gold Buckle, RodeoAI's balanced expert 
assistant named after the prestigious World Champion buckle.
        You provide comprehensive rodeo expertise with the perfect balance of 
depth and clarity.
        You know detailed rodeo information, can explain complex rules, help 
with strategy, and provide thorough answers.
        Be friendly and helpful while maintaining expert-level knowledge.""",
        "temperature": 0.8,
        "max_tokens": 1500
    },
    "bodacious": {
        "name": "Bodacious",
        "model": "gpt-4o",  # Most powerful - you might want to use 
gpt-4-turbo for this
        "description": "Unstoppable intelligence",
        "emoji": "🐂",
        "system_prompt": """You are Bodacious, RodeoAI's most powerful 
assistant named after the legendary bull.
        You provide deep analysis, complex planning, and comprehensive rodeo 
intelligence.
        You can handle multi-faceted questions, create detailed circuit 
plans, analyze statistics, and provide expert-level insights.
        Be thorough, analytical, and never back down from complex queries. 
Include data, statistics, and detailed reasoning.""",
        "temperature": 0.9,
        "max_tokens": 2500
    }
}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gold-buckle"  # Default to Gold Buckle
    stream: bool = True

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "RodeoAI Backend",
        "models": list(RODEO_MODELS.keys())
    }

@app.get("/api/models")
async def get_models():
    """Return available models and their descriptions"""
    return {
        "models": [
            {
                "id": key,
                "name": value["name"],
                "description": value["description"],
                "emoji": value["emoji"]
            }
            for key, value in RODEO_MODELS.items()
        ]
    }

async def generate_stream(messages: List[dict], model_config: dict) -> 
AsyncGenerator[str, None]:
    """Generate streaming response from OpenAI"""
    try:
        # Add system prompt to messages
        full_messages = [
            {"role": "system", "content": model_config["system_prompt"]}
        ] + [msg.dict() for msg in messages]
        
        # Create streaming completion
        stream = client.chat.completions.create(
            model=model_config["model"],
            messages=full_messages,
            temperature=model_config["temperature"],
            max_tokens=model_config["max_tokens"],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"\n\nError: {str(e)}"

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    
    # Validate model selection
    if request.model not in RODEO_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model. Choose 
from: {list(RODEO_MODELS.keys())}")
    
    model_config = RODEO_MODELS[request.model]
    
    if request.stream:
        return StreamingResponse(
            generate_stream(request.messages, model_config),
            media_type="text/event-stream"
        )
    else:
        # Non-streaming response
        try:
            full_messages = [
                {"role": "system", "content": model_config["system_prompt"]}
            ] + [msg.dict() for msg in request.messages]
            
            response = client.chat.completions.create(
                model=model_config["model"],
                messages=full_messages,
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"]
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": request.model,
                "usage": response.usage.dict() if response.usage else None
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
