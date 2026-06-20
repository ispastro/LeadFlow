# LeadFlow Backend - Part 4: Deployment, Scripts & Configuration

## Deployment Architecture

### Production Stack
```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│  ┌──────────────┐          ┌─────────────────┐ │
│  │   Widget     │          │   Dashboard     │ │
│  │  (Vercel)    │          │   (Vercel)      │ │
│  └──────┬───────┘          └────────┬────────┘ │
└─────────┼──────────────────────────┼───────────┘
          │                          │
          │ HTTPS                    │ HTTPS
          ▼                          ▼
┌─────────────────────────────────────────────────┐
│              Backend (Heroku)                    │
│  ┌──────────────────────────────────────────┐  │
│  │        FastAPI + Uvicorn                 │  │
│  │          (Docker Container)              │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
          │           │              │
          │           │              │
          ▼           ▼              ▼
    ┌─────────┐ ┌──────────┐ ┌────────────┐
    │PostgreSQL│ │  Qdrant  │ │  Groq AI   │
    │(Supabase)│ │  Cloud   │ │    API     │
    └─────────┘ └──────────┘ └────────────┘
```

---

## Docker Deployment

### Dockerfile

**File**: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Build & Run Locally
```bash
# Build image
docker build -t leadflow-backend .

# Run container
docker run -p 8000:8000 --env-file .env leadflow-backend
```

---

## Heroku Deployment

### heroku.yml

**File**: `backend/heroku.yml`

```yaml
build:
  docker:
    web: Dockerfile
run:
  web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Deployment Steps

#### 1. Login to Heroku
```bash
heroku login
```

#### 2. Create App
```bash
heroku create leadflow-backend
heroku stack:set container -a leadflow-backend
```

#### 3. Set Environment Variables
```bash
heroku config:set DATABASE_URL="postgresql://..." -a leadflow-backend
heroku config:set GROQ_API_KEY="gsk_..." -a leadflow-backend
heroku config:set QDRANT_URL="https://..." -a leadflow-backend
heroku config:set QDRANT_API_KEY="..." -a leadflow-backend
heroku config:set JWT_SECRET="your-secret-key" -a leadflow-backend
heroku config:set ALLOWED_ORIGINS="https://..." -a leadflow-backend
```

#### 4. Deploy (from monorepo)
```bash
# Add Heroku remote
heroku git:remote -a leadflow-backend

# Deploy using git subtree (if monorepo)
git subtree push --prefix backend heroku main

# Or if backend is root
git push heroku main
```

#### 5. View Logs
```bash
heroku logs --tail -a leadflow-backend
```

### Heroku Procfile (alternative)

**File**: `backend/Procfile`

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Database Setup Scripts

### 1. Setup Database Schema

**File**: `backend/scripts/setup_database.py`

```python
import psycopg2
from config import settings

def setup_database():
    """Create all necessary tables"""
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()
    
    # Create businesses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            api_key VARCHAR(255) UNIQUE,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    # Create conversations table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id VARCHAR(255) UNIQUE NOT NULL,
            business_id UUID REFERENCES businesses(id),
            stage VARCHAR(50) DEFAULT 'NEW',
            email_captured BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_conversations_session 
        ON conversations(session_id);
        
        CREATE INDEX IF NOT EXISTS idx_conversations_updated 
        ON conversations(updated_at DESC);
    """)
    
    # Create messages table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID REFERENCES conversations(id),
            business_id UUID REFERENCES businesses(id),
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_messages_conversation 
        ON messages(conversation_id, created_at);
        
        CREATE INDEX IF NOT EXISTS idx_messages_created 
        ON messages(created_at DESC);
    """)
    
    # Create leads table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            conversation_id UUID REFERENCES conversations(id),
            business_id UUID REFERENCES businesses(id),
            email VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            intent_trigger VARCHAR(100),
            quality VARCHAR(20),
            captured_via VARCHAR(50),
            metadata JSONB,
            captured_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_leads_email 
        ON leads(email);
        
        CREATE INDEX IF NOT EXISTS idx_leads_captured 
        ON leads(captured_at DESC);
        
        CREATE INDEX IF NOT EXISTS idx_leads_conversation 
        ON leads(conversation_id);
    """)
    
    # Insert default business
    cur.execute("""
        INSERT INTO businesses (name, api_key)
        VALUES ('Default Business', 'default_api_key_123')
        ON CONFLICT (api_key) DO NOTHING;
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Database schema created successfully!")

if __name__ == "__main__":
    setup_database()
```

**Run:**
```bash
cd backend
python scripts/setup_database.py
```

---

### 2. Setup Knowledge Base Table (PostgreSQL with pgvector)

**File**: `backend/scripts/setup_knowledge_table.py`

```python
import psycopg2
from config import settings

def setup_knowledge_table():
    """Create knowledge_base table with vector support"""
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()
    
    # Enable pgvector extension
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Create knowledge_base table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content TEXT NOT NULL,
            embedding VECTOR(384),
            metadata JSONB,
            source VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Create index for vector similarity search
        CREATE INDEX IF NOT EXISTS idx_knowledge_embedding 
        ON knowledge_base 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Knowledge base table created with vector support!")

if __name__ == "__main__":
    setup_knowledge_table()
```

---

### 3. Knowledge Ingestion Script

**File**: `backend/scripts/ingest_knowledge.py`

```python
from app.core.embeddings import embedding_service
from app.services.qdrant_service import qdrant_service
from config import settings
import uuid

def ingest_knowledge():
    """Load knowledge base into Qdrant"""
    
    print("🚀 Starting knowledge ingestion...")
    
    # Configure Qdrant
    qdrant_service.configure(settings.qdrant_url, settings.qdrant_api_key)
    
    # Define knowledge documents
    documents = [
        {
            "content": """LeadFlow AI is a SaaS platform that converts website visitors 
            into qualified leads automatically using AI-powered chat. It provides 24/7 
            automated customer engagement, lead qualification, and real-time analytics.""",
            "source": "company_overview",
            "category": "general"
        },
        {
            "content": """LeadFlow AI offers three pricing tiers:
            
            Starter Plan - $49/month:
            - Up to 1,000 conversations/month
            - Email notifications
            - Basic analytics
            - 1 website integration
            
            Professional Plan - $99/month:
            - Up to 5,000 conversations/month
            - Priority email notifications
            - Advanced analytics & reports
            - Unlimited website integrations
            - Custom branding
            
            Enterprise Plan - Custom pricing:
            - Unlimited conversations
            - Dedicated account manager
            - Custom AI training
            - API access
            - White-label solution
            
            All plans include a 14-day free trial with no credit card required.""",
            "source": "pricing",
            "category": "pricing"
        },
        {
            "content": """Key Features of LeadFlow AI:
            
            1. AI-Powered Chat - Intelligent conversations using advanced LLMs with 
               retrieval-augmented generation (RAG) for accurate responses
            
            2. Lead Capture - Automatically detects interest and captures contact 
               information at the optimal moment
            
            3. Analytics Dashboard - Track conversations, leads, conversion rates, 
               and user engagement with beautiful visualizations
            
            4. Email Notifications - Instant alerts when leads are captured with 
               full conversation context
            
            5. Easy Integration - Drop-in chat widget that works on any website 
               with just a few lines of code
            
            6. Conversation History - Full chat logs with lead context for follow-up
            
            7. Intent Detection - Smart classification of user intent (pricing, demo, 
               integration inquiries)
            
            8. Multi-channel Support - Widget can be embedded on multiple websites""",
            "source": "features",
            "category": "features"
        },
        {
            "content": """LeadFlow AI integrates seamlessly with popular CRM and 
            marketing tools including:
            - Salesforce
            - HubSpot
            - Pipedrive
            - Zapier (connects to 5,000+ apps)
            - Slack (for real-time notifications)
            - Google Sheets (for lead exports)
            
            Integration is available on Professional and Enterprise plans. Setup 
            takes less than 5 minutes with our guided wizard.""",
            "source": "integrations",
            "category": "integrations"
        },
        {
            "content": """Getting started with LeadFlow AI is simple:
            
            Step 1: Sign up for a free 14-day trial at https://leadflow.ai/signup
            Step 2: Customize your chat widget appearance and welcome message
            Step 3: Copy the embed code from your dashboard
            Step 4: Paste the code before the closing </body> tag on your website
            Step 5: Test the chat widget and start capturing leads!
            
            No technical expertise required. Our support team is available to help 
            with setup via email or live chat.""",
            "source": "getting_started",
            "category": "onboarding"
        },
        {
            "content": """LeadFlow AI Demo:
            
            You can try a live demo at https://lead-flow-cgkd.vercel.app/
            
            To request a personalized demo for your business:
            1. Provide your email address
            2. Our team will set up a custom demo environment
            3. Schedule a 30-minute walkthrough with our product specialist
            4. Get answers to all your questions
            
            Enterprise demos can include custom AI training on your specific 
            business information.""",
            "source": "demo",
            "category": "demo"
        }
    ]
    
    # Generate embeddings and prepare for Qdrant
    print(f"📦 Processing {len(documents)} documents...")
    
    qdrant_documents = []
    for i, doc in enumerate(documents):
        print(f"  Embedding document {i+1}/{len(documents)}...")
        
        embedding = embedding_service.embed_text(doc["content"])
        
        qdrant_documents.append({
            "id": str(uuid.uuid4()),
            "content": doc["content"],
            "embedding": embedding,
            "source": doc["source"],
            "category": doc["category"],
            "metadata": {
                "source": doc["source"],
                "category": doc["category"]
            }
        })
    
    # Upload to Qdrant
    print(f"☁️  Uploading to Qdrant Cloud...")
    qdrant_service.add_documents(qdrant_documents)
    
    # Verify
    count = qdrant_service.count_documents()
    print(f"✅ Knowledge ingestion complete! {count} documents in Qdrant.")

if __name__ == "__main__":
    ingest_knowledge()
```

**Run:**
```bash
cd backend
python scripts/ingest_knowledge.py
```

---

## Environment Configuration

### .env.example

**File**: `backend/.env.example`

```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database

# Groq AI
GROQ_API_KEY=gsk_your_api_key_here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
USE_QDRANT=true

# Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production

# CORS (comma-separated URLs)
ALLOWED_ORIGINS=https://yourdomain.com,https://dashboard.yourdomain.com

# Email Notifications (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
NOTIFICATION_EMAILS=sales@yourdomain.com,team@yourdomain.com

# Dashboard URL (for email links)
DASHBOARD_URL=https://dashboard.yourdomain.com

# JWT Authentication
JWT_SECRET=your-secure-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Admin Credentials
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=change-this-password
```

### Configuration Loading

**File**: `backend/config.py`

```python
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Groq
    groq_api_key: str
    
    # Qdrant
    qdrant_url: str
    qdrant_api_key: str
    use_qdrant: bool = True
    
    # Server
    port: int = 8000
    host: str = "0.0.0.0"
    environment: str = "development"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Email (Optional)
    smtp_host: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    notification_emails: Optional[str] = None
    dashboard_url: Optional[str] = "http://localhost:3001"
    
    # Auth
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    admin_email: str = "admin@leadflow.com"
    admin_password: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

settings = Settings()
```

---

## Requirements

### requirements.txt

**File**: `backend/requirements.txt`

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.25.0
python-multipart==0.0.6

# Database
psycopg2-binary==2.9.9
pgvector==0.2.4

# AI & Embeddings
groq==0.4.2
fastembed==0.2.2

# Vector Database
qdrant-client==1.7.0

# Auth
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Configuration
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Utilities
requests==2.31.0

# Email
email-validator==2.1.0
```

**Install:**
```bash
pip install -r requirements.txt
```

---

## Monitoring & Logging

### Logging Configuration

Add to `main.py`:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)
```

### Performance Monitoring

Add timing middleware:

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.2f}s")
    return response
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```
ERROR: could not connect to server
```

**Solution:**
- Check `DATABASE_URL` in `.env`
- Verify Supabase credentials
- Ensure IP is whitelisted in Supabase dashboard
- Test connection: `psql $DATABASE_URL`

#### 2. Qdrant Connection Timeout
```
ERROR: Failed to connect to Qdrant
```

**Solution:**
- Verify `QDRANT_URL` and `QDRANT_API_KEY`
- Check Qdrant Cloud dashboard
- Ensure collection exists (run `ingest_knowledge.py`)
- Test with: `curl -X GET "https://your-cluster.qdrant.io/collections" -H "api-key: ..."`

#### 3. Groq API Rate Limits
```
ERROR: Rate limit exceeded
```

**Solution:**
- Check Groq API quota at https://console.groq.com/
- Implement exponential backoff
- Add rate limiting middleware
- Consider caching responses

#### 4. CORS Errors in Frontend
```
Access to fetch blocked by CORS policy
```

**Solution:**
- Add frontend URL to `ALLOWED_ORIGINS` in `.env`
- Restart backend server
- Check browser console for exact origin
- Verify CORS middleware is configured

#### 5. Email Notifications Not Sending
```
WARNING: Email service not configured
```

**Solution:**
- Set all SMTP variables in `.env`
- For Gmail, use App Password (not regular password)
- Enable "Less secure app access" or use OAuth2
- Check spam folder

---

## Performance Optimization

### 1. Database Query Optimization

**Use Indexes:**
```sql
CREATE INDEX idx_messages_conversation_created 
ON messages(conversation_id, created_at DESC);
```

**Connection Pooling:**
- Use `get_db_connection()` context manager
- Set appropriate pool size: `minconn=2, maxconn=10`
- Monitor active connections

### 2. RAG Pipeline Optimization

**Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_embed(text: str):
    return embedding_service.embed_text(text)
```

**Batch Processing:**
```python
# Instead of:
for text in texts:
    embed = embedding_service.embed_text(text)

# Use:
embeddings = embedding_service.embed_batch(texts)
```

### 3. Response Caching

**Redis Cache (Optional):**
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## Security Best Practices

### 1. Environment Variables
- Never commit `.env` to git
- Use different secrets for dev/prod
- Rotate JWT secrets regularly
- Use strong passwords (16+ chars)

### 2. Database Security
- Use connection pooling
- Sanitize all inputs (parameterized queries)
- Enable SSL for database connections
- Implement rate limiting

### 3. API Security
- Enable HTTPS only
- Implement request validation
- Add rate limiting middleware
- Log security events

### 4. CORS Configuration
- Only allow specific origins
- Don't use wildcard `*` in production
- Validate origin headers

---

## Testing

### Unit Tests Example

```python
import pytest
from app.utils.text_processing import extract_email, extract_name

def test_extract_email():
    assert extract_email("My email is test@example.com") == "test@example.com"
    assert extract_email("No email here") is None

def test_extract_name():
    assert extract_name("I'm John Doe") == "John Doe"
    assert extract_name("Hi there") is None

def test_state_transitions():
    from app.core.state_machine import state_machine, ConversationStage
    
    new_stage, email = state_machine.transition(
        current_stage=ConversationStage.NEW,
        message="Hello",
        email_captured=False,
        message_count=0
    )
    
    assert new_stage == ConversationStage.GREETED
    assert email is None
```

**Run tests:**
```bash
pytest tests/ -v
```

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check API response times
- Verify email notifications

**Weekly:**
- Review analytics data
- Check database size
- Update knowledge base

**Monthly:**
- Rotate secrets/credentials
- Review security logs
- Update dependencies
- Database backup verification

---

## Summary: Complete Backend Flow

```
                    Application Startup
                           ↓
    ┌──────────────────────────────────────────┐
    │  Initialize Connection Pool (PostgreSQL)  │
    │  Load FastEmbed Model (384-dim vectors)   │
    │  Connect to Qdrant Cloud                  │
    │  Configure Email Service (SMTP)           │
    └──────────────────────────────────────────┘
                           ↓
                   Ready for Requests
                           ↓
    ┌──────────────────────────────────────────┐
    │        Incoming Request: POST /api/chat   │
    └──────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────┐
    │     1. Database: Get/Create Conversation  │
    │        - Load state & history             │
    │        - Save user message                │
    └──────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────┐
    │     2. State Machine: Determine Action    │
    │        - Detect intent (Groq)             │
    │        - Extract email (Regex)            │
    │        - Transition stage                 │
    └──────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────┐
    │     3. RAG Pipeline: Generate Response    │
    │        - Embed query (FastEmbed)          │
    │        - Search context (Qdrant)          │
    │        - Build prompt                     │
    │        - Call Groq API                    │
    └──────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────┐
    │     4. Lead Capture (if applicable)       │
    │        - Save to database                 │
    │        - Send email notification          │
    └──────────────────────────────────────────┘
                           ↓
    ┌──────────────────────────────────────────┐
    │     5. Save Response & Return to Client   │
    └──────────────────────────────────────────┘
```

**End-to-End Latency**: ~450-600ms
- Database: ~50ms
- State Machine: ~100ms (with intent detection)
- RAG Pipeline: ~300-400ms
  - Embedding: ~30ms
  - Qdrant: ~50ms
  - Groq: ~200-300ms

---

## Quick Reference Commands

```bash
# Local Development
uvicorn main:app --reload --port 8000

# Database Setup
python scripts/setup_database.py
python scripts/ingest_knowledge.py

# Docker
docker build -t leadflow-backend .
docker run -p 8000:8000 --env-file .env leadflow-backend

# Heroku
heroku logs --tail -a leadflow-backend
heroku restart -a leadflow-backend
heroku config -a leadflow-backend

# Testing
pytest tests/ -v
```

