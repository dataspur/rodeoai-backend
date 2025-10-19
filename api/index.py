"""
RodeoAI backend - Uses OpenAI API for intelligent rodeo expertise.
Vercel serverless function format.
"""

import json
import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

MODELS = {
    "scamper": {"name": "Scamper (Fast)", "icon": "🐎"},
    "gold buckle": {"name": "Gold Buckle", "icon": "🏅"},
    "bodacious": {"name": "Bodacious", "icon": "🐂"}
}

def get_rodeo_response(message, model):
    """Get intelligent rodeo response from OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert rodeo coach and instructor. Provide expert advice on roping techniques, horse training, competition strategies, and all aspects of professional rodeo. Be concise but informative."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting rodeo advice: {str(e)}"

def handler(request):
    """Vercel serverless handler."""
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    # Handle OPTIONS
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    # Handle GET /health
    if request.method == 'GET' and request.path == '/health':
        return (json.dumps({"status": "RodeoAI backend live"}), 200, headers)

    # Handle POST /chat
    if request.method == 'POST' and request.path in ['/chat', '/chat/']:
        try:
            data = json.loads(request.body) if request.body else {}
            message = data.get('message', '')
            model = data.get('model', 'scamper')

            if not message:
                return (json.dumps({"error": "Message is required"}), 400, headers)

            reply = get_rodeo_response(message, model)
            response = {"reply": reply, "model": model}
            return (json.dumps(response), 200, headers)

        except Exception as e:
            return (json.dumps({"error": str(e)}), 500, headers)

    # Handle POST /analytics/log
    if request.method == 'POST' and request.path == '/analytics/log':
        return (json.dumps({"status": "ok", "logged": True}), 200, headers)

    # 404
    return (json.dumps({"error": "Endpoint not found"}), 404, headers)
