from core.database import get_connection

def create_note(user_id: int, title: str, content: str) -> dict:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
            (user_id, title, content)
        )
        conn.commit()
        return {"ok": True, "id": cursor.lastrowid}
    finally:
        conn.close()

def update_note(user_id: int, note_id: int, title: str = None, content: str = None) -> dict:
    conn = get_connection()
    try:
        if title and content:
            conn.execute(
                "UPDATE notes SET title=?, content=?, updated_at=datetime('now') WHERE id=? AND user_id=?",
                (title, content, note_id, user_id)
            )
        elif title:
            conn.execute(
                "UPDATE notes SET title=?, updated_at=datetime('now') WHERE id=? AND user_id=?",
                (title, note_id, user_id)
            )
        elif content:
            conn.execute(
                "UPDATE notes SET content=?, updated_at=datetime('now') WHERE id=? AND user_id=?",
                (content, note_id, user_id)
            )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()

def delete_note(user_id: int, note_id: int) -> dict:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, user_id))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()

def get_notes(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notes WHERE user_id=? ORDER BY updated_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_note(user_id: int, note_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM notes WHERE id=? AND user_id=?",
        (note_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None
