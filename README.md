# LeadFlow AI

LeadFlow AI is a production-grade, state-driven Revenue Operations (RevOps) engine designed for high-concurrency lead qualification. Unlike standard LLM wrappers, LeadFlow AI utilizes a deterministic state-machine architecture to ensure reliability, brand safety, and full observability in enterprise sales pipelines.

---

## Architectural pillars

- **State-driven workflow** — Built on LangGraph, using persistent Postgres checkpointers to ensure crash-resilient lead processing.
- **Deterministic brand guardrails** — Implements a multi-agent Draft-Critic architecture, ensuring 100% of outbound communication is validated against brand persona guidelines.
- **Full-stack observability** — Deep integration with LangSmith for end-to-end tracing, providing an audit trail for every lead decision.
- **Human-in-the-Loop (HITL) governance** — Integrated interrupt gates for high-value leads, ensuring manual sign-off before CRM synchronization.

---

## System architecture

The system operates as a 6-phase state machine:

```
Visitor message
      │
      ▼
 [input_node]            sanitise + load conversation history
      │
      ▼
 [enrichment_node]       automated firmographic enrichment (MCP-compliant)
      │
      ▼
 [qualification_node]    structured JSON intent scoring (0-100)
      │
      ├─ score >= 90 ──► [hitl_node]   interrupt() → wait for human approval
      │                       │
      │               approved / rejected
      │                       │
      └─ score < 90 ──────────┤
                              ▼
                    [drafting_node]    RAG-enabled response generation
                              │
                              ▼
                    [critic_node]      persona-based quality gate (auto-rewrite loop)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
             [deliver_node]    [manual_review_node]
        idempotent CRM sync      no lead is discarded
```

| Phase | Description |
|-------|-------------|
| 1 — Ingestion & Enrichment | Automated firmographic enrichment via MCP-compliant tools |
| 2 — Qualification | Structured JSON-based intent scoring (0-100) |
| 3 — Drafting | RAG-enabled response generation |
| 4 — Criticism | Persona-based quality gate with auto-rewrite loop |
| 5 — Governance | Human-in-the-Loop approval for high-intent prospects |
| 6 — Delivery | Idempotent CRM synchronization |

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph, LangChain |
| API framework | FastAPI (async) |
| LLM | Groq — Llama 3.3 70B |
| Vector storage | Qdrant |
| Database | PostgreSQL (AsyncPostgresSaver checkpointer) |
| Embeddings | FastEmbed (all-MiniLM-L6-v2) |
| Observability | LangSmith |
| Auth | JWT + bcrypt |
| Validation | Pydantic v2 |

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/ispastro/leadflow.git
cd leadflow/backend

# 2. Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Set GROQ_API_KEY, QDRANT_URL, QDRANT_API_KEY, JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD
# DATABASE_URL is not required — app uses SQLite

# 4. Create SQLite schema
python scripts/migrate_revops.py

# 5. Launch
uvicorn main:app --reload
```

API: `http://localhost:8000`
Docs: `http://localhost:8000/docs` (development only)

---

## Key endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/graph/invoke` | — | Run the RevOps pipeline for a session |
| `GET`  | `/api/graph/state/{session_id}` | JWT | Live graph state snapshot |
| `POST` | `/api/graph/approve/{session_id}` | JWT | Submit HITL approval decision |
| `POST` | `/api/auth/login` | — | Get JWT token |
| `GET`  | `/api/leads` | JWT | All captured leads with qualification data |
| `GET`  | `/api/analytics` | JWT | Dashboard metrics |
| `GET`  | `/api/knowledge` | JWT | Knowledge base documents |
| `POST` | `/api/ingest/file` | JWT | Upload a file (PDF, DOCX, TXT, MD) and index it |
| `POST` | `/api/ingest/text` | JWT | Ingest plain text via JSON body |
| `GET`  | `/api/ingest/status` | JWT | Vector collection stats |
| `GET`  | `/health` | — | Health check |

---

## Production governance

This system is designed for auditability. Every lead processed is logged with a unique `thread_id`, and all internal AI reasoning is captured via LangSmith traces. No lead is discarded — all failures are routed to `manual_review_node` for human intervention.

The fail-safe routing guarantees:

- Enrichment failure → pipeline continues with null fields
- Qualification error → routed to `manual_review_node`
- Critic max retries exceeded → routed to `manual_review_node`
- HITL rejection → routed to `manual_review_node`
- Any unhandled exception → lead upserted with `is_manual_review=True`
