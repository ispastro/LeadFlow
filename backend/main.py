from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.api import chat, leads, health, knowledge, analytics, conversations, auth
from app.core.embeddings import embedding_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Sales & Support Agent API",
    description="Production-ready AI agent for lead generation and customer support",
    version="1.0.0"
)

# CORS middleware - Must be added BEFORE routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Dashboard
        "http://localhost:3001",  # Widget
        "http://localhost:5173"   # Widget (Vite default fallback)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(leads.router, prefix="/api", tags=["Leads"])
app.include_router(knowledge.router, prefix="/api", tags=["Knowledge"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(conversations.router, prefix="/api", tags=["Conversations"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting AI Sales Agent API...")
    
    # Initialize database connection pool
    from app.db.pg_direct import initialize_pool
    initialize_pool(minconn=2, maxconn=10)
    print("✅ Database connection pool initialized (2-10 connections)")
    
    # Load FastEmbed model (lightweight, fast startup)
    print("📦 Loading FastEmbed model...")
    _ = embedding_service.dimension
    print("✅ FastEmbed loaded!")
    
    print(f"🌐 CORS enabled for: {settings.origins_list}")
    print(f"🔧 Environment: {settings.environment}")
    
    # Check Qdrant
    from app.services.qdrant_service import qdrant_service
    if settings.qdrant_url and settings.qdrant_api_key:
        qdrant_service.configure(settings.qdrant_url, settings.qdrant_api_key)
        if qdrant_service.collection_exists():
            count = qdrant_service.count_documents()
            print(f"✅ Qdrant connected: {count} documents")
        else:
            print("⚠️  Qdrant collection not found. Run: python scripts/ingest_knowledge.py")
    else:
        print("⚠️  Qdrant credentials not configured")
    
    # Configure email service
    from app.services.email_service import email_service
    email_service.configure(settings)
    if email_service.enabled:
        print(f"📧 Email notifications enabled: {email_service.notification_recipients}")
    else:
        print("⚠️  Email notifications disabled (not configured)")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    from app.db.pg_direct import close_pool
    close_pool()
    print("✅ Database connection pool closed")


@app.get("/")
async def root():
    return {
        "message": "AI Sales & Support Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    
    # Fix for Windows multiprocessing
    multiprocessing.freeze_support()
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
