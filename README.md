# LeadFlow AI

> Your 24/7 AI Sales Team - Converts website visitors into qualified leads automatically

[![Live Demo](https://img.shields.io/badge/demo-live-success?style=flat)](https://lead-flow-cgkd.vercel.app/)
[![Dashboard](https://img.shields.io/badge/dashboard-live-blue?style=flat)](https://lead-flow-roan.vercel.app/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb?style=flat&logo=react&logoColor=black)](https://react.dev/)

## ✨ Features

- 🤖 **AI-Powered Chat** - Intelligent responses using Groq AI with RAG
- 📧 **Email Notifications** - Instant alerts when leads are captured
- 📊 **Analytics Dashboard** - Track conversations, leads, and conversion rates
- 💬 **Conversation History** - Full chat logs with lead context
- 🎯 **Smart Lead Capture** - Automatic intent detection and qualification
- 🔍 **Vector Search** - Qdrant-powered semantic knowledge retrieval
- 📱 **Embeddable Widget** - Drop-in chat widget for any website
- 🔐 **JWT Authentication** - Secure dashboard access
- 🎨 **Modern UI** - Clean minimal design inspired by Vercel

## 🚀 Live Demo

- **Widget**: https://lead-flow-cgkd.vercel.app/
- **Dashboard**: https://lead-flow-roan.vercel.app/
- **Backend API**: https://leadflow-backend-0457e7580588.herokuapp.com/

**Default Login:**
- Email: `admin@leadflow.com`
- Password: `admin123`

## 📁 Project Structure

```
leadflow/
├── backend/                 # FastAPI backend (Heroku)
│   ├── app/
│   │   ├── api/            # REST endpoints
│   │   ├── core/           # RAG pipeline, lead capture
│   │   ├── services/       # Groq AI, email, Qdrant
│   │   └── db/             # PostgreSQL operations
│   └── scripts/            # Knowledge ingestion
│
├── frontend/
│   ├── dashboard/          # Admin dashboard (Vercel)
│   │   └── src/pages/      # Overview, Leads, Analytics, Conversations
│   │
│   └── widget/             # Chat widget (Vercel)
│       └── src/            # Landing page + chat interface
│
└── README.md
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI + Uvicorn
- Groq AI (Llama 3.3 70B)
- Qdrant Cloud (vector database)
- PostgreSQL (Supabase)
- JWT Authentication
- SMTP Email Notifications

**Frontend:**
- React 18 + Vite
- Tailwind CSS
- Recharts (analytics)
- Axios (HTTP client)

**Deployment:**
- Backend: Heroku (Docker)
- Frontend: Vercel
- Database: Supabase
- Vector DB: Qdrant Cloud

## 🎯 How It Works

### 1. User Visits Website
```
Landing page → Click "Chat with Demo" → Chat window opens
```

### 2. AI Conversation (RAG Pipeline)
```
User message → Embed query → Qdrant vector search → 
Retrieve context → Groq AI generates response → Return to user
```

### 3. Lead Capture
```
Detect intent → Ask for email → Save to PostgreSQL → 
Send email notification → Appears in dashboard
```

### 4. Dashboard Analytics
```
Admin logs in → View leads, conversations, analytics → 
Export to CSV → Track conversion rates
```

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database (Supabase)
- Qdrant Cloud account
- Groq API key

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Load knowledge base
python scripts/ingest_knowledge.py

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

**Dashboard:**
```bash
cd frontend/dashboard
npm install
npm run dev
# Opens at http://localhost:3001
```

**Widget:**
```bash
cd frontend/widget
npm install
npm run dev
# Opens at http://localhost:3001
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login to dashboard |
| `GET` | `/api/auth/me` | Get current user |
| `POST` | `/api/chat` | Send message, get AI response |
| `GET` | `/api/leads` | Get all captured leads |
| `GET` | `/api/analytics` | Get analytics data |
| `GET` | `/api/conversations` | Get all conversations |
| `GET` | `/api/conversations/{id}` | Get conversation details |
| `GET` | `/api/knowledge` | Get knowledge base documents |
| `GET` | `/health` | Health check |

## 📝 Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://...

# AI
GROQ_API_KEY=gsk_...

# Vector Database
QDRANT_URL=https://...qdrant.io
QDRANT_API_KEY=...

# Authentication
JWT_SECRET=your-secret-key
ADMIN_EMAIL=admin@leadflow.com
ADMIN_PASSWORD=admin123

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAILS=sales@company.com

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend (.env.production)
```bash
# Dashboard
VITE_API_URL=https://leadflow-backend-0457e7580588.herokuapp.com

# Widget
VITE_API_URL=https://leadflow-backend-0457e7580588.herokuapp.com
```

## 🚢 Deployment

### Backend (Heroku)

```bash
# Login and create app
heroku login
heroku create leadflow-backend
heroku stack:set container -a leadflow-backend

# Set environment variables
heroku config:set DATABASE_URL="..." -a leadflow-backend
heroku config:set GROQ_API_KEY="..." -a leadflow-backend
heroku config:set QDRANT_URL="..." -a leadflow-backend
heroku config:set QDRANT_API_KEY="..." -a leadflow-backend
heroku config:set JWT_SECRET="..." -a leadflow-backend

# Deploy using git subtree (monorepo)
heroku git:remote -a leadflow-backend
git subtree push --prefix backend heroku main
```

### Frontend (Vercel)

```bash
# Deploy dashboard
cd frontend/dashboard
vercel deploy --prod

# Deploy widget
cd frontend/widget
vercel deploy --prod

# Add environment variable in Vercel Dashboard:
# VITE_API_URL = https://your-backend.herokuapp.com
```

## 🎨 Customization

### Knowledge Base

Edit `backend/scripts/ingest_knowledge.py` to add your business information:

```python
documents = [
    {
        "content": "Your business information here...",
        "metadata": {"source": "company_info", "type": "text"}
    }
]
```

Then run:
```bash
python scripts/ingest_knowledge.py
```

### Widget Branding

Edit `frontend/widget/index.html` to customize:
- Logo
- Headline
- Subheadline
- CTA buttons
- Colors

### Welcome Message

Edit `frontend/widget/src/components/ChatWindow.jsx`:
```javascript
content: '👋 Hi! I\'m LeadFlow AI.\n\nI can help you:\n• Your custom bullet points\n• More information\n• Get started'
```

## 📊 Analytics

Track key metrics in the dashboard:
- Total Conversations
- Leads Captured
- Conversion Rate
- Average Messages per Conversation
- Lead Quality Distribution
- Intent Breakdown
- Time Series Trends

## 🔐 Security

- JWT-based authentication
- Bcrypt password hashing
- CORS protection
- Environment variable secrets
- Secure HTTPS endpoints

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Groq](https://groq.com/) - Lightning-fast LLM inference
- [Qdrant](https://qdrant.tech/) - Vector similarity search
- [Supabase](https://supabase.com/) - PostgreSQL database
- [Vercel](https://vercel.com/) - Frontend deployment
- [Heroku](https://heroku.com/) - Backend deployment

## 📞 Support

- **Live Demo**: https://lead-flow-cgkd.vercel.app/
- **Issues**: [GitHub Issues](https://github.com/ispastro/LeadFlow/issues)
- **Email**: haileasaye@gmail.com

---

**Built with ❤️ for sales teams who want to capture every lead**
