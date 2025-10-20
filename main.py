from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, AsyncGenerator
import os
import json
from openai import OpenAI

# Environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 3001))

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="RodeoAI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Models
RODEO_MODELS = {
    "scamper": {
        "name": "Scamper",
        "model": "gpt-4o-mini",
        "description": "Lightning-fast answers",
        "emoji": "⚡",
        "system_prompt": "You are Scamper, RodeoAI's lightning-fast 
assistant. Provide quick, concise rodeo information.",
        "temperature": 0.7,
        "max_tokens": 500
    },
    "gold-buckle": {
        "name": "Gold Buckle",
        "model": "gpt-4o",
        "description": "Your champion companion",
        "emoji": "🏆",
        "system_prompt": "You are Gold Buckle, RodeoAI's balanced expert. 
Provide comprehensive rodeo expertise.",
        "temperature": 0.8,
        "max_tokens": 1500
    },
    "bodacious": {
        "name": "Bodacious",
        "model": "gpt-4o",
        "description": "Unstoppable intelligence",
        "emoji": "🐂",
        "system_prompt": "You are Bodacious, RodeoAI's most powerful 
assistant. Provide deep analysis and complex planning.",
        "temperature": 0.9,
        "max_tokens": 2500
    }
}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gold-buckle"
    stream: bool = True

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": "RodeoAI Backend",
        "models": list(RODEO_MODELS.keys()),
        "openai_configured": OPENAI_API_KEY is not None
    }

@app.get("/api/models")
async def get_models():
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

async def generate_stream(messages: List[ChatMessage], model_config: dict) -> 
AsyncGenerator[str, None]:
    try:
        full_messages = [
            {"role": "system", "content": model_config["system_prompt"]}
        ] + [{"role": msg.role, "content": msg.content} for msg in messages]
        
        stream = client.chat.completions.create(
            model=model_config["model"],
            messages=full_messages,
            temperature=model_config["temperature"],
            max_tokens=model_config["max_tokens"],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield f"data: {json.dumps({'content': 
chunk.choices[0].delta.content})}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if request.model not in RODEO_MODELS:
        raise HTTPException(status_code=400, detail=f"Invalid model")
    
    model_config = RODEO_MODELS[request.model]
    
    if request.stream:
        return StreamingResponse(
            generate_stream(request.messages, model_config),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    else:
        try:
            full_messages = [
                {"role": "system", "content": model_config["system_prompt"]}
            ] + [{"role": msg.role, "content": msg.content} for msg in 
request.messages]
            
            response = client.chat.completions.create(
                model=model_config["model"],
                messages=full_messages,
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"]
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": request.model
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
