# LeadFlow Backend - Complete Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Application Startup Flow](#application-startup-flow)
3. [Chat Conversation Flow](#chat-conversation-flow)
4. [Database Layer](#database-layer)
5. [AI & RAG Pipeline](#ai--rag-pipeline)
6. [Authentication Flow](#authentication-flow)
7. [API Endpoints](#api-endpoints)
8. [Services Layer](#services-layer)

---

## Architecture Overview

### Tech Stack
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL (Supabase) with connection pooling
- **Vector DB**: Qdrant Cloud (semantic search)
- **AI Model**: Groq (Llama 3.3 70B - ultra-fast inference)
- **Embeddings**: FastEmbed (all-MiniLM-L6-v2, 384 dimensions)
- **Auth**: JWT tokens
- **Email**: SMTP (Gmail)

### Project Structure
```
backend/
├── main.py                    # Application entry point
├── config.py                  # Environment configuration
├── app/
│   ├── api/                   # API route handlers
│   ├── core/                  # Business logic (RAG, state machine)
│   ├── db/                    # Database operations
│   ├── models/                # Pydantic models
│   ├── services/              # External services (Groq, Qdrant, Email)
│   └── utils/                 # Helper functions
└── scripts/                   # Setup & migration scripts
```

---

## Application Startup Flow

### main.py - Entry Point

**File**: `backend/main.py`

#### 1. FastAPI App Initialization
```python
app = FastAPI(
    title="AI Sales & Support Agent API",
    version="1.0.0"
)
```

#### 2. CORS Middleware Setup
- Allows cross-origin requests from frontend
- Configured origins from `settings.origins_list`
- Enables credentials, all methods, all headers

#### 3. Router Registration
Routes are mounted in this order:
- `/health` - Health check endpoint
- `/api/auth` - Authentication (login, logout)
- `/api/chat` - Main chat endpoint
- `/api/leads` - Lead management
- `/api/knowledge` - Knowledge base queries
- `/api/analytics` - Analytics data
- `/api/conversations` - Conversation history

#### 4. Startup Event (`@app.on_event("startup")`)

**Step-by-step initialization:**

```
1. Database Connection Pool
   → initialize_pool(minconn=2, maxconn=10)
   → Creates PostgreSQL connection pool
   → Reuses connections for performance

2. Load FastEmbed Model
   → embedding_service.dimension (triggers lazy load)
   → Loads all-MiniLM-L6-v2 model
   → ~1 second startup time

3. Configure Qdrant
   → qdrant_service.configure(url, api_key)
   → Connects to Qdrant Cloud
   → Checks if collection exists
   → Displays document count

4. Configure Email Service
   → email_service.configure(settings)
   → Sets up SMTP credentials
   → Validates notification recipients
```

#### 5. Shutdown Event
- Closes database connection pool
- Releases resources gracefully

---

## Chat Conversation Flow

### Complete Message Processing Pipeline

**File**: `backend/app/api/chat.py`

This is the **CORE** of the entire system. Every user message flows through this pipeline.

### Request Model
```python
ChatRequest:
  - message: str (1-2000 chars)
  - session_id: str (unique per user)
  - user_email: Optional[str]
  - user_name: Optional[str]
```

### Response Model
```python
ChatResponse:
  - response: str (AI-generated reply)
  - session_id: str
  - should_capture_lead: bool
  - lead_captured: bool
  - conversation_state: str (NEW, GREETED, etc.)
```

---

### Step-by-Step Flow

#### STEP 1: Load Conversation State
```python
conversation = conv_db.get_or_create_conversation(session_id)
conversation_id = conversation['id']
current_stage = ConversationStage(conversation['stage'])
email_captured = conversation['email_captured']
```

**What happens:**
- Queries `conversations` table by `session_id`
- If not found, creates new conversation with stage='NEW'
- Returns conversation metadata including current stage

**Database Query:**
```sql
SELECT id, session_id, business_id, stage, email_captured, created_at, updated_at
FROM conversations
WHERE session_id = %s
```

---

#### STEP 2: Get Conversation History
```python
history = msg_db.get_conversation_history(conversation_id, limit=4)
message_count = msg_db.count_user_messages(conversation_id)
```

**What happens:**
- Fetches last 4 messages from `messages` table
- Counts total user messages
- Formats messages for AI context

**Database Queries:**
```sql
-- Get history
SELECT id, conversation_id, role, content, created_at
FROM messages
WHERE conversation_id = %s
ORDER BY created_at
LIMIT 4

-- Count user messages
SELECT COUNT(*)
FROM messages
WHERE conversation_id = %s AND role = 'user'
```

---

#### STEP 3: Save User Message
```python
msg_db.create_message(conversation_id, 'user', request.message)
```

**Database Query:**
```sql
INSERT INTO messages (conversation_id, business_id, role, content, created_at)
VALUES (%s, %s, 'user', %s, NOW())
```

---

#### STEP 4: State Machine Transition

**File**: `backend/app/core/state_machine.py`

```python
new_stage, extracted_email = state_machine.transition(
    current_stage=current_stage,
    message=request.message,
    email_captured=email_captured,
    message_count=message_count
)
```

### Conversation Stages (Enum)
```python
class ConversationStage:
    NEW              # First contact (no messages yet)
    GREETED          # User sent first message
    DISCOVERY        # AI answering questions, building trust
    INTENT_DETECTED  # User shows high interest
    EMAIL_REQUESTED  # AI asking for email
    CAPTURED         # Email successfully captured
    POST_CAPTURE     # After email captured, continued conversation
```

### State Transition Logic

#### NEW → GREETED
**Trigger**: First user message  
**Condition**: `message_count == 0`

#### GREETED/DISCOVERY → INTENT_DETECTED
**Trigger**: High interest detected  
**Conditions**:
- LLM classifies intent as "HIGH_INTEREST" OR
- User has sent 2+ messages

**Intent Detection:**
```python
def detect_intent(message: str) -> str:
    prompt = """Classify user intent as HIGH_INTEREST, INFORMATION_SEEKING, or LOW_INTEREST.
    
    HIGH_INTEREST: pricing, demo, trial, buying, signing up, integrations
    INFORMATION_SEEKING: general questions, "what is this"
    LOW_INTEREST: "no thanks", "not interested"
    """
    return groq_service.chat_completion([{"role": "user", "content": prompt}])
```

#### INTENT_DETECTED → EMAIL_REQUESTED
**Trigger**: After answering high-interest question  
**Action**: AI will ask for email in next response

#### EMAIL_REQUESTED → CAPTURED
**Trigger**: Email found in message  
**Validation**: `extract_email(message)` using regex

#### CAPTURED → POST_CAPTURE
**Trigger**: Email already captured  
**State**: Terminal state, continues helping user

---

#### STEP 5: Handle Email Capture

```python
if extracted_email and not email_captured:
    name = extract_name(request.message)
    
    # Analyze conversation to determine intent trigger
    all_messages = msg_db.get_conversation_history(conversation_id, limit=10)
    conversation_text = ' '.join([m['content'].lower() for m in all_messages])
    
    # Intent classification based on keywords
    if 'price' in conversation_text or 'pricing' in conversation_text:
        intent_trigger = 'pricing'
    elif 'demo' in conversation_text or 'trial' in conversation_text:
        intent_trigger = 'demo'
    elif 'integrate' in conversation_text or 'api' in conversation_text:
        intent_trigger = 'integration'
    elif new_stage == ConversationStage.DISCOVERY:
        intent_trigger = 'unprompted'
    else:
        intent_trigger = 'other'
    
    # Create lead in database
    lead_id = leads_db.create_lead(
        conversation_id=conversation_id,
        email=extracted_email,
        name=name,
        intent=intent_trigger,
        metadata={'stage': new_stage.value}
    )
    
    # Send email notification in background
    background_tasks.add_task(
        email_service.send_lead_notification,
        lead_email=extracted_email,
        lead_name=name,
        intent=intent_trigger,
        quality='MEDIUM',
        conversation_id=conversation_id,
        lead_id=lead_id
    )
```

**Database Query:**
```sql
INSERT INTO leads (conversation_id, business_id, email, name, intent_trigger, 
                   quality, captured_via, metadata, captured_at)
VALUES (%s, %s, %s, %s, %s, 'MEDIUM', 'asked', %s, NOW())
RETURNING id
```

---

#### STEP 6: Update Conversation Stage

```python
conv_db.update_conversation_stage(
    conversation_id, 
    new_stage.value, 
    email_captured
)
```

**Database Query:**
```sql
UPDATE conversations
SET stage = %s, email_captured = %s, updated_at = NOW()
WHERE id = %s
```

---

#### STEP 7: Generate RAG Response

**File**: `backend/app/core/rag.py`

```python
system_instructions = state_machine.get_system_instructions(new_stage)

ai_response = rag_service.generate_response(
    user_message=request.message,
    conversation_history=history[:-1],  # Exclude current message
    additional_instructions=system_instructions
)
```

### RAG Pipeline Breakdown

**Sub-step 7.1: Retrieve Context**
```python
def retrieve_context(query: str, top_k: int = 3) -> List[Dict]:
    # 1. Embed the query
    query_embedding = embedding_service.embed_text(query)
    
    # 2. Search Qdrant for similar documents
    docs = qdrant_service.search(
        query_vector=query_embedding,
        top_k=top_k,
        score_threshold=0.3
    )
    
    return docs
```

**Timing**: ~50-100ms
- Embedding: 20-30ms
- Qdrant search: 30-70ms

**Sub-step 7.2: Build System Prompt**
```python
if context_docs:
    context = "\n\n".join([
        f"[Source: {doc.get('metadata', {}).get('source', 'Unknown')}]\n{doc['content']}"
        for doc in context_docs
    ])
else:
    # Fallback context
    context = """LeadFlow AI is a SaaS platform that converts website visitors 
    into qualified leads automatically using AI-powered chat."""

system_prompt = f"""You are a helpful AI sales and support agent for LeadFlow AI.

Your primary information source is the context below.

=== KNOWLEDGE BASE ===
{context}
=== END OF KNOWLEDGE BASE ===

Guidelines:
- Answer questions using the context provided
- Be friendly, professional, and helpful
- Keep responses concise (2-3 sentences)
"""
```

**Sub-step 7.3: Call Groq API**
```python
messages = [
    {"role": "system", "content": system_prompt}
]

# Add conversation history
if conversation_history:
    messages.extend(conversation_history)

# Add current message
messages.append({"role": "user", "content": user_message})

response = groq_service.chat_completion(
    messages,
    model="llama-3.3-70b-versatile",
    temperature=0.3
)
```

**Timing**: 200-400ms (Groq is ultra-fast!)

---

#### STEP 8: Append Email Request (if needed)

```python
if state_machine.should_append_email_ask(new_stage) and not email_captured:
    ai_response += "\n\nTo get you started, what's your name and email address?"
```

**When this happens:**
- Stage is `EMAIL_REQUESTED`
- Email not yet captured

---

#### STEP 9: Handle Capture Confirmation

```python
if new_stage == ConversationStage.CAPTURED:
    ai_response = f"""Perfect! I've sent the setup details to {extracted_email}. 
    Our team will reach out within the next few hours.
    
    Do you have any other questions in the meantime?"""
```

---

#### STEP 10: Save AI Response

```python
msg_db.create_message(conversation_id, 'assistant', ai_response)
conv_db.update_conversation_timestamp(conversation_id)
```

**Database Queries:**
```sql
-- Save AI message
INSERT INTO messages (conversation_id, business_id, role, content, created_at)
VALUES (%s, %s, 'assistant', %s, NOW())

-- Update conversation timestamp
UPDATE conversations
SET updated_at = NOW()
WHERE id = %s
```

---

#### STEP 11: Return Response

```python
return ChatResponse(
    response=ai_response,
    session_id=request.session_id,
    should_capture_lead=(new_stage == ConversationStage.EMAIL_REQUESTED),
    lead_captured=email_captured,
    conversation_state=new_stage.value
)
```

### Total Timing Breakdown
- Database operations: ~50ms
- RAG context retrieval: ~100ms
- Groq AI generation: ~300ms
- **Total: ~450-600ms** per message

---

