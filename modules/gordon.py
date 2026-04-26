from core.database import get_connection
from modules.transactions import get_balance, get_extract, get_summary_by_category

def _build_context(user_id: int) -> str:
    balance = get_balance(user_id)
    recent = get_extract(user_id, limit=10)
    categories = get_summary_by_category(user_id)

    ctx = f"""Você é Gordon, o agente financeiro pessoal do Flora Banks.
Você é direto, inteligente e fala como um analista financeiro de confiança — sem enrolação.
Você tem acesso aos dados financeiros reais do usuário.

=== SITUAÇÃO FINANCEIRA ATUAL ===
Saldo: R$ {balance['balance']:.2f}
Total de entradas: R$ {balance['total_income']:.2f}
Total de saídas: R$ {balance['total_expense']:.2f}

=== ÚLTIMAS TRANSAÇÕES ===
"""
    if recent:
        for t in recent:
            emoji = "↑" if t["type"] == "income" else "↓"
            ctx += f"{emoji} R$ {t['amount']:.2f} | {t.get('category','') or 'Sem categoria'} | {t.get('description','') or 'Sem descrição'} | {t['date']}\n"
    else:
        ctx += "Nenhuma transação registrada ainda.\n"

    if categories:
        ctx += "\n=== RESUMO POR CATEGORIA ===\n"
        for c in categories:
            tipo = "Entrada" if c["type"] == "income" else "Saída"
            ctx += f"{tipo} | {c.get('category') or 'Sem categoria'}: R$ {c['total']:.2f} ({c['count']}x)\n"

    ctx += "\nResponda sempre em português. Seja útil, preciso e conciso."
    return ctx

def _save_message(user_id: int, role: str, content: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO gordon_messages (user_id, role, content) VALUES (?,?,?)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()

def get_history(user_id: int, limit: int = 20) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content FROM gordon_messages WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return list(reversed([dict(r) for r in rows]))

def clear_history(user_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM gordon_messages WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def build_gordon_payload(user_id: int, user_message: str) -> dict:
    """Returns system prompt + messages history ready for Claude API call."""
    _save_message(user_id, "user", user_message)
    history = get_history(user_id, limit=20)
    system = _build_context(user_id)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    return {"system": system, "messages": messages}

def save_gordon_response(user_id: int, response: str):
    _save_message(user_id, "assistant", response)
