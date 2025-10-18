import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

def get_db():
    conn = sqlite3.connect("rodeoai.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_all_tables():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            tier TEXT DEFAULT 'free',
            daily_usage INTEGER DEFAULT 0,
            total_usage INTEGER DEFAULT 0,
            last_reset TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            model TEXT DEFAULT 'scamper',
            persona TEXT DEFAULT 'general',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            model TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            conversation_id INTEGER,
            model TEXT NOT NULL,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            cost REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    """)
    conn.commit()
    conn.close()

def create_conversation(user_id: int, model: str = "scamper", persona: str = "general") -> int:
    conn = get_db()
    cursor = conn.execute("INSERT INTO conversations (user_id, model, persona) VALUES (?, ?, ?)", (user_id, model, persona))
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def get_conversation(conversation_id: int) -> Optional[Dict]:
    conn = get_db()
    conv = conn.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
    conn.close()
    return dict(conv) if conv else None

def get_user_conversations(user_id: int, limit: int = 50) -> List[Dict]:
    conn = get_db()
    convs = conn.execute("SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(c) for c in convs]

def update_conversation_title(conversation_id: int, title: str):
    conn = get_db()
    conn.execute("UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?", (title, datetime.utcnow().isoformat(), conversation_id))
    conn.commit()
    conn.close()

def add_message(conversation_id: int, role: str, content: str, tokens_used: int = 0, model: str = None) -> int:
    conn = get_db()
    cursor = conn.execute("INSERT INTO messages (conversation_id, role, content, tokens_used, model) VALUES (?, ?, ?, ?, ?)", (conversation_id, role, content, tokens_used, model))
    message_id = cursor.lastrowid
    conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (datetime.utcnow().isoformat(), conversation_id))
    conn.commit()
    conn.close()
    return message_id

def get_conversation_messages(conversation_id: int) -> List[Dict]:
    conn = get_db()
    messages = conn.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (conversation_id,)).fetchall()
    conn.close()
    return [dict(m) for m in messages]

def log_usage(user_id: int, conversation_id: int, model: str, prompt_tokens: int, completion_tokens: int, cost: float):
    conn = get_db()
    total_tokens = prompt_tokens + completion_tokens
    conn.execute("INSERT INTO usage_logs (user_id, conversation_id, model, prompt_tokens, completion_tokens, total_tokens, cost) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, conversation_id, model, prompt_tokens, completion_tokens, total_tokens, cost))
    conn.execute("UPDATE users SET daily_usage = daily_usage + ?, total_usage = total_usage + ? WHERE id = ?", (total_tokens, total_tokens, user_id))
    conn.commit()
    conn.close()

def get_user_usage_today(user_id: int) -> int:
    conn = get_db()
    user = conn.execute("SELECT daily_usage FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user["daily_usage"] if user else 0

init_all_tables()
