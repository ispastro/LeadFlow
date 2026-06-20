# LeadFlow Backend - Part 2: Database, Services & APIs

## Database Layer

### Connection Pool Architecture

**File**: `backend/app/db/pg_direct.py`

#### Connection Pool Pattern
```python
# Global connection pool (thread-safe)
_connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=2,      # Minimum connections always open
    maxconn=10,     # Maximum concurrent connections
    dsn=database_url,
    keepalives=1,
    keepalives_idle=30,
    keepalives_interval=10,
    keepalives_count=5
)
```

**Benefits:**
- Reuses connections (no connection overhead per request)
- Thread-safe for async operations
- Health checks detect dead connections
- Automatic reconnection

#### Context Manager Pattern
```python
@contextmanager
def get_db_connection():
    conn = _connection_pool.getconn()
    
    try:
        # Health check
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        
        yield conn
    except Exception as e:
        _connection_pool.putconn(conn, close=True)
        raise
    finally:
        _connection_pool.putconn(conn)  # Return to pool
```

**Usage:**
```python
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM conversations WHERE id = %s", (conv_id,))
    result = cur.fetchone()
    cur.close()
```

---

### Database Tables Schema

#### 1. businesses
```sql
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```
**Purpose**: Multi-tenancy support (each business has isolated data)

#### 2. conversations
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    business_id UUID REFERENCES businesses(id),
    stage VARCHAR(50) DEFAULT 'NEW',
    email_captured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);
```
**Purpose**: Track each user session and conversation state

#### 3. messages
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    business_id UUID REFERENCES businesses(id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
```
**Purpose**: Store all chat messages with full history

#### 4. leads
```sql
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    business_id UUID REFERENCES businesses(id),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    intent_trigger VARCHAR(100),  -- 'pricing', 'demo', 'integration', 'other'
    quality VARCHAR(20),           -- 'HOT', 'WARM', 'COLD', 'MEDIUM'
    captured_via VARCHAR(50),      -- 'asked', 'unprompted'
    metadata JSONB,
    captured_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_captured ON leads(captured_at DESC);
CREATE INDEX idx_leads_conversation ON leads(conversation_id);
```
**Purpose**: Store captured leads with qualification data

#### 5. knowledge_base (if using PostgreSQL instead of Qdrant)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(384),  -- FastEmbed dimension
    metadata JSONB,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
```
**Purpose**: Vector storage for RAG (alternative to Qdrant)

---

### Database Operations

#### Conversations Module
**File**: `backend/app/db/conversations.py`

**1. Create Conversation**
```python
def create_conversation(session_id: str, business_id: str = None) -> Dict:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Get default business if not provided
        if not business_id:
            cur.execute("SELECT id FROM businesses WHERE api_key = 'default_api_key_123' LIMIT 1;")
            result = cur.fetchone()
            business_id = str(result[0]) if result else None
        
        cur.execute("""
            INSERT INTO conversations (session_id, business_id, stage, email_captured, created_at, updated_at)
            VALUES (%s, %s, 'NEW', FALSE, %s, %s)
            RETURNING id, session_id, business_id, stage, email_captured, created_at, updated_at
        """, (session_id, business_id, datetime.utcnow(), datetime.utcnow()))
        
        row = cur.fetchone()
        conn.commit()
        cur.close()
        
        return {
            'id': str(row[0]),
            'session_id': row[1],
            'business_id': str(row[2]),
            'stage': row[3],
            'email_captured': row[4],
            'created_at': row[5].isoformat(),
            'updated_at': row[6].isoformat()
        }
```

**2. Get or Create Conversation**
```python
def get_or_create_conversation(session_id: str) -> Dict:
    conversation = get_conversation_by_session(session_id)
    if conversation:
        return conversation
    return create_conversation(session_id)
```
**Pattern**: Idempotent operation (safe to call multiple times)

**3. Update Conversation Stage**
```python
def update_conversation_stage(conversation_id: str, stage: str, email_captured: bool = None):
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        if email_captured is not None:
            cur.execute("""
                UPDATE conversations
                SET stage = %s, email_captured = %s, updated_at = %s
                WHERE id = %s
            """, (stage, email_captured, datetime.utcnow(), conversation_id))
        else:
            cur.execute("""
                UPDATE conversations
                SET stage = %s, updated_at = %s
                WHERE id = %s
            """, (stage, datetime.utcnow(), conversation_id))
        
        conn.commit()
        cur.close()
```

---

#### Messages Module
**File**: `backend/app/db/messages.py`

**1. Create Message**
```python
def create_message(conversation_id: str, role: str, content: str) -> Dict:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Get business_id from conversation
        cur.execute("SELECT business_id FROM conversations WHERE id = %s", (conversation_id,))
        result = cur.fetchone()
        business_id = str(result[0]) if result else None
        
        cur.execute("""
            INSERT INTO messages (conversation_id, business_id, role, content, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, conversation_id, business_id, role, content, created_at
        """, (conversation_id, business_id, role, content, datetime.utcnow()))
        
        row = cur.fetchone()
        conn.commit()
        cur.close()
        
        return {
            'id': str(row[0]),
            'conversation_id': str(row[1]),
            'role': row[3],
            'content': row[4],
            'created_at': row[5].isoformat()
        }
```

**2. Get Conversation History**
```python
def get_conversation_history(conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
    messages = get_conversation_messages(conversation_id)
    
    # Get last N messages
    recent_messages = messages[-limit:] if len(messages) > limit else messages
    
    # Format for AI (only role and content)
    history = []
    for msg in recent_messages:
        history.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    return history
```
**Purpose**: Provides context to AI without metadata

**3. Count User Messages**
```python
def count_user_messages(conversation_id: str) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*)
            FROM messages
            WHERE conversation_id = %s AND role = 'user'
        """, (conversation_id,))
        return cur.fetchone()[0]
```
**Purpose**: Used in state machine to detect engagement level

---

#### Leads Module
**File**: `backend/app/db/leads.py`

**1. Create Lead**
```python
def create_lead(
    conversation_id: str,
    email: str,
    name: str = None,
    intent: str = None,
    metadata: Dict = None
) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Get business_id from conversation
        cur.execute("SELECT business_id FROM conversations WHERE id = %s", (conversation_id,))
        result = cur.fetchone()
        business_id = str(result[0]) if result else None
        
        cur.execute("""
            INSERT INTO leads (conversation_id, business_id, email, name, 
                             intent_trigger, quality, captured_via, metadata, captured_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            conversation_id,
            business_id,
            email,
            name,
            intent or 'other',
            'MEDIUM',
            'asked',
            psycopg2.extras.Json(metadata or {}),
            datetime.utcnow()
        ))
        
        lead_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        
        return lead_id
```

**2. Get All Leads**
```python
def get_all_leads() -> List[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, conversation_id, business_id, email, name, 
                   intent_trigger, quality, captured_via, metadata, captured_at
            FROM leads
            ORDER BY captured_at DESC
        """)
        
        rows = cur.fetchall()
        cur.close()
        
        leads = []
        for row in rows:
            leads.append({
                'id': str(row[0]),
                'conversation_id': str(row[1]),
                'email': row[3],
                'name': row[4],
                'intent': row[5],
                'quality': row[6],
                'captured_via': row[7],
                'metadata': row[8],
                'created_at': row[9].isoformat() if row[9] else None
            })
        
        return leads
```

---

## Services Layer

### 1. Groq AI Service

**File**: `backend/app/services/groq_client.py`

#### Singleton Pattern
```python
class GroqService:
    _instance = None
    _client: Groq = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = Groq(api_key=settings.groq_api_key)
        return cls._instance
```

#### Chat Completion
```python
def chat_completion(
    self,
    messages: List[Dict[str, str]],
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> str:
    response = self._client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content
```

**Why Groq?**
- 300-500 tokens/second (10x faster than OpenAI)
- ~200-400ms response time
- Llama 3.3 70B quality
- Cost-effective at scale

---

### 2. Qdrant Vector Database Service

**File**: `backend/app/services/qdrant_service.py`

#### Lazy Connection Pattern
```python
def _ensure_connected(self):
    if self._client is not None:
        return
    
    if not self._qdrant_url or not self._qdrant_api_key:
        logger.warning("Qdrant credentials not configured")
        return
    
    try:
        self._client = QdrantClient(
            url=self._qdrant_url,
            api_key=self._qdrant_api_key,
            timeout=60,
            prefer_grpc=False
        )
        self._ensure_collection()
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        self._client = None
```

#### Add Documents
```python
def add_documents(self, documents: List[Dict]):
    self._ensure_connected()
    
    points = []
    for doc in documents:
        point = PointStruct(
            id=doc.get('id', str(uuid.uuid4())),
            vector=doc['embedding'],  # 384-dim vector
            payload={
                'content': doc['content'],
                'source': doc.get('source', 'unknown'),
                'category': doc.get('category', 'general'),
                'metadata': doc.get('metadata', {})
            }
        )
        points.append(point)
    
    self._client.upsert(
        collection_name=self.collection_name,
        points=points
    )
```

#### Semantic Search
```python
def search(
    self,
    query_vector: List[float],
    top_k: int = 3,
    score_threshold: float = 0.5
) -> List[Dict]:
    self._ensure_connected()
    
    results = self._client.search(
        collection_name=self.collection_name,
        query_vector=query_vector,
        limit=top_k,
        score_threshold=score_threshold
    )
    
    documents = []
    for result in results:
        documents.append({
            'id': result.id,
            'content': result.payload.get('content', ''),
            'score': result.score,  # Cosine similarity
            'metadata': {
                'source': result.payload.get('source', 'unknown'),
                'category': result.payload.get('category', 'general')
            }
        })
    
    return documents
```

**Search Process:**
1. Receive query embedding (384 dimensions)
2. Calculate cosine similarity with all vectors
3. Return top-k results above threshold
4. Typical latency: 30-70ms

---

### 3. FastEmbed Service

**File**: `backend/app/core/embeddings.py`

#### Lightweight Embeddings
```python
class FastEmbeddingService:
    _model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    def embed_text(self, text: str) -> List[float]:
        embeddings = list(self._model.embed([text]))
        return embeddings[0].tolist()  # 384 dimensions
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = list(self._model.embed(texts))
        return [emb.tolist() for emb in embeddings]
```

**Why FastEmbed?**
- No PyTorch dependency (smaller Docker image)
- Fast startup (~1s vs 10s with sentence-transformers)
- Same quality as sentence-transformers
- 384-dimensional vectors (good balance)

---

### 4. Email Notification Service

**File**: `backend/app/services/email_service.py`

#### Configuration
```python
def configure(self, settings):
    self.smtp_host = settings.smtp_host
    self.smtp_port = settings.smtp_port
    self.smtp_user = settings.smtp_user
    self.smtp_password = settings.smtp_password
    self.from_email = settings.smtp_from_email or settings.smtp_user
    self.notification_recipients = settings.notification_emails.split(",")
    self.enabled = bool(self.smtp_user and self.smtp_password and self.notification_recipients)
```

#### Send Lead Notification
```python
def send_lead_notification(
    self,
    lead_email: str,
    lead_name: Optional[str],
    intent: Optional[str],
    quality: Optional[str],
    conversation_id: int,
    lead_id: int
):
    if not self.enabled:
        logger.warning("Email service not configured")
        return

    subject = f"🎯 New Lead Captured: {lead_name or lead_email}"
    html_body = self._build_email_template(...)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = self.from_email
    msg["To"] = ", ".join(self.notification_recipients)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
        server.starttls()
        server.login(self.smtp_user, self.smtp_password)
        server.send_message(msg)
```

#### Email Template Features
- Quality badge (🔥 HOT, ⚡ WARM, ❄️ COLD)
- Lead details (name, email, intent)
- Timestamp
- Link to conversation in dashboard
- Responsive HTML design
- Call-to-action button

---

