from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.api import chat, leads, health
from app.core.embeddings import embedding_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Sales & Support Agent API",
    description="Production-ready AI agent for lead generation and customer support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(leads.router, prefix="/api", tags=["Leads"])


@app.on_event("startup")
async def startup_event():
    """Load models and initialize services on startup"""
    print("🚀 Starting AI Sales Agent API...")
    print("📦 Loading Sentence Transformer model...")
    # This triggers model loading
    _ = embedding_service.dimension
    print("✅ Model loaded successfully!")
    print(f"🌐 CORS enabled for: {settings.origins_list}")
    print(f"🔧 Environment: {settings.environment}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Sales & Support Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
