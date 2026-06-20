# LeadFlow Backend - Interview Preparation Guide

## 🎯 Goal: Defend Your System Confidently

This guide gives you **simple explanations** and **talking points** for your interview.

---

## 📖 Table of Contents

1. [30-Second Elevator Pitch](#30-second-elevator-pitch)
2. [High-Level Architecture](#high-level-architecture)
3. [The Complete User Journey](#the-complete-user-journey)
4. [Deep Dive: Chat Flow (Step-by-Step)](#deep-dive-chat-flow-step-by-step)
5. [Deep Dive: State Machine](#deep-dive-state-machine)
6. [Deep Dive: RAG Pipeline](#deep-dive-rag-pipeline)
7. [Database Design Decisions](#database-design-decisions)
8. [Technology Choices & Why](#technology-choices--why)
9. [Performance & Scalability](#performance--scalability)
10. [Common Interview Questions & Answers](#common-interview-questions--answers)

---

## 30-Second Elevator Pitch

> **"LeadFlow AI is an intelligent sales assistant that converts website visitors into qualified leads automatically."**

### What It Does:
- User visits website, clicks chat widget
- AI engages them in conversation using RAG (Retrieval Augmented Generation)
- System detects when user shows interest (asks about pricing, demos, etc.)
- Naturally asks for their email at the right moment
- Saves lead to database and notifies sales team via email
- Dashboard shows all conversations, leads, and analytics

### Tech Stack in One Sentence:
> **"FastAPI backend with PostgreSQL database, using Groq's Llama 3.3 for ultra-fast AI responses, Qdrant for semantic search, and a state machine to manage conversation flow."**

---

## High-Level Architecture

### Visual Overview

```
┌─────────────────────────────────────────────────────┐
│                USER ON WEBSITE                       │
│          (Clicks "Chat with Demo")                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌──────────────────┐
         │  React Widget     │ ◄── Simple chat UI
         │  (Frontend)       │
         └─────────┬─────────┘
                   │
                   │ POST /api/chat
                   │ { message: "What are your pricing plans?",
                   │   session_id: "uuid-1234" }
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│            FastAPI Backend (main.py)                  │
│                                                       │
│  ┌────────────────────────────────────────────┐     │
│  │         Chat Endpoint (chat.py)            │     │
│  │                                             │     │
│  │  1. Get conversation from database         │     │
│  │  2. Run state machine (determine action)   │     │
│  │  3. Generate AI response using RAG         │     │
│  │  4. Save everything back to database       │     │
│  │  5. Send email if lead captured            │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
          │           │              │
          ▼           ▼              ▼
    ┌─────────┐ ┌──────────┐ ┌────────────┐
    │PostgreSQL│ │  Qdrant  │ │  Groq AI   │
    │ Database │ │  Vectors │ │  (Llama)   │
    └─────────┘ └──────────┘ └────────────┘
```

### Key Components (Easy Explanation):

1. **Frontend Widget**: Just a chat interface (React)
2. **Backend API**: Handles all the logic (FastAPI)
3. **PostgreSQL**: Stores conversations, messages, leads
4. **Qdrant**: Stores company knowledge as vectors for smart search
5. **Groq AI**: Generates intelligent responses (like ChatGPT but faster)

---

## The Complete User Journey

### Story Time: Meet Sarah

**Sarah lands on your website and sees a chat bubble...**

#### Message 1: Sarah clicks and types "Hi"

```
┌─────────────────────────────────────────┐
│ Sarah: "Hi"                              │
└─────────────────────────────────────────┘
                   │
                   ▼
        Backend creates NEW conversation
        Stage: NEW → GREETED
                   │
                   ▼
        AI responds: "👋 Hi! I'm LeadFlow AI.
        How can I help you today?"
```

**What happened inside:**
- Created a conversation record in database
- Assigned stage: `GREETED`
- Returned a friendly greeting

---

#### Message 2: Sarah asks "What do you offer?"

```
┌─────────────────────────────────────────┐
│ Sarah: "What do you offer?"              │
└─────────────────────────────────────────┘
                   │
                   ▼
        State Machine: Not high interest yet
        Stage: GREETED → DISCOVERY
                   │
                   ▼
        RAG Pipeline:
        1. Search Qdrant for "what do you offer"
        2. Find company overview document
        3. Build prompt with context
        4. Call Groq AI
                   │
                   ▼
        AI responds: "LeadFlow AI is a platform that
        converts website visitors into leads using
        AI chat. We offer 24/7 automation..."
```

**What happened inside:**
- State machine kept her in `DISCOVERY` (just learning phase)
- RAG found relevant docs from knowledge base
- AI gave informed response

---

#### Message 3: Sarah asks "How much does it cost?"

```
┌─────────────────────────────────────────┐
│ Sarah: "How much does it cost?"          │
└─────────────────────────────────────────┘
                   │
                   ▼
        State Machine detects HIGH INTEREST!
        (She asked about pricing!)
        Stage: DISCOVERY → INTENT_DETECTED
                   │
                   ▼
        RAG Pipeline:
        1. Search for "pricing" docs
        2. Find pricing plans
        3. Generate response with plans
                   │
                   ▼
        AI responds: "We offer 3 plans:
        - Starter: $49/month
        - Pro: $99/month
        - Enterprise: Custom
        All include 14-day free trial."
```

**What happened inside:**
- State machine detected "pricing" = HIGH_INTEREST
- Moved to `INTENT_DETECTED` stage
- Next response will ask for email!

---

#### Message 4: Sarah says "Sounds good!"

```
┌─────────────────────────────────────────┐
│ Sarah: "Sounds good!"                    │
└─────────────────────────────────────────┘
                   │
                   ▼
        State Machine: She showed interest
        Stage: INTENT_DETECTED → EMAIL_REQUESTED
                   │
                   ▼
        AI responds: "Great! I'd love to help you
        get started. What's your name and email?"
```

**What happened inside:**
- After answering her high-interest question, now ask for email
- Stage moved to `EMAIL_REQUESTED`

---

#### Message 5: Sarah provides "I'm Sarah, sarah@example.com"

```
┌─────────────────────────────────────────┐
│ Sarah: "I'm Sarah, sarah@example.com"    │
└─────────────────────────────────────────┘
                   │
                   ▼
        Extract email using regex!
        Email found: "sarah@example.com"
        Name found: "Sarah"
                   │
                   ▼
        LEAD CAPTURED! 🎉
        Stage: EMAIL_REQUESTED → CAPTURED
                   │
                   ▼
        1. Save lead to database
        2. Send email notification to sales team
        3. Return confirmation message
                   │
                   ▼
        AI responds: "Perfect! I've sent the
        details to sarah@example.com. Our team
        will reach out within a few hours.
        Any other questions?"
```

**What happened inside:**
- Regex extracted email and name
- Created lead record in database
- Sent beautiful HTML email to sales team
- Stage moved to `CAPTURED` (terminal state)

---

#### Message 6: Sarah asks "Do you integrate with Salesforce?"

```
┌─────────────────────────────────────────┐
│ Sarah: "Do you integrate with Salesforce?"│
└─────────────────────────────────────────┘
                   │
                   ▼
        Stage: CAPTURED → POST_CAPTURE
        (Email already captured, keep helping)
                   │
                   ▼
        RAG Pipeline finds integration docs
                   │
                   ▼
        AI responds: "Yes! We integrate with
        Salesforce, HubSpot, and many others..."
```

**What happened inside:**
- Email already captured, just continue helping
- RAG provides accurate information
- Conversation continues naturally

---

## Deep Dive: Chat Flow (Step-by-Step)

### The 11-Step Pipeline

When Sarah sends **"How much does it cost?"**, here's what happens:

#### STEP 1: Load Conversation (Database Query)
```sql
SELECT id, session_id, stage, email_captured
FROM conversations
WHERE session_id = 'sarah-uuid-1234'
```

**Result:**
```json
{
  "id": "conv-123",
  "session_id": "sarah-uuid-1234",
  "stage": "DISCOVERY",
  "email_captured": false
}
```

**Why?** Need to know where Sarah is in the conversation journey.

---

#### STEP 2: Get History (Database Query)
```sql
SELECT role, content
FROM messages
WHERE conversation_id = 'conv-123'
ORDER BY created_at DESC
LIMIT 4
```

**Result:**
```json
[
  {"role": "user", "content": "Hi"},
  {"role": "assistant", "content": "Hi! I'm LeadFlow AI..."},
  {"role": "user", "content": "What do you offer?"},
  {"role": "assistant", "content": "LeadFlow AI is a platform..."}
]
```

**Why?** AI needs context to give coherent responses.

---

#### STEP 3: Save User Message (Database Insert)
```sql
INSERT INTO messages (conversation_id, role, content, created_at)
VALUES ('conv-123', 'user', 'How much does it cost?', NOW())
```

**Why?** Store everything for analytics and history.

---

#### STEP 4: State Machine Transition

```python
# Input:
current_stage = "DISCOVERY"
message = "How much does it cost?"
email_captured = False
message_count = 2

# Process:
1. Call Groq to detect intent
   Prompt: "Is 'How much does it cost?' HIGH_INTEREST, 
            INFORMATION_SEEKING, or LOW_INTEREST?"
   Response: "HIGH_INTEREST"

2. Decide transition
   DISCOVERY + HIGH_INTEREST → INTENT_DETECTED

# Output:
new_stage = "INTENT_DETECTED"
extracted_email = None
```

**Why?** Determines what action to take next (answer vs ask for email).

---

#### STEP 5: Check for Email (Skip for now)

```python
if extracted_email and not email_captured:
    # Create lead, send email
    pass
```

**Why?** No email in message yet, skip.

---

#### STEP 6: Update Conversation Stage (Database Update)
```sql
UPDATE conversations
SET stage = 'INTENT_DETECTED', updated_at = NOW()
WHERE id = 'conv-123'
```

**Why?** Track progression through conversation funnel.

---

#### STEP 7: Generate AI Response (RAG Pipeline)

##### Sub-step 7a: Embed Query (FastEmbed)
```python
query = "How much does it cost?"
embedding = embedding_service.embed_text(query)
# Returns: [0.123, -0.456, 0.789, ...] (384 numbers)
```
**Time:** ~30ms

##### Sub-step 7b: Search Qdrant (Vector Similarity)
```python
results = qdrant_service.search(
    query_vector=embedding,
    top_k=3,
    score_threshold=0.3
)
```
**Returns:**
```json
[
  {
    "content": "Pricing: Starter $49, Pro $99, Enterprise Custom...",
    "score": 0.87,
    "source": "pricing"
  }
]
```
**Time:** ~50ms

##### Sub-step 7c: Build Prompt
```python
system_prompt = f"""
You are LeadFlow AI sales assistant.

KNOWLEDGE BASE:
{context_from_qdrant}

Answer the user's question using this information.
"""

messages = [
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": "Hi"},
  {"role": "assistant", "content": "Hi! I'm LeadFlow AI..."},
  {"role": "user", "content": "What do you offer?"},
  {"role": "assistant", "content": "LeadFlow AI is..."},
  {"role": "user", "content": "How much does it cost?"}
]
```

##### Sub-step 7d: Call Groq API
```python
response = groq_client.chat_completion(
    messages=messages,
    model="llama-3.3-70b-versatile",
    temperature=0.3
)
```
**Returns:**
```
"We offer 3 pricing tiers:
- Starter: $49/month
- Pro: $99/month
- Enterprise: Custom pricing
All plans include a 14-day free trial."
```
**Time:** ~250ms

**Total RAG time:** ~330ms

---

#### STEP 8: Append Email Ask? (Check)
```python
if new_stage == "EMAIL_REQUESTED" and not email_captured:
    ai_response += "\n\nWhat's your name and email?"
```

**Why?** Not EMAIL_REQUESTED yet, so skip.

---

#### STEP 9: Handle Capture Confirmation? (Skip)
```python
if new_stage == "CAPTURED":
    ai_response = "Perfect! I've sent details to {email}..."
```

**Why?** Not captured yet, skip.

---

#### STEP 10: Save AI Response (Database Insert)
```sql
INSERT INTO messages (conversation_id, role, content, created_at)
VALUES ('conv-123', 'assistant', 'We offer 3 pricing tiers...', NOW())
```

```sql
UPDATE conversations
SET updated_at = NOW()
WHERE id = 'conv-123'
```

---

#### STEP 11: Return Response

```json
{
  "response": "We offer 3 pricing tiers:\n- Starter: $49/month...",
  "session_id": "sarah-uuid-1234",
  "should_capture_lead": false,
  "lead_captured": false,
  "conversation_state": "INTENT_DETECTED"
}
```

**Frontend shows this to Sarah!**

---

### Timing Breakdown

```
┌────────────────────────────┬─────────┐
│ Operation                  │ Time    │
├────────────────────────────┼─────────┤
│ Load conversation (DB)     │ ~10ms   │
│ Get history (DB)           │ ~15ms   │
│ Save user message (DB)     │ ~15ms   │
│ State machine (Groq)       │ ~100ms  │
│ Update stage (DB)          │ ~10ms   │
│ RAG: Embed query           │ ~30ms   │
│ RAG: Search Qdrant         │ ~50ms   │
│ RAG: Call Groq             │ ~250ms  │
│ Save AI response (DB)      │ ~15ms   │
├────────────────────────────┼─────────┤
│ TOTAL                      │ ~495ms  │
└────────────────────────────┴─────────┘
```

**Half a second from user hitting enter to seeing AI response! ⚡**

---

## Deep Dive: State Machine

### The 7 Conversation Stages

Think of it like a **sales funnel**:

```
┌─────────────────────────────────────────┐
│ NEW                                      │ ◄── User hasn't sent message yet
└───────────────┬─────────────────────────┘
                │ User sends first message
                ▼
┌─────────────────────────────────────────┐
│ GREETED                                  │ ◄── AI said hello
└───────────────┬─────────────────────────┘
                │ User asks questions
                ▼
┌─────────────────────────────────────────┐
│ DISCOVERY                                │ ◄── Learning about product
└───────────────┬─────────────────────────┘
                │ Asks about pricing/demo
                ▼
┌─────────────────────────────────────────┐
│ INTENT_DETECTED                          │ ◄── High interest detected!
└───────────────┬─────────────────────────┘
                │ AI asks for email
                ▼
┌─────────────────────────────────────────┐
│ EMAIL_REQUESTED                          │ ◄── Waiting for contact info
└───────────────┬─────────────────────────┘
                │ User provides email
                ▼
┌─────────────────────────────────────────┐
│ CAPTURED ✅                              │ ◄── Lead saved! Email sent!
└───────────────┬─────────────────────────┘
                │ Continue conversation
                ▼
┌─────────────────────────────────────────┐
│ POST_CAPTURE                             │ ◄── Keep helping them
└─────────────────────────────────────────┘
```

### Transition Logic (Easy Rules)

#### Rule 1: First Message
```
IF message_count == 0:
    NEW → GREETED
```

#### Rule 2: High Interest Detected
```
IF (user asks about pricing OR demo OR integration) OR message_count >= 2:
    GREETED/DISCOVERY → INTENT_DETECTED
```

#### Rule 3: Asked Question, Now Ask for Email
```
IF stage == INTENT_DETECTED:
    INTENT_DETECTED → EMAIL_REQUESTED
```

#### Rule 4: Email Found
```
IF email found in message AND stage == EMAIL_REQUESTED:
    EMAIL_REQUESTED → CAPTURED
    (Create lead, send notification)
```

#### Rule 5: Already Captured
```
IF email_captured == True:
    CAPTURED → POST_CAPTURE
    (Just keep helping)
```

### How Intent Detection Works

**Send message to Groq:**
```
"Classify user intent as HIGH_INTEREST, INFORMATION_SEEKING, or LOW_INTEREST.

HIGH_INTEREST: pricing, demo, trial, buying, signup, integration
INFORMATION_SEEKING: general questions, "what is this"
LOW_INTEREST: "no thanks", "not interested"

Message: "How much does it cost?"

Classify as ONE word only:"
```

**Groq response:** `"HIGH_INTEREST"`

**Why Groq?** Fast (~100ms) and smart enough to understand context.

---

## Deep Dive: RAG Pipeline

### What is RAG?

**RAG = Retrieval Augmented Generation**

**Simple Explanation:**
Instead of making the AI memorize everything, we:
1. Store company info in a searchable database (Qdrant)
2. When user asks a question, search for relevant info
3. Give that info to AI as "context"
4. AI generates response using the context

**Why?** AI gives accurate, up-to-date answers without hallucinating.

---

### The 4-Step RAG Process

#### Step 1: Embed the Query

**User asks:** "Do you integrate with HubSpot?"

**Convert to numbers:**
```python
embedding = FastEmbed.embed("Do you integrate with HubSpot?")
# Returns: [0.12, -0.34, 0.56, ..., 0.89] (384 numbers)
```

**Why numbers?** Computers can't search text directly. Numbers represent meaning.

---

#### Step 2: Search Qdrant (Vector Database)

**Search for similar documents:**
```python
results = qdrant.search(
    vector=embedding,
    top_k=3  # Find 3 most similar docs
)
```

**Qdrant compares:**
```
Query vector:     [0.12, -0.34, 0.56, ...]
Doc1 vector:      [0.15, -0.32, 0.54, ...]  Similarity: 0.87 ✅
Doc2 vector:      [0.89,  0.12, -0.43, ...] Similarity: 0.45
Doc3 vector:      [-0.23, 0.67, 0.12, ...]  Similarity: 0.32
```

**Returns:**
```json
[
  {
    "content": "Integrations: Salesforce, HubSpot, Pipedrive...",
    "score": 0.87
  }
]
```

**Math:** Cosine similarity (measures angle between vectors)

---

#### Step 3: Build Prompt with Context

```python
system_prompt = f"""
You are LeadFlow AI assistant.

Use this information to answer questions:
=== KNOWLEDGE BASE ===
{context_from_qdrant}
=== END KNOWLEDGE BASE ===

Be helpful and accurate.
"""

messages = [
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": "Do you integrate with HubSpot?"}
]
```

---

#### Step 4: Call Groq AI

```python
response = groq.chat(messages)
```

**Groq generates:**
```
"Yes! We integrate with HubSpot, Salesforce, Pipedrive, 
and 5,000+ apps via Zapier. Setup takes less than 5 minutes."
```

**Why Groq?** Ultra-fast (250ms vs 2000ms for GPT-4)

---

### Visual Diagram

```
User Question
    │
    ▼
┌─────────────────┐
│ "Do you         │
│  integrate      │
│  with HubSpot?" │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ FastEmbed               │
│ Convert to vector       │
│ [0.12, -0.34, ...]     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Qdrant Vector DB        │
│ Search similar docs     │
│ Return: "Integrations:  │
│  Salesforce, HubSpot..."│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Build Prompt            │
│ System: "Use this       │
│  context..."            │
│ User: "Do you integrate │
│  with HubSpot?"         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Groq AI (Llama 3.3)     │
│ Generate smart response │
└────────┬────────────────┘
         │
         ▼
    "Yes! We integrate
     with HubSpot..."
```

---

## Database Design Decisions

### Why PostgreSQL?

**✅ Pros:**
- Reliable and battle-tested
- ACID transactions (data consistency)
- Great for relational data (conversations → messages → leads)
- Free tier on Supabase
- Supports JSON columns (flexible metadata)

**❌ Alternatives considered:**
- MongoDB: Not needed, data is relational
- MySQL: PostgreSQL has better JSON support

---

### Table Design Explained

#### conversations
```sql
id              UUID        -- Unique conversation
session_id      VARCHAR     -- Frontend generates this
stage           VARCHAR     -- Current conversation stage
email_captured  BOOLEAN     -- Did we get their email?
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**Why?** Tracks user's journey through the funnel.

---

#### messages
```sql
id                UUID
conversation_id   UUID        -- Links to conversation
role              VARCHAR     -- 'user' or 'assistant'
content           TEXT        -- The actual message
created_at        TIMESTAMP
```

**Why?** Full conversation history for context and analytics.

---

#### leads
```sql
id                SERIAL      -- Auto-increment ID
conversation_id   UUID        -- Which conversation?
email             VARCHAR     -- Contact info!
name              VARCHAR     -- Their name
intent_trigger    VARCHAR     -- What made them interested?
quality           VARCHAR     -- HOT/WARM/COLD
metadata          JSONB       -- Extra flexible data
captured_at       TIMESTAMP
```

**Why?** Sales team needs all this info to follow up effectively.

---

### Connection Pooling Strategy

**Problem:** Opening a new database connection is SLOW (100-200ms)

**Solution:** Connection Pool

```python
# Create pool on startup
pool = ThreadedConnectionPool(
    minconn=2,   # Always keep 2 connections open
    maxconn=10   # Maximum 10 concurrent connections
)

# Reuse connections
with get_db_connection() as conn:
    # Connection is already open! ⚡
    cur = conn.cursor()
    cur.execute("SELECT ...")
# Connection returned to pool (not closed!)
```

**Benefits:**
- No connection overhead per request
- Handles concurrent requests efficiently
- Health checks detect dead connections

---

