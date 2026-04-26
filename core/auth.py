import hashlib
import secrets
import time
from core.database import get_connection

# Simple in-memory session store
_sessions = {}

def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed = stored.split(":")
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False

def register_user(username: str, password: str) -> dict:
    if len(password) < 6:
        return {"ok": False, "error": "Senha deve ter ao menos 6 caracteres"}
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username.strip().lower(), _hash_password(password))
        )
        conn.commit()
        return {"ok": True}
    except Exception:
        return {"ok": False, "error": "Usuário já existe"}
    finally:
        conn.close()

def login_user(username: str, password: str) -> dict:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username.strip().lower(),)
    ).fetchone()
    conn.close()

    if not row or not _verify_password(password, row["password_hash"]):
        return {"ok": False, "error": "Usuário ou senha incorretos"}

    token = secrets.token_hex(32)
    _sessions[token] = {
        "user_id": row["id"],
        "username": row["username"],
        "expires": time.time() + 86400  # 24h
    }
    return {"ok": True, "token": token, "username": row["username"]}

def get_session(token: str) -> dict | None:
    session = _sessions.get(token)
    if not session:
        return None
    if time.time() > session["expires"]:
        del _sessions[token]
        return None
    return session

def logout_user(token: str):
    _sessions.pop(token, None)
