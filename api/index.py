"""
RodeoAI backend - Uses OpenAI API for intelligent rodeo expertise.
"""

from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse
from datetime import datetime
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

class handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/' or path == '/health':
            self._set_headers()
            response = {
                "status": "RodeoAI backend live",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        if path == '/chat/' or path == '/chat':
            message = data.get('message', '')
            model = data.get('model', 'scamper')

            if not message:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Message is required"}).encode())
                return

            reply = get_rodeo_response(message, model)
            self._set_headers()
            response = {"reply": reply, "model": model}
            self.wfile.write(json.dumps(response).encode())

        elif path == '/analytics/log':
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok", "logged": True}).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
