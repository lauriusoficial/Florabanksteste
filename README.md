# 🌿 Flora Banks

Sistema financeiro pessoal com agente Gordon.

## Instalação no Termux (Android)

```bash
pkg update && pkg upgrade
pkg install python
pip install flask requests

cd flora-banks
python main.py
```

Acesse no navegador: `http://localhost:5000`

## Ativar Gordon (opcional)

```bash
export ANTHROPIC_API_KEY="sua_chave_aqui"
python main.py
```

Sem a chave, Gordon funciona offline com mensagem de aviso.

## Estrutura

```
flora-banks/
├── core/
│   ├── database.py     # SQLite, criação de tabelas
│   └── auth.py         # Login seguro, sessões
├── modules/
│   ├── transactions.py # Entradas, saídas, saldo, extrato
│   ├── notes.py        # Anotações CRUD
│   └── gordon.py       # Agente financeiro, contexto
├── api/
│   └── routes.py       # Endpoints REST
├── frontend/
│   └── index.html      # PWA completo (HTML/CSS/JS)
├── main.py             # Servidor Flask
├── requirements.txt
└── flora.db            # Banco SQLite (gerado ao rodar)
```

## Módulos

| Módulo | Responsabilidade |
|--------|-----------------|
| `core/database.py` | Conexão, inicialização do banco |
| `core/auth.py` | Hash de senha, tokens de sessão |
| `modules/transactions.py` | CRUD de transações, saldo, extrato |
| `modules/notes.py` | CRUD de anotações |
| `modules/gordon.py` | Contexto financeiro para IA, histórico de chat |
| `api/routes.py` | Todos os endpoints REST |
| `frontend/index.html` | Interface PWA completa |

## Futuras integrações

- Gateway de pagamento: adicionar rotas em `api/routes.py`
- Autenticação OAuth: expandir `core/auth.py`
- Exportar CSV/PDF: novo módulo `modules/export.py`
- Notificações: integrar com serviço externo via `requests`
