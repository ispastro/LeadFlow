# LeadFlow Interview - Quick Reference Cheat Sheet

## 🎯 30-Second Pitch
*"LeadFlow AI is an intelligent sales assistant that converts website visitors into qualified leads. It uses FastAPI backend with Groq's Llama 3.3 for ultra-fast AI responses, Qdrant for semantic search via RAG, and a state machine to ask for contact info at the optimal moment. Response time is ~500ms, and it scales horizontally."*

---

## 🏗️ Architecture in 60 Seconds

```
User Widget → POST /api/chat → FastAPI Backend
                                      ↓
                   [1. Load conversation from PostgreSQL]
                                      ↓
                   [2. State machine: Detect intent (Groq)]
                                      ↓
                   [3. RAG: Search Qdrant → Call Groq]
                                      ↓
                   [4. Save lead if email found]
                                      ↓
                   [5. Return response]
```

**Time:** ~500ms total

---

## 🔄 The 7 Conversation Stages (State Machine)

```
NEW → GREETED → DISCOVERY → INTENT_DETECTED 
→ EMAIL_REQUESTED → CAPTURED → POST_CAPTURE
```

| Stage | When | Action |
|-------|------|--------|
| **NEW** | No messages yet | Wait for first message |
| **GREETED** | First message received | Say hello |
| **DISCOVERY** | Asking questions | Answer, build trust |
| **INTENT_DETECTED** | Asked about pricing/demo | Answer question fully |
| **EMAIL_REQUESTED** | After high interest | Ask for email |
| **CAPTURED** | Email provided | Confirm, notify sales |
| **POST_CAPTURE** | Email already captured | Keep helping |

**Key Transition:** Groq detects "HIGH_INTEREST" (pricing, demo, trial) → Move to INTENT_DETECTED

---

## 🧠 RAG Pipeline (4 Steps)

```
1. User asks: "How much does it cost?"
         ↓
2. FastEmbed: Convert to vector [0.12, -0.34, ...]  (~30ms)
         ↓
3. Qdrant: Search similar docs → Find pricing doc  (~50ms)
         ↓
4. Groq: Generate response with context  (~250ms)
         ↓
   "We offer 3 plans: Starter $49/month..."
```

**Why RAG?** AI can't hallucinate because we give it real company info as context.

---

## 💾 Database Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| **conversations** | Track user journey | session_id, stage, email_captured |
| **messages** | Chat history | conversation_id, role, content |
| **leads** | Captured contacts | email, name, intent_trigger |
| **businesses** | Multi-tenancy | name, api_key |

**Why PostgreSQL?** Data is relational (conversations → messages → leads), ACID transactions, JSON support

---

## ⚡ Performance Breakdown

| Operation | Time | % of Total |
|-----------|------|------------|
| Database queries | 50ms | 10% |
| State machine (Groq intent) | 100ms | 20% |
| RAG pipeline | 350ms | 70% |
| **TOTAL** | **500ms** | **100%** |

**Bottleneck:** Groq API call (~250ms) - but still 6x faster than GPT-4!

---

## 🛠️ Tech Stack Justifications

### FastAPI (vs Flask/Django)
✅ Async support built-in  
✅ Auto API docs  
✅ Type validation  
✅ Fastest Python framework

### PostgreSQL (vs MongoDB)
✅ Data is relational  
✅ ACID transactions  
✅ JSON support (JSONB)  
✅ Free on Supabase

### Groq (vs OpenAI)
✅ **300 tokens/s** (vs 50 for GPT-4)  
✅ ~250ms response (vs 2-3s)  
✅ Llama 3.3 70B quality  
✅ Cheaper

### Qdrant (vs Pinecone/pgvector)
✅ Purpose-built for vectors  
✅ Free cloud tier  
✅ Fast (~50ms searches)  
✅ Good Python SDK

### FastEmbed (vs sentence-transformers)
✅ No PyTorch (500MB smaller)  
✅ Fast startup (~1s vs ~10s)  
✅ Free (vs OpenAI $$$)  
✅ 384-dim vectors

---

## 📊 Scalability

| Component | Current | Can Scale To |
|-----------|---------|--------------|
| **FastAPI** | 1 dyno = 100 req/s | 10 dynos = 1000 req/s |
| **PostgreSQL** | 10 connection pool | Read replicas + 100 pool |
| **Qdrant** | Cloud tier | Unlimited queries/s |
| **Groq** | Single API key | Multiple keys (round-robin) |

**Key:** Stateless architecture = easy horizontal scaling

---

## 🔐 Security Measures

✅ JWT authentication (24hr expiry)  
✅ Bcrypt password hashing  
✅ Parameterized SQL queries (no injection)  
✅ CORS configured (no wildcard)  
✅ HTTPS only  
✅ Secrets in environment variables  
✅ Input validation (Pydantic)

**TODO:** Rate limiting, API keys for widget

---

## 🎤 Top 10 Interview Questions - Quick Answers

### 1. "Walk me through a message flow"
*"User sends message → Load conversation from DB → State machine detects intent using Groq → RAG searches Qdrant for context → Groq generates response → Save to DB → Return. Takes ~500ms."*

### 2. "Why state machine?"
*"Ensures we ask for email at the right time - after user shows interest (pricing, demo). Too early = annoying, too late = they left. State is persisted in DB."*

### 3. "What is RAG?"
*"Retrieval Augmented Generation - search knowledge base for relevant docs, give to AI as context. Prevents hallucinations, ensures accuracy without fine-tuning."*

### 4. "How handle concurrent users?"
*"Connection pooling (2-10), async FastAPI, stateless design (state in DB not memory), horizontal scaling with load balancer."*

### 5. "Why Groq over OpenAI?"
*"Speed. 300 tokens/s vs 50. ~250ms vs 2-3s. Users expect instant chat responses. Quality is comparable (Llama 3.3 70B)."*

### 6. "How prevent AI hallucinations?"
*"RAG grounds responses in real docs, low temperature (0.3), explicit prompt: 'only use provided context', fallback to human if no context found."*

### 7. "Why DB instead of memory?"
*"Persistence (survives restarts), horizontal scaling (no sticky sessions), multi-device support, analytics, debugging. Trade 10ms latency for massive benefits."*

### 8. "Handle traffic spike?"
*"Auto-scale Heroku dynos, increase connection pool, enable Redis caching, add read replicas, implement queuing for emails. Stateless = easy horizontal scale."*

### 9. "Security measures?"
*"JWT auth, bcrypt passwords, parameterized queries, CORS config, HTTPS, input validation, secrets in env vars."*

### 10. "What metrics track?"
*"Conversion rate (leads/conversations), time to capture, response time P95, error rate, intent breakdown, cost per conversation."*

---

## 💡 Future Improvements (Show Vision)

**Short-term:**
- Response streaming (first words in 100ms)
- Redis caching (50% requests instant)
- Rate limiting

**Medium-term:**
- A/B testing for conversation strategies
- Better analytics (drop-off points)
- Multi-language support

**Long-term:**
- ML-based intent detection
- Conversation summarization
- Predictive lead scoring

---

## 🎯 Confident Phrases

### When Explaining Choices
- ✅ *"I chose X because..."* (always have reason)
- ✅ *"The trade-off was worth it because..."*
- ✅ *"This optimizes for..."* (speed/cost/scale)

### When Discussing Trade-offs
- ✅ *"Currently no caching - prioritized MVP speed, but adding Redis is first improvement"*
- ✅ *"Rule-based state machine gives predictable behavior and easy debugging"*
- ✅ *"Database state trades 10ms for unlimited scaling"*

### When Asked About Something You Haven't Implemented
- ✅ *"Great question! I'd approach that by..."*
- ✅ *"That's on my roadmap, I'd implement it as..."*
- ✅ *"In production, I'd add..."*

---

## 🔢 Numbers to Memorize

**Performance:**
- Total: 500ms
- Database: 50ms
- Groq: 250ms
- Qdrant: 50ms
- Embed: 30ms

**Capacity:**
- 1 dyno = 100 req/s
- 10 dynos = 1000 req/s
- Pool: 2-10 connections

**AI:**
- Groq: 300 tokens/s
- OpenAI: 50 tokens/s
- Groq: 6x faster!

**Embeddings:**
- Dimensions: 384
- Model: all-MiniLM-L6-v2

---

## 🗣️ Practice Saying Out Loud

### Elevator Pitch (30 seconds)
*Practice 3 times before interview!*

"LeadFlow AI converts website visitors into qualified leads using intelligent conversation. When a user clicks the chat widget, our FastAPI backend creates a conversation in PostgreSQL. As they ask questions, we use RAG - searching our Qdrant vector database for relevant company info and feeding it to Groq's Llama 3.3 model for accurate responses. A state machine detects when users show high interest, like asking about pricing, and asks for their email at that optimal moment. We capture the lead, notify the sales team via email, and the whole flow takes about 500 milliseconds. The system scales horizontally because it's stateless - all state is in the database, not in memory."

### Technical Deep Dive (60 seconds)
*Practice explaining the RAG pipeline!*

"When a user asks 'How much does it cost?', here's what happens: First, we load their conversation state from PostgreSQL - what stage are they at, have we captured their email yet. Then we use the state machine to detect intent by calling Groq with a simple classification prompt. Since they asked about pricing, that's high interest. Now the RAG pipeline kicks in: FastEmbed converts their question to a 384-dimensional vector in about 30 milliseconds. We search Qdrant's vector database using cosine similarity and retrieve the most relevant pricing documents in 50 milliseconds. We build a prompt with that context and send it to Groq's Llama 3.3 model, which generates an accurate response in 250 milliseconds. We save everything back to the database and return the response. The user sees our answer in about half a second total."

---

## 🎬 Before Interview Checklist

- [ ] Read elevator pitch out loud 3 times
- [ ] Draw architecture diagram from memory
- [ ] Explain RAG to yourself
- [ ] List 7 conversation stages
- [ ] Remember key numbers (500ms, 100 req/s, 384-dim)
- [ ] Practice 3 interview questions
- [ ] Review tech stack justifications
- [ ] Breathe! You built this! You know it!

---

## 🚀 Remember

- **You made smart decisions** - Have reasons for every choice
- **Show enthusiasm** - You're proud of what you built!
- **It's okay to say "I'd improve X by..."** - Shows growth mindset
- **Numbers matter** - 500ms, 100 req/s, 6x faster than GPT-4
- **Tell stories** - "When Sarah asks about pricing..." (more memorable)

---

## 📱 Quick Reference URLs

- **Live Demo:** https://lead-flow-cgkd.vercel.app/
- **Dashboard:** https://lead-flow-roan.vercel.app/
- **Backend API:** https://leadflow-backend-0457e7580588.herokuapp.com/docs
- **Login:** admin@leadflow.com / admin123

---

## 🎯 Final Power Moves

**When they ask:** *"Any questions for us?"*

✅ *"How do you approach scaling AI applications at your company?"*  
✅ *"What does the team's ML infrastructure look like?"*  
✅ *"What's the biggest technical challenge you're facing right now?"*

**Closing:**
✅ *"I really enjoyed discussing the architecture. I'm excited about the opportunity and confident I can contribute to the team. Thank you for your time!"*

---

**YOU'VE GOT THIS! 💪**

Print this out. Review 30 mins before interview. Ace it! 🚀

