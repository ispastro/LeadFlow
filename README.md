# AI Sales & Support Agent - Backend

Production-ready FastAPI backend for AI-powered lead generation and customer support.

## Tech Stack

- **Framework**: FastAPI
- **AI Chat**: Groq (Llama 3.1 70B)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Vector Search**: pgvector

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### 3. Load Knowledge Base

Run the ingestion script to load your business data:

```bash
python scripts/ingest_knowledge.py
```

### 4. Run Server

```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `POST /api/chat` - Chat with AI agent
- `GET /api/leads` - Get captured leads
- `GET /health` - Health check

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Business logic
│   ├── services/     # External services
│   ├── models/       # Pydantic models
│   ├── db/           # Database operations
│   └── utils/        # Utilities
├── scripts/          # One-time scripts
└── main.py           # FastAPI entry point
```

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload

# Test RAG pipeline
python scripts/test_rag.py
```
