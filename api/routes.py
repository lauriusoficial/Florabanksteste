from flask import Blueprint, request, jsonify
from core.auth import login_user, register_user, get_session, logout_user
from modules.transactions import (
    add_transaction, delete_transaction, update_transaction,
    get_balance, get_extract, get_summary_by_category
)
from modules.notes import create_note, update_note, delete_note, get_notes, get_note
from modules.gordon import build_gordon_payload, save_gordon_response, get_history, clear_history
import os, requests

api = Blueprint("api", __name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def auth_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        session = get_session(token)
        if not session:
            return jsonify({"ok": False, "error": "Não autorizado"}), 401
        request.user_id = session["user_id"]
        request.username = session["username"]
        return f(*args, **kwargs)
    return wrapper

# ── AUTH ────────────────────────────────────────────────────────
@api.post("/auth/register")
def route_register():
    d = request.json or {}
    return jsonify(register_user(d.get("username",""), d.get("password","")))

@api.post("/auth/login")
def route_login():
    d = request.json or {}
    return jsonify(login_user(d.get("username",""), d.get("password","")))

@api.post("/auth/logout")
@auth_required
def route_logout():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    logout_user(token)
    return jsonify({"ok": True})

# ── TRANSACTIONS ─────────────────────────────────────────────────
@api.get("/transactions/balance")
@auth_required
def route_balance():
    return jsonify(get_balance(request.user_id))

@api.get("/transactions")
@auth_required
def route_extract():
    type_filter = request.args.get("type")
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    return jsonify(get_extract(request.user_id, type_filter, limit, offset))

@api.get("/transactions/categories")
@auth_required
def route_categories():
    return jsonify(get_summary_by_category(request.user_id))

@api.post("/transactions")
@auth_required
def route_add_transaction():
    d = request.json or {}
    return jsonify(add_transaction(
        request.user_id,
        d.get("type"), d.get("amount", 0),
        d.get("category",""), d.get("description",""),
        d.get("date")
      ))

@api.delete("/transactions/<int:tid>")
@auth_required
def route_delete_transaction(tid):
    return jsonify(delete_transaction(request.user_id, tid))

@api.put("/transactions/<int:tid>")
@auth_required
def route_update_transaction(tid):
    d = request.json or {}
    return jsonify(update_transaction(request.user_id, tid, **d))

# ── NOTES ────────────────────────────────────────────────────────
@api.get("/notes")
@auth_required
def route_get_notes():
    return jsonify(get_notes(request.user_id))

@api.get("/notes/<int:nid>")
@auth_required
def route_get_note(nid):
    note = get_note(request.user_id, nid)
    if not note:
        return jsonify({"ok": False, "error": "Não encontrada"}), 404
    return jsonify(note)

@api.post("/notes")
@auth_required
def route_create_note():
    d = request.json or {}
    return jsonify(create_note(request.user_id, d.get("title",""), d.get("content","")))

@api.put("/notes/<int:nid>")
@auth_required
def route_update_note(nid):
    d = request.json or {}
    return jsonify(update_note(request.user_id, nid, d.get("title"), d.get("content")))

@api.delete("/notes/<int:nid>")
@auth_required
def route_delete_note(nid):
    return jsonify(delete_note(request.user_id, nid))

# ── GORDON ───────────────────────────────────────────────────────
@api.get("/gordon/history")
@auth_required
def route_gordon_history():
    return jsonify(get_history(request.user_id))

@api.delete("/gordon/history")
@auth_required
def route_clear_gordon():
    clear_history(request.user_id)
    return jsonify({"ok": True})

@api.post("/gordon/chat")
@auth_required
def route_gordon_chat():
    d = request.json or {}
    user_message = d.get("message","").strip()
    if not user_message:
        return jsonify({"ok": False, "error": "Mensagem vazia"})

    payload = build_gordon_payload(request.user_id, user_message)

    if not GEMINI_API_KEY:
        reply = "[Gordon offline — configure GEMINI_API_KEY no terminal]"
        save_gordon_response(request.user_id, reply)
        return jsonify({"ok": True, "reply": reply})

    try:
        contents = []
        for m in payload["messages"]:
            role = "user" if m["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })

        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {
                    "parts": [{"text": payload["system"]}]
                },
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": 1024,
                    "temperature": 0.7
                }
            },
            timeout=30
        )
        data = resp.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        save_gordon_response(request.user_id, reply)
        return jsonify({"ok": True, "reply": reply})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
