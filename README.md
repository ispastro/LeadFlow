# LeadFlow

> AI-powered sales agent that converts website visitors into qualified leads automatically

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ Features

- 🤖 **AI-Powered Chat** - RAG-based responses using Llama 3.3 70B via Groq
- 📧 **Email Notifications** - Instant alerts when leads are captured (1-2 seconds)
- 📊 **Analytics Dashboard** - Track conversations, leads, and conversion rates
- 💬 **Conversation History** - Full chat logs with lead context
- 🎯 **Smart Lead Capture** - Automatic intent detection and qualification
- 🔍 **Vector Search** - pgvector-powered semantic knowledge retrieval
- 📱 **Embeddable Widget** - Drop-in chat widget for any website
- 📈 **CSV Export** - Download leads for CRM import
- 🎨 **Modern UI** - Vercel-inspired dark mode design

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 16+ with pgvector extension
- Gmail account (for email notifications)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/leadflow.git
cd leadflow
```

### 2. Backend Setup

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

### 3. Frontend Setup

**Dashboard:**
```bash
cd frontend/dashboard
npm install
npm run dev
# Opens at http://localhost:3001
```

**Chat Widget:**
```bash
cd frontend/widget
npm install
npm run dev
# Opens at http://localhost:3000
```

### 4. Email Notifications (Optional)

```bash
# Get Gmail app password
# Visit: https://myaccount.google.com/apppasswords

# Add to backend/.env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAILS=sales@company.com

# Test email
cd backend
python scripts/test_email.py
```

## 📁 Project Structure

```
leadflow/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST endpoints
│   │   ├── core/           # Business logic (RAG, lead capture)
│   │   ├── services/       # External services (Groq, email)
│   │   ├── db/             # Database operations
│   │   └── models/         # Pydantic schemas
│   ├── scripts/            # Utility scripts
│   └── main.py             # Application entry point
│
├── frontend/
│   ├── dashboard/          # Admin dashboard (React + Vite)
│   │   ├── src/
│   │   │   ├── pages/      # Dashboard, Analytics, Leads, Conversations
│   │   │   ├── components/ # Reusable UI components
│   │   │   └── services/   # API client
│   │   └── public/
│   │
│   └── widget/             # Embeddable chat widget (React + Vite)
│       ├── src/
│       │   └── components/ # ChatWindow, ChatBubble
│       └── public/
│
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **AI**: Groq (Llama 3.3 70B)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Database**: PostgreSQL + pgvector
- **Email**: SMTP (Gmail/SendGrid/AWS SES)

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP**: Axios

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message, get AI response |
| `GET` | `/api/leads` | Get all captured leads |
| `GET` | `/api/analytics` | Get analytics data |
| `GET` | `/api/conversations` | Get all conversations |
| `GET` | `/api/conversations/{id}` | Get conversation details |
| `POST` | `/api/knowledge/ingest` | Add knowledge base content |
| `GET` | `/health` | Health check |

## 🎯 How It Works

### 1. User Interaction
```
User visits website → Opens chat widget → Asks questions
```

### 2. AI Response (RAG Pipeline)
```
User message → Embed query → Vector search → Retrieve context → 
Generate response with Llama 3.3 → Return to user
```

### 3. Lead Capture
```
Detect intent → Qualify lead → Ask for email → 
Save to database → Send email notification (background task)
```

### 4. Email Notification
```
Lead captured → Background task queued → SMTP send → 
Sales team receives email (1-2 seconds) → Click link → View conversation
```

## 📧 Email Notifications

When a lead is captured, your sales team receives:

**Subject:** 🎯 New Lead Captured: [Name]

**Content:**
- 🔥 Lead quality badge (Hot/Warm/Cold)
- Name, email, intent, timestamp
- Direct link to conversation history
- Pro tip: "Respond within 5 minutes to increase conversion by 21x"

**Setup:**
```bash
# See backend/EMAIL_SETUP.md for detailed guide
python scripts/check_email_config.py  # Verify config
python scripts/test_email.py          # Send test email
```

## 📊 Analytics

Track key metrics in the dashboard:

- **Total Conversations** - All chat sessions
- **Leads Captured** - Email addresses collected
- **Conversion Rate** - Leads / Conversations
- **Avg Messages** - Engagement per conversation
- **Lead Quality** - Hot/Warm/Cold breakdown
- **Intent Distribution** - What users want
- **Time Series** - Trends over time

## 🎨 Customization

### Knowledge Base

Add your business information:

```bash
# Edit backend/scripts/ingest_knowledge.py
# Add your content (text, PDFs, URLs)
python scripts/ingest_knowledge.py
```

### Chat Widget Styling

```javascript
// frontend/widget/src/index.css
// Customize colors, fonts, positioning
```

### Email Templates

```python
# backend/app/services/email_service.py
# Edit _build_email_template() method
```

## 🚢 Deployment

### Backend (Railway/Render/Fly.io)

```bash
# Set environment variables
SUPABASE_DB_URL=postgresql://...
GROQ_API_KEY=gsk_...
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAILS=sales@company.com

# Deploy
railway up  # or render deploy, fly deploy
```

### Frontend (Vercel/Netlify)

```bash
# Dashboard
cd frontend/dashboard
vercel deploy

# Widget
cd frontend/widget
vercel deploy
```

### Database (Supabase)

1. Create project at https://supabase.com
2. Enable pgvector extension
3. Run migrations (see backend/db/schema.sql)
4. Update SUPABASE_DB_URL in .env

## 🧪 Testing

### Backend Tests
```bash
cd backend
python scripts/test_rag.py           # Test RAG pipeline
python scripts/test_email.py         # Test email service
python scripts/check_email_config.py # Verify email config
```

### Frontend Tests
```bash
cd frontend/dashboard
npm run build  # Check for build errors

cd frontend/widget
npm run build  # Check for build errors
```

### Integration Test
1. Start backend: `uvicorn main:app --reload`
2. Start widget: `cd frontend/widget && npm run dev`
3. Open http://localhost:3000
4. Chat: "My email is test@example.com"
5. Check inbox for notification email

## 📝 Environment Variables

### Backend (.env)
```bash
# Database
SUPABASE_DB_URL=postgresql://...

# AI
GROQ_API_KEY=gsk_...

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@leadflow.com
NOTIFICATION_EMAILS=sales@company.com,team@company.com
DASHBOARD_URL=http://localhost:3001

# Server
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend (.env)
```bash
# Dashboard
VITE_API_URL=http://localhost:8000

# Widget
VITE_API_URL=http://localhost:8000
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Groq](https://groq.com/) - Lightning-fast LLM inference
- [Supabase](https://supabase.com/) - Open source Firebase alternative
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search
- [Sentence Transformers](https://www.sbert.net/) - State-of-the-art embeddings

## 📞 Support

- **Documentation**: See `/backend/EMAIL_SETUP.md`, `/backend/TESTING_EMAIL.md`
- **Issues**: [GitHub Issues](https://github.com/yourusername/leadflow/issues)
- **Email**: support@leadflow.com

---

**Built with ❤️ for sales teams who want to capture every lead**
