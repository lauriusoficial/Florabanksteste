from core.database import get_connection

def add_transaction(user_id: int, type_: str, amount: float, category: str, description: str, date: str = None) -> dict:
    if amount <= 0:
        return {"ok": False, "error": "Valor deve ser positivo"}
    if type_ not in ("income", "expense"):
        return {"ok": False, "error": "Tipo inválido"}
    conn = get_connection()
    try:
        if date:
            conn.execute(
                "INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES (?,?,?,?,?,?)",
                (user_id, type_, amount, category, description, date)
            )
        else:
            conn.execute(
                "INSERT INTO transactions (user_id, type, amount, category, description) VALUES (?,?,?,?,?)",
                (user_id, type_, amount, category, description)
            )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()

def delete_transaction(user_id: int, transaction_id: int) -> dict:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()

def update_transaction(user_id: int, transaction_id: int, **fields) -> dict:
    allowed = {"amount", "category", "description", "date", "type"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return {"ok": False, "error": "Nada para atualizar"}
    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [transaction_id, user_id]
        conn.execute(f"UPDATE transactions SET {set_clause} WHERE id = ? AND user_id = ?", values)
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()

def get_balance(user_id: int) -> dict:
    conn = get_connection()
    row = conn.execute('''
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as total_expense
        FROM transactions WHERE user_id = ?
    ''', (user_id,)).fetchone()
    conn.close()
    income = row["total_income"]
    expense = row["total_expense"]
    return {
        "balance": round(income - expense, 2),
        "total_income": round(income, 2),
        "total_expense": round(expense, 2)
    }

def get_extract(user_id: int, type_filter: str = None, limit: int = 100, offset: int = 0) -> list:
    conn = get_connection()
    if type_filter in ("income", "expense"):
        rows = conn.execute('''
            SELECT * FROM transactions WHERE user_id = ? AND type = ?
            ORDER BY date DESC, created_at DESC LIMIT ? OFFSET ?
        ''', (user_id, type_filter, limit, offset)).fetchall()
    else:
        rows = conn.execute('''
            SELECT * FROM transactions WHERE user_id = ?
            ORDER BY date DESC, created_at DESC LIMIT ? OFFSET ?
        ''', (user_id, limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_summary_by_category(user_id: int) -> list:
    conn = get_connection()
    rows = conn.execute('''
        SELECT type, category, ROUND(SUM(amount), 2) as total, COUNT(*) as count
        FROM transactions WHERE user_id = ?
        GROUP BY type, category ORDER BY total DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
