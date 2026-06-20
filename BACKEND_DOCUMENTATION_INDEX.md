# LeadFlow Backend - Complete Documentation Index

## 📚 Documentation Structure

This comprehensive backend documentation is split into 4 detailed parts:

### [Part 1: Architecture & Chat Flow](BACKEND_DOCUMENTATION.md)
- Architecture Overview
- Application Startup Flow
- **Complete Chat Conversation Pipeline** (11 detailed steps)
- State Machine Logic
- RAG Pipeline Breakdown

### [Part 2: Database & Services](BACKEND_DOCUMENTATION_PART2.md)
- Database Layer & Connection Pooling
- Database Tables Schema
- Database Operations (Conversations, Messages, Leads)
- Services Layer (Groq, Qdrant, FastEmbed, Email)

### [Part 3: Auth, Analytics & APIs](BACKEND_DOCUMENTATION_PART3.md)
- JWT Authentication Flow
- Analytics System (4 metrics types)
- Complete API Endpoints Reference
- Utility Functions

### [Part 4: Deployment & Scripts](BACKEND_DOCUMENTATION_PART4.md)
- Docker & Heroku Deployment
- Database Setup Scripts
- Knowledge Ingestion
- Environment Configuration
- Troubleshooting & Performance

---

## 🚀 Quick Start Guide

### 1. Setup Environment
```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```bash
python scripts/setup_database.py
python scripts/ingest_knowledge.py
```

### 4. Run Server
```bash
uvicorn main:app --reload --port 8000
```

### 5. Test API
```bash
curl http://localhost:8000/health
```

---

## 🏗️ System Architecture at a Glance

```
┌─────────────────────────────────────────────────────┐
│                    Frontend Layer                    │
│  ┌──────────────┐              ┌─────────────────┐  │
│  │   Widget     │              │   Dashboard     │  │
│  │  (React)     │              │   (React)       │  │
│  └──────┬───────┘              └────────┬────────┘  │
└─────────┼──────────────────────────────┼───────────┘
          │                              │
          │ POST /api/chat              │ GET /api/*
          │                              │
┌─────────▼──────────────────────────────▼───────────┐
│              Backend (FastAPI)                      │
│  ┌────────────────────────────────────────────┐   │
│  │  API Layer (8 routers)                     │   │
│  │  - /api/chat          - /api/analytics     │   │
│  │  - /api/leads         - /api/conversations │   │
│  │  - /api/auth          - /api/knowledge     │   │
│  └────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────┐   │
│  │  Core Layer                                │   │
│  │  - State Machine    - RAG Pipeline         │   │
│  │  - Analytics        - Embeddings           │   │
│  └────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────┐   │
│  │  Database Layer (Connection Pool)          │   │
│  │  - Conversations    - Leads                │   │
│  │  - Messages         - Knowledge            │   │
│  └────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────┐   │
│  │  Services Layer                            │   │
│  │  - Groq AI          - Qdrant               │   │
│  │  - Email            - FastEmbed            │   │
│  └────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
          │           │              │
          │           │              │
          ▼           ▼              ▼
    ┌─────────┐ ┌──────────┐ ┌────────────┐
    │PostgreSQL│ │  Qdrant  │ │  Groq AI   │
    │(Supabase)│ │  Cloud   │ │    API     │
    └─────────┘ └──────────┘ └────────────┘
```

---

## 🔄 Request Flow Summary

### User Sends Message: "What are your pricing plans?"

#### Step 1: Database Operations (~50ms)
```
1. Get/create conversation by session_id
2. Load last 4 messages for context
3. Count total user messages
4. Save user message to database
```

#### Step 2: State Machine (~100ms)
```
1. Current stage: DISCOVERY
2. Detect intent using Groq: "HIGH_INTEREST" (pricing question)
3. Transition: DISCOVERY → INTENT_DETECTED
4. No email extracted yet
```

#### Step 3: RAG Pipeline (~300-400ms)
```
1. Embed query using FastEmbed (30ms)
2. Search Qdrant for pricing docs (50ms)
3. Build system prompt with context
4. Call Groq API with conversation history (200-300ms)
5. Return AI response
```

#### Step 4: Post-Processing (~50ms)
```
1. Update conversation stage to INTENT_DETECTED
2. Save AI response to database
3. Return response to frontend
```

#### Response:
```json
{
  "response": "We offer 3 pricing tiers:\n- Starter: $49/month...",
  "session_id": "uuid-...",
  "should_capture_lead": false,
  "lead_captured": false,
  "conversation_state": "INTENT_DETECTED"
}
```

**Total Time**: ~450-600ms

---

## 📊 Database Schema Summary

### conversations
- Tracks each user session
- Stores current conversation stage
- Tracks if email captured

### messages
- All chat messages (user + assistant)
- Linked to conversation
- Used for history context

### leads
- Captured lead information
- Email, name, intent, quality
- Linked to conversation

### businesses
- Multi-tenancy support
- Each business isolated

### knowledge_base (optional)
- Vector embeddings for RAG
- Alternative to Qdrant

---

## 🎯 Key Components Deep Dive

### 1. State Machine (Conversation Stages)
```
NEW → GREETED → DISCOVERY → INTENT_DETECTED → 
EMAIL_REQUESTED → CAPTURED → POST_CAPTURE
```

**Transitions:**
- NEW → GREETED: First user message
- GREETED/DISCOVERY → INTENT_DETECTED: High interest detected
- INTENT_DETECTED → EMAIL_REQUESTED: After answering question
- EMAIL_REQUESTED → CAPTURED: Email found in message

### 2. RAG Pipeline
```
User Query → Embed (FastEmbed) → Search (Qdrant) → 
Build Prompt → Groq API → AI Response
```

**Components:**
- **FastEmbed**: 384-dim vectors, ~30ms
- **Qdrant**: Cosine similarity search, ~50ms
- **Groq**: Llama 3.3 70B, ~200-300ms

### 3. Lead Capture
```
Email Detected → Extract Name → Determine Intent → 
Save to DB → Send Email Notification → Update Stage
```

**Intent Types:**
- pricing, demo, integration, unprompted, other

**Quality Levels:**
- HOT, WARM, COLD, MEDIUM

### 4. Analytics
```
Database Queries → Aggregate Metrics → 
Calculate Rates → Format Time Series → Return JSON
```

**Metrics:**
- Total conversations
- Total leads
- Conversion rate
- Avg messages per conversation
- Lead quality breakdown
- Intent breakdown
- Time series data

---

## 🔌 API Endpoints Quick Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/api/auth/login` | No | Login, get JWT |
| GET | `/api/auth/me` | Yes | Get current user |
| POST | `/api/chat` | No | Send message, get AI response |
| GET | `/api/leads` | No | Get all leads |
| GET | `/api/conversations` | No | Get all conversations |
| GET | `/api/conversations/{id}` | No | Get conversation details |
| GET | `/api/analytics?days=30` | No | Get analytics data |
| GET | `/api/knowledge` | No | Get knowledge docs |

**Authentication**: Bearer token in `Authorization` header

---

## 🛠️ Configuration Quick Reference

### Required Environment Variables
```bash
DATABASE_URL=postgresql://...
GROQ_API_KEY=gsk_...
QDRANT_URL=https://...
QDRANT_API_KEY=...
ALLOWED_ORIGINS=https://yourdomain.com
JWT_SECRET=your-secret-key
```

### Optional Environment Variables
```bash
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAILS=sales@company.com
ADMIN_EMAIL=admin@leadflow.com
ADMIN_PASSWORD=admin123
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Update environment variables
- [ ] Change default admin password
- [ ] Generate strong JWT secret
- [ ] Configure CORS origins
- [ ] Setup email notifications
- [ ] Test database connection

### Heroku Deployment
```bash
heroku create leadflow-backend
heroku stack:set container -a leadflow-backend
heroku config:set DATABASE_URL="..." -a leadflow-backend
heroku config:set GROQ_API_KEY="..." -a leadflow-backend
heroku config:set QDRANT_URL="..." -a leadflow-backend
heroku config:set QDRANT_API_KEY="..." -a leadflow-backend
git subtree push --prefix backend heroku main
```

### Post-Deployment
- [ ] Run database setup script
- [ ] Ingest knowledge base
- [ ] Test health endpoint
- [ ] Test chat endpoint
- [ ] Verify email notifications
- [ ] Monitor logs

---

## 🔍 Troubleshooting Quick Guide

### Database Connection Failed
```bash
# Test connection
psql $DATABASE_URL

# Check pool status
heroku logs --tail -a leadflow-backend | grep "Database"
```

### Qdrant Not Working
```bash
# Verify credentials
curl -X GET "$QDRANT_URL/collections" -H "api-key: $QDRANT_API_KEY"

# Re-ingest knowledge
python scripts/ingest_knowledge.py
```

### Slow Response Times
- Check Groq API quota
- Monitor database query times
- Review connection pool size
- Add response caching
- Optimize Qdrant search

### CORS Errors
- Add frontend URL to `ALLOWED_ORIGINS`
- Restart backend
- Clear browser cache
- Check browser console

---

## 📈 Performance Benchmarks

### Typical Response Times
- Health check: ~5ms
- Chat message (no RAG): ~100ms
- Chat message (with RAG): ~450-600ms
- Analytics query: ~50-100ms
- Lead creation: ~30ms

### Database Operations
- Get conversation: ~10ms
- Save message: ~15ms
- Create lead: ~20ms
- Get analytics: ~50ms

### AI Operations
- FastEmbed: ~30ms
- Qdrant search: ~50ms
- Groq API: ~200-300ms

### Bottlenecks
1. Groq API call (200-300ms) - **Largest**
2. Qdrant search (50ms)
3. Database queries (50ms)
4. FastEmbed (30ms)

---

## 🔐 Security Checklist

- [ ] JWT secrets rotated regularly
- [ ] HTTPS only in production
- [ ] Database connections use SSL
- [ ] Input validation on all endpoints
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] Passwords hashed with bcrypt
- [ ] Secrets not in version control
- [ ] Admin password changed from default
- [ ] Email notifications secured

---

## 📦 Tech Stack Summary

### Core Framework
- **FastAPI**: Async Python web framework
- **Uvicorn**: ASGI server

### Database
- **PostgreSQL**: Main database (Supabase)
- **psycopg2**: Database driver
- **Connection Pool**: 2-10 connections

### AI & ML
- **Groq**: Llama 3.3 70B (ultra-fast)
- **Qdrant**: Vector database
- **FastEmbed**: Sentence embeddings

### Authentication
- **JWT**: JSON Web Tokens
- **bcrypt**: Password hashing

### Email
- **SMTP**: Email notifications
- **HTML Templates**: Rich email format

### Deployment
- **Docker**: Containerization
- **Heroku**: Backend hosting
- **Vercel**: Frontend hosting

---

## 📚 File Structure Reference

```
backend/
├── main.py                    # App entry, startup
├── config.py                  # Settings, env vars
├── requirements.txt           # Dependencies
├── Dockerfile                 # Docker config
├── Procfile                   # Heroku config
│
├── app/
│   ├── api/                   # Route handlers
│   │   ├── chat.py           # Chat endpoint ⭐
│   │   ├── auth.py           # Login, JWT
│   │   ├── leads.py          # Leads CRUD
│   │   ├── analytics.py      # Analytics
│   │   ├── conversations.py  # Conversation history
│   │   └── health.py         # Health check
│   │
│   ├── core/                  # Business logic
│   │   ├── rag.py            # RAG pipeline ⭐
│   │   ├── state_machine.py  # Conversation stages ⭐
│   │   ├── embeddings.py     # FastEmbed
│   │   └── analytics.py      # Analytics logic
│   │
│   ├── db/                    # Database ops
│   │   ├── pg_direct.py      # Connection pool ⭐
│   │   ├── conversations.py  # Conversation CRUD
│   │   ├── messages.py       # Message CRUD
│   │   └── leads.py          # Lead CRUD
│   │
│   ├── services/              # External services
│   │   ├── groq_client.py    # Groq AI
│   │   ├── qdrant_service.py # Qdrant
│   │   ├── email_service.py  # SMTP
│   │   └── auth_service.py   # JWT, bcrypt
│   │
│   ├── models/                # Pydantic models
│   │   ├── chat.py           # Request/response
│   │   └── lead.py           # Lead model
│   │
│   └── utils/                 # Helpers
│       ├── text_processing.py # Extract email/name
│       └── prompts.py         # System prompts
│
└── scripts/                   # Setup scripts
    ├── setup_database.py      # Create tables
    ├── ingest_knowledge.py    # Load knowledge ⭐
    └── migrate_schema.py      # Migrations
```

⭐ = Most critical files

---

## 🎓 Learning Path

### Beginner
1. Read Part 1: Understand architecture
2. Study chat.py: Main request flow
3. Explore state_machine.py: Conversation logic
4. Review database schema

### Intermediate
1. Deep dive into RAG pipeline
2. Understand connection pooling
3. Study Qdrant vector search
4. Explore analytics queries

### Advanced
1. Optimize performance
2. Implement caching strategies
3. Add monitoring/logging
4. Scale horizontally
5. Custom AI training

---

## 📞 Getting Help

### Resources
- **Live Demo**: https://lead-flow-cgkd.vercel.app/
- **Dashboard**: https://lead-flow-roan.vercel.app/
- **API Docs**: https://your-backend.herokuapp.com/docs

### Documentation Parts
1. [Architecture & Chat Flow](BACKEND_DOCUMENTATION.md)
2. [Database & Services](BACKEND_DOCUMENTATION_PART2.md)
3. [Auth, Analytics & APIs](BACKEND_DOCUMENTATION_PART3.md)
4. [Deployment & Scripts](BACKEND_DOCUMENTATION_PART4.md)

### Support
- GitHub Issues: Report bugs
- Email: haileasaye@gmail.com

---

## ✅ Next Steps

1. **Read Part 1** to understand the complete chat flow
2. **Set up local environment** using Quick Start Guide
3. **Explore the code** following the file structure
4. **Deploy** using Part 4 deployment guide
5. **Customize** knowledge base and prompts
6. **Monitor** performance and logs

---

**Built with ❤️ for developers who want to understand every detail**

*Last Updated: January 2024*
