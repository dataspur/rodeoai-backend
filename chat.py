from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from auth import get_current_user
from quota import check_quota, check_persona_access, calculate_cost, get_openai_model
from db_models import create_conversation, add_message, log_usage, get_conversation_messages, update_conversation_title

router = APIRouter(prefix="/api/chat", tags=["chat"])
openai.api_key = os.getenv("OPENAI_API_KEY")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "scamper"
    persona: str = "general"
    conversation_id: Optional[int] = None
    stream: bool = True

PERSONA_PROMPTS = {
    "general": "You are RodeoAI, an expert on all things rodeo. Provide accurate, helpful information about rodeo events, schedules, rules, and western lifestyle. Be friendly and concise.",
    "wesley": "You are Wesley Thorp, 3-time PRCA World Champion team roper. Speak in first person. Known for Classic ropes (35' Medium), USTRC/WSTR circuits, and direct practical advice.",
    "dale": "You are Dale Brisby, rodeo entertainer. Enthusiastic and funny. Known for 'It's Rodeo Time!' catchphrase and making rodeo accessible.",
    "carlye": "You are Cowgirl Carlye, barrel racer in WPRA circuits. Warm, supportive, technically knowledgeable about barrel racing and horses.",
    "ezekiel": "You are Ezekiel 'Blue' Mitchell, PBR bull rider. Motivational, tough but fair, safety-conscious.",
    "westdesperado": "You are Westdesperado, western fashion influencer. Knowledgeable about brands like Kimes Ranch and Tecovas. Fashionable and enthusiastic."
}

async def stream_openai_response(messages: List[dict], model: str, conversation_id: int, user_id: int):
    try:
        stream = openai.chat.completions.create(model=get_openai_model(model), messages=messages, stream=True, temperature=0.7)
        full_response = ""
        completion_tokens = 0
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                completion_tokens += 1
                yield content
        prompt_tokens = sum(len(m["content"]) // 4 for m in messages)
        add_message(conversation_id, "assistant", full_response, completion_tokens, model)
        cost = calculate_cost(model, prompt_tokens, completion_tokens)
        log_usage(user_id, conversation_id, model, prompt_tokens, completion_tokens, cost)
    except Exception as e:
        yield f"\n\nError: {str(e)}"

@router.post("/")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    check_quota(current_user, request.model)
    check_persona_access(current_user, request.persona)
    conversation_id = request.conversation_id or create_conversation(current_user["id"], request.model, request.persona)
    user_message = request.messages[-1]
    add_message(conversation_id, "user", user_message.content, 0, request.model)
    messages = get_conversation_messages(conversation_id)
    if len(messages) == 1:
        title = user_message.content[:50] + ("..." if len(user_message.content) > 50 else "")
        update_conversation_title(conversation_id, title)
    openai_messages = [{"role": "system", "content": PERSONA_PROMPTS.get(request.persona, PERSONA_PROMPTS["general"])}]
    for msg in messages[:-1]:
        openai_messages.append({"role": msg["role"], "content": msg["content"]})
    openai_messages.append({"role": "user", "content": user_message.content})
    return StreamingResponse(stream_openai_response(openai_messages, request.model, conversation_id, current_user["id"]), media_type="text/plain")

@router.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    from db_models import get_user_conversations
    return {"conversations": get_user_conversations(current_user["id"])}
