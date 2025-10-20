from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import openai
import os
from auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])
openai.api_key = os.getenv("OPENAI_API_KEY")

MODELS = {
    "scamper": "gpt-4o-mini",
    "gold buckle": "gpt-4o", 
    "bodacious": "gpt-4-turbo"
}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "scamper"

@router.post("/")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    if request.model not in MODELS:
        raise HTTPException(status_code=400, detail="Invalid model")
    
    openai_model = MODELS[request.model]
    messages = [
        {
            "role": "system",
            "content": "You are RodeoAI, an expert on all things rodeo. Provide accurate, practical advice about rodeo events, techniques, equipment, and western lifestyle. Be concise and helpful."
        }
    ] + [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    async def generate():
        try:
            stream = openai.chat.completions.create(
                model=openai_model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"
    
    return StreamingResponse(generate(), media_type="text/plain")
