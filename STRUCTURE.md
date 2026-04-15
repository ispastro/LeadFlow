# LeadFlow Project Structure

```
LeadFlow/
│
├── README.md                    # Main project documentation
├── QUICKSTART.md               # 5-minute setup guide
│
├── backend/                    # FastAPI + RAG + PostgreSQL
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── chat.py       # Main chat endpoint
│   │   │   ├── leads.py      # Lead management
│   │   │   └── health.py     # Health check
│   │   ├── core/              # Core business logic
│   │   │   ├── rag.py        # RAG service (retrieval + generation)
│   │   │   ├── embeddings.py # Sentence Transformers
│   │   │   ├── conversation.py # State management
│   │   │   └── lead_capture.py # Intent detection
│   │   ├── db/                # Database operations
│   │   │   ├── pg_direct.py  # Direct PostgreSQL (vector ops)
│   │   │   ├── conversations.py
│   │   │   ├── messages.py
│   │   │   ├── leads.py
│   │   │   └── knowledge_base.py
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # External services
│   │   │   └── groq_client.py # Groq API wrapper
│   │   └── utils/             # Utilities
│   ├── scripts/
│   │   ├── ingest_knowledge.py # Load business data
│   │   ├── test_rag_debug.py   # Test RAG pipeline
│   │   └── clear_knowledge.py  # Clear database
│   ├── .env                   # Environment variables
│   ├── config.py              # Configuration
│   ├── main.py                # FastAPI app
│   └── requirements.txt       # Python dependencies
│
└── frontend/                  # React + Vite + Tailwind
    ├── README.md
    ├── .gitignore
    │
    ├── widget/                # Customer-facing chat widget
    │   ├── src/
    │   │   ├── components/
    │   │   │   ├── ChatBubble.jsx    # Floating button
    │   │   │   └── ChatWindow.jsx    # Chat interface
    │   │   ├── Widget.jsx            # Main widget component
    │   │   ├── main.jsx              # Entry point
    │   │   └── index.css             # Tailwind styles
    │   ├── index.html
    │   ├── package.json
    │   ├── vite.config.js
    │   ├── tailwind.config.js
    │   └── README.md
    │
    └── dashboard/             # Admin dashboard
        ├── src/
        │   ├── components/
        │   │   └── Sidebar.jsx       # Navigation
        │   ├── pages/
        │   │   ├── Dashboard.jsx     # Overview with stats
        │   │   ├── Leads.jsx         # Lead management
        │   │   ├── Conversations.jsx # Coming soon
        │   │   ├── Knowledge.jsx     # Coming soon
        │   │   └── Settings.jsx      # Coming soon
        │   ├── services/
        │   │   └── api.js            # API client
        │   ├── App.jsx               # Main app with routing
        │   ├── main.jsx              # Entry point
        │   └── index.css             # Tailwind styles
        ├── index.html
        ├── package.json
        ├── vite.config.js
        ├── tailwind.config.js
        ├── .env.example
        └── README.md
```

## Key Files

### Backend
- `main.py` - FastAPI application entry point
- `app/core/rag.py` - RAG pipeline (retrieval + generation)
- `app/db/pg_direct.py` - Direct PostgreSQL for vectors
- `app/api/chat.py` - Main chat endpoint

### Frontend Widget
- `src/Widget.jsx` - Main widget component
- `src/components/ChatWindow.jsx` - Chat interface
- `src/main.jsx` - Embeddable entry point

### Frontend Dashboard
- `src/App.jsx` - Main app with routing
- `src/pages/Dashboard.jsx` - Overview page
- `src/pages/Leads.jsx` - Lead management

## Ports

- Backend API: `http://localhost:8000`
- Chat Widget: `http://localhost:5173`
- Admin Dashboard: `http://localhost:3000`

## Database Tables

- `knowledge_base` - Vector embeddings + content
- `conversations` - Chat sessions
- `messages` - Chat messages
- `leads` - Captured leads
