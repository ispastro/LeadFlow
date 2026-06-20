# LeadFlow Backend - Part 3: Authentication, Analytics & APIs

## Authentication Flow

**File**: `backend/app/api/auth.py`

### JWT Authentication Pattern

#### Configuration
```python
# config.py
jwt_secret: str = "your-secret-key-change-in-production"
jwt_algorithm: str = "HS256"
access_token_expire_minutes: int = 60 * 24  # 24 hours
admin_email: str = "admin@leadflow.com"
admin_password: str = "admin123"  # Change in production
```

### Auth Service

**File**: `backend/app/services/auth_service.py`

#### 1. Password Hashing
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
```

#### 2. Admin Authentication
```python
def authenticate_admin(email: str, password: str) -> bool:
    # In production, query database for user
    # For demo, hardcoded admin credentials
    if email == settings.admin_email:
        # In production, compare with hashed password from DB
        return password == settings.admin_password
    return False
```

#### 3. JWT Token Creation
```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret, 
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt
```

**JWT Payload:**
```json
{
  "sub": "admin@leadflow.com",
  "exp": 1734567890  // Unix timestamp
}
```

#### 4. JWT Token Verification
```python
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
```

---

### Authentication Endpoints

#### POST /api/auth/login

**Request:**
```json
{
  "email": "admin@leadflow.com",
  "password": "admin123"
}
```

**Flow:**
```python
@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # 1. Authenticate credentials
    if not auth_service.authenticate_admin(request.email, request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # 2. Create JWT token
    access_token = auth_service.create_access_token(data={"sub": request.email})
    
    # 3. Return token
    return LoginResponse(access_token=access_token)
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### GET /api/auth/me

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Flow:**
```python
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload

@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(email=current_user["sub"])
```

**Response:**
```json
{
  "email": "admin@leadflow.com"
}
```

---

#### POST /api/auth/logout

**Flow:**
```python
@router.post("/auth/logout")
async def logout():
    # Token invalidation happens client-side (remove from localStorage)
    return {"message": "Logged out successfully"}
```

**Note**: JWT is stateless, so logout is handled by client removing token.

---

## Analytics System

**File**: `backend/app/core/analytics.py`

### Analytics Service

#### 1. Overview Metrics

```python
def get_overview_metrics(self, days: int = 30) -> Dict:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total conversations in period
        cur.execute("""
            SELECT COUNT(*) 
            FROM conversations 
            WHERE created_at >= %s
        """, (start_date,))
        total_conversations = cur.fetchone()[0]
        
        # Total leads captured
        cur.execute("""
            SELECT COUNT(*) 
            FROM leads 
            WHERE captured_at >= %s
        """, (start_date,))
        total_leads = cur.fetchone()[0]
        
        # Conversion rate
        conversion_rate = (total_leads / total_conversations * 100) if total_conversations > 0 else 0
        
        # Average messages per conversation
        cur.execute("""
            SELECT AVG(message_count) 
            FROM (
                SELECT conversation_id, COUNT(*) as message_count
                FROM messages
                WHERE created_at >= %s
                GROUP BY conversation_id
            ) AS subquery
        """, (start_date,))
        avg_messages = cur.fetchone()[0] or 0
        
        cur.close()
        
        return {
            "total_conversations": total_conversations,
            "total_leads": total_leads,
            "conversion_rate": round(conversion_rate, 2),
            "avg_messages_per_conversation": round(float(avg_messages), 2)
        }
```

**Response Example:**
```json
{
  "total_conversations": 156,
  "total_leads": 42,
  "conversion_rate": 26.92,
  "avg_messages_per_conversation": 8.5
}
```

---

#### 2. Lead Quality Breakdown

```python
def get_lead_quality_breakdown(self, days: int = 30) -> List[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        cur.execute("""
            SELECT 
                COALESCE(quality, 'UNKNOWN') as quality, 
                COUNT(*) as count
            FROM leads
            WHERE captured_at >= %s
            GROUP BY quality
        """, (start_date,))
        
        rows = cur.fetchall()
        cur.close()
        
        return [
            {"quality": row[0], "count": row[1]} 
            for row in rows
        ]
```

**Response Example:**
```json
[
  {"quality": "HOT", "count": 12},
  {"quality": "WARM", "count": 18},
  {"quality": "COLD", "count": 8},
  {"quality": "MEDIUM", "count": 4}
]
```

---

#### 3. Intent Breakdown

```python
def get_intent_breakdown(self, days: int = 30) -> List[Dict]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        cur.execute("""
            SELECT 
                COALESCE(intent_trigger, 'other') as intent, 
                COUNT(*) as count
            FROM leads
            WHERE captured_at >= %s
            GROUP BY intent_trigger
            ORDER BY count DESC
        """, (start_date,))
        
        rows = cur.fetchall()
        cur.close()
        
        return [
            {"intent": row[0], "count": row[1]} 
            for row in rows
        ]
```

**Response Example:**
```json
[
  {"intent": "pricing", "count": 18},
  {"intent": "demo", "count": 12},
  {"intent": "integration", "count": 8},
  {"intent": "other", "count": 4}
]
```

---

#### 4. Time Series Data

```python
def get_time_series_data(self, days: int = 30) -> Dict:
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Conversations per day
        cur.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM conversations
            WHERE created_at >= %s
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (start_date,))
        
        conv_rows = cur.fetchall()
        conversations = [
            {"date": row[0].isoformat(), "count": row[1]} 
            for row in conv_rows
        ]
        
        # Leads per day
        cur.execute("""
            SELECT 
                DATE(captured_at) as date,
                COUNT(*) as count
            FROM leads
            WHERE captured_at >= %s
            GROUP BY DATE(captured_at)
            ORDER BY date
        """, (start_date,))
        
        lead_rows = cur.fetchall()
        leads = [
            {"date": row[0].isoformat(), "count": row[1]} 
            for row in lead_rows
        ]
        
        cur.close()
        
        return {
            "conversations": conversations,
            "leads": leads
        }
```

**Response Example:**
```json
{
  "conversations": [
    {"date": "2024-01-01", "count": 5},
    {"date": "2024-01-02", "count": 8},
    {"date": "2024-01-03", "count": 12}
  ],
  "leads": [
    {"date": "2024-01-01", "count": 2},
    {"date": "2024-01-02", "count": 3},
    {"date": "2024-01-03", "count": 5}
  ]
}
```

---

### Analytics Endpoint

#### GET /api/analytics?days=30

```python
@router.get("/analytics")
async def get_analytics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze")
):
    try:
        overview = analytics_service.get_overview_metrics(days)
        lead_quality = analytics_service.get_lead_quality_breakdown(days)
        intent_breakdown = analytics_service.get_intent_breakdown(days)
        time_series = analytics_service.get_time_series_data(days)
        
        return {
            "overview": overview,
            "lead_quality": lead_quality,
            "intent_breakdown": intent_breakdown,
            "time_series": time_series,
            "period_days": days
        }
    except Exception as e:
        # Return empty data structure on error
        return {
            "error": str(e),
            "overview": {
                "total_conversations": 0,
                "total_leads": 0,
                "conversion_rate": 0,
                "avg_messages_per_conversation": 0
            },
            "lead_quality": [],
            "intent_breakdown": [],
            "time_series": {"conversations": [], "leads": []}
        }
```

---

## API Endpoints Reference

### 1. Health Check

#### GET /health

**File**: `backend/app/api/health.py`

```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

---

### 2. Chat Endpoint

#### POST /api/chat

**Request:**
```json
{
  "message": "What are your pricing plans?",
  "session_id": "uuid-1234-5678-abcd"
}
```

**Response:**
```json
{
  "response": "We offer 3 pricing tiers:\n- Starter: $49/month\n- Pro: $99/month\n- Enterprise: Custom pricing\n\nAll plans include a 14-day free trial. Would you like to start a trial?",
  "session_id": "uuid-1234-5678-abcd",
  "should_capture_lead": false,
  "lead_captured": false,
  "conversation_state": "DISCOVERY"
}
```

---

### 3. Leads Endpoints

#### GET /api/leads

**File**: `backend/app/api/leads.py`

```python
@router.get("/leads")
async def get_all_leads():
    try:
        leads = leads_db.get_all_leads()
        return {
            "leads": leads,
            "total": len(leads)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Response:**
```json
{
  "leads": [
    {
      "id": "1",
      "conversation_id": "uuid-...",
      "email": "john@example.com",
      "name": "John Doe",
      "intent": "pricing",
      "quality": "WARM",
      "captured_via": "asked",
      "metadata": {"stage": "INTENT_DETECTED"},
      "created_at": "2024-01-15T10:30:00.000Z"
    }
  ],
  "total": 1
}
```

---

### 4. Conversations Endpoints

#### GET /api/conversations

**File**: `backend/app/api/conversations.py`

```python
@router.get("/conversations")
async def get_all_conversations():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    c.id,
                    c.session_id,
                    c.created_at,
                    c.updated_at,
                    COUNT(m.id) as message_count,
                    l.email,
                    l.name
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                LEFT JOIN leads l ON c.id = l.conversation_id
                GROUP BY c.id, c.session_id, c.created_at, c.updated_at, l.email, l.name
                ORDER BY c.updated_at DESC
            """)
            
            rows = cur.fetchall()
            conversations = [
                {
                    'id': str(row[0]),
                    'session_id': row[1],
                    'created_at': row[2].isoformat(),
                    'updated_at': row[3].isoformat(),
                    'message_count': row[4],
                    'email': row[5],
                    'name': row[6]
                }
                for row in rows
            ]
            
            cur.close()
        
        return {'conversations': conversations, 'total': len(conversations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Response:**
```json
{
  "conversations": [
    {
      "id": "uuid-...",
      "session_id": "session-123",
      "created_at": "2024-01-15T10:00:00.000Z",
      "updated_at": "2024-01-15T10:30:00.000Z",
      "message_count": 8,
      "email": "john@example.com",
      "name": "John Doe"
    }
  ],
  "total": 1
}
```

---

#### GET /api/conversations/{conversation_id}

```python
@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    try:
        # Get conversation details
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, session_id, created_at, updated_at
                FROM conversations
                WHERE id = %s
            """, (conversation_id,))
            
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            conversation = {
                'id': str(row[0]),
                'session_id': row[1],
                'created_at': row[2].isoformat(),
                'updated_at': row[3].isoformat()
            }
            
            cur.close()
        
        # Get messages
        messages = msg_db.get_conversation_history(conversation_id, limit=100)
        
        return {
            'conversation': conversation,
            'messages': messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Response:**
```json
{
  "conversation": {
    "id": "uuid-...",
    "session_id": "session-123",
    "created_at": "2024-01-15T10:00:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  },
  "messages": [
    {
      "role": "user",
      "content": "What are your pricing plans?"
    },
    {
      "role": "assistant",
      "content": "We offer 3 pricing tiers..."
    }
  ]
}
```

---

### 5. Knowledge Endpoints

#### GET /api/knowledge

**File**: `backend/app/api/knowledge.py`

```python
@router.get("/knowledge")
async def get_knowledge_documents():
    try:
        documents = qdrant_service.get_all_documents(limit=100)
        return {
            "documents": documents,
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Response:**
```json
{
  "documents": [
    {
      "id": "1",
      "content": "LeadFlow AI is a SaaS platform...",
      "source": "company_info",
      "metadata": {"category": "general"}
    }
  ],
  "total": 1
}
```

---

## Utility Functions

### Text Processing

**File**: `backend/app/utils/text_processing.py`

#### 1. Extract Email
```python
def extract_email(text: str) -> str:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None
```

**Examples:**
- "My email is john@example.com" → "john@example.com"
- "Contact me at john.doe+test@company.co.uk" → "john.doe+test@company.co.uk"

#### 2. Extract Name
```python
def extract_name(text: str) -> str:
    # Remove email to avoid confusion
    text_no_email = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    patterns = [
        r"(?:i'm|i am|my name is|this is|name's)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_no_email, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            if len(name.split()) <= 3 and len(name) <= 50:
                return name
    
    return None
```

**Examples:**
- "I'm John Doe" → "John Doe"
- "My name is Alice Smith" → "Alice Smith"
- "John" → "John"

#### 3. Clean Text
```python
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\w\s.,!?-]', '', text)  # Remove special chars
    return text.strip()
```

#### 4. Chunk Text
```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    
    return chunks
```

**Purpose**: Split long documents for vector embedding

---

## Summary: Request Flow Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/chat
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Application              │
│  ┌────────────────────────────────────┐ │
│  │  1. CORS Middleware Check          │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  2. Route Handler (chat.py)        │ │
│  │     - Get/Create Conversation      │ │
│  │     - Load History                 │ │
│  │     - Save User Message            │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  3. State Machine Transition       │ │
│  │     - Detect Intent (Groq API)     │ │
│  │     - Extract Email (Regex)        │ │
│  │     - Determine Next Stage         │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  4. RAG Pipeline                   │ │
│  │     - Embed Query (FastEmbed)      │ │
│  │     - Search Qdrant                │ │
│  │     - Build Prompt                 │ │
│  │     - Call Groq API                │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  5. Lead Capture (if applicable)   │ │
│  │     - Save to Database             │ │
│  │     - Send Email Notification      │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  6. Save Response & Return         │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Client    │
└─────────────┘
```

**Total Latency**: 450-600ms per message

