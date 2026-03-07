# AI Knowledge Assistant Backend

A production-style FastAPI backend where users upload documents, ask questions, and an AI agent decides how to answer — using RAG search, database queries, or summarization.

## Architecture

```
Client
  ↓
FastAPI API
  ↓
Agent Orchestrator (brain)
  ├─ LLM reasoning (GPT-4o-mini)
  ├─ Tool Router
  ├─ RAG retriever (FAISS)
  ├─ DB queries (SQLite/PostgreSQL)
  └─ State manager
  ↓
Response
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/upload_docs` | Upload PDF, TXT, or DOCX |
| `POST` | `/chat` | Ask a question (agent decides tool) |
| `GET` | `/history/{session_id}` | Get conversation history |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

## Quick Start

### 1. Clone & configure
```bash
cp .env .env.local
# Edit .env and add your OPENAI_API_KEY
```

### 2. Install & run locally
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Run with Docker
```bash
docker build -t ai-assistant .
docker run -p 8000:8000 --env-file .env ai-assistant
```

### 4. Test it
```bash
# Upload a document
curl -X POST http://localhost:8000/upload_docs \
  -F "file=@your_document.pdf" \
  -F "session_id=my-session"

# Ask a question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session", "message": "Summarize the key points"}'

# Get history
curl http://localhost:8000/history/my-session
```

## Project Structure

```
app/
├── main.py              # FastAPI app entry
├── config.py            # Settings from .env
├── api/                 # HTTP routes only
├── agent/               # Orchestrator + tool routing
├── tools/               # RAG, DB, summarizer, email
├── services/            # OpenAI, FAISS wrappers
├── ingestion/           # PDF→text→chunks→embeddings
├── database/            # SQLAlchemy models + CRUD
├── schemas/             # Pydantic request/response
└── utils/               # Logger, helpers
```

## Tools Available to the Agent

- **rag_search** — semantic search over uploaded documents
- **db_query** — query database for stats/metadata
- **summarizer** — LLM-powered text summarization
- **email_writer** — draft professional emails
- **direct_answer** — answer from model knowledge

## Tech Stack

- **FastAPI** + async/await
- **OpenAI** GPT-4o-mini + text-embedding-3-small
- **FAISS** for vector similarity search
- **SQLAlchemy** + SQLite (swap to PostgreSQL for prod)
- **Docker** for containerization
- **Loguru** for structured logging

## Run Tests
```bash
pytest tests/ -v
```
