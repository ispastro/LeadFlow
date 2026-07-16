import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from app.api import chat, leads, health, analytics, conversations, auth, knowledge_mgmt
from app.api import graph as graph_router
from app.core.embeddings import embedding_service

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "root": {
        "level": "INFO" if settings.environment == "production" else "DEBUG",
        "handlers": ["console"],
    },
    "loggers": {
        "uvicorn.access": {"level": "WARNING", "propagate": False, "handlers": ["console"]},
        "httpx":          {"level": "WARNING", "propagate": False},
        "qdrant_client":  {"level": "WARNING", "propagate": False},
        "langchain":      {"level": "WARNING", "propagate": False},
        "langgraph":      {"level": "INFO",    "propagate": False, "handlers": ["console"]},
    },
}
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LeadFlow RevOps Engine (env=%s)", settings.environment)

    # 1. Postgres connection pool
    from app.db.pg_direct import initialize_pool
    initialize_pool(minconn=2, maxconn=10)
    logger.info("DB connection pool ready")

    # 2. Embedding model
    _ = embedding_service.dimension
    logger.info("FastEmbed model loaded (dim=%d)", embedding_service.dimension)

    # 3. Qdrant
    from app.services.qdrant_service import qdrant_service
    if settings.qdrant_url and settings.qdrant_api_key:
        qdrant_service.configure(settings.qdrant_url, settings.qdrant_api_key)
        if qdrant_service.collection_exists():
            logger.info("Qdrant connected — %d documents", qdrant_service.count_documents())
        else:
            logger.warning("Qdrant collection not found. Run: python scripts/ingest_knowledge.py")
    else:
        logger.warning("Qdrant credentials not configured")

    # 4. LangSmith
    logger.info(
        "LangSmith tracing: %s",
        "ENABLED → " + settings.langchain_project if settings.langsmith_enabled else "DISABLED",
    )

    # 5. LangGraph checkpointer (async SQLite — zero infra required locally)
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    from app.db.checkpointer import set_checkpointer
    from app.graph.builder import build_graph, set_graph

    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
        set_checkpointer(checkpointer)
        logger.info("SQLite checkpointer ready → checkpoints.db")

        revops_graph = build_graph(checkpointer)
        set_graph(revops_graph)
        logger.info("RevOps graph compiled and ready")

        logger.info("CORS origins: %s", settings.origins_list)

        yield  # ← application serves requests here

    # Cleanup
    from app.db.pg_direct import close_pool
    close_pool()
    logger.info("Shutdown complete")


app = FastAPI(
    title="LeadFlow RevOps Engine",
    description=(
        "AI-powered Revenue Operations Engine — "
        "LangGraph state machine, structured qualification, "
        "brand-guardrailed responses, and HITL governance."
    ),
    version="2.0.0",
    docs_url="/docs"  if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(health.router,         tags=["Health"])
app.include_router(auth.router,           prefix="/api", tags=["Auth"])
app.include_router(graph_router.router,   prefix="/api", tags=["RevOps Graph"])
app.include_router(chat.router,           prefix="/api", tags=["Chat (Legacy)"])
app.include_router(leads.router,          prefix="/api", tags=["Leads"])
app.include_router(knowledge_mgmt.router, prefix="/api", tags=["Knowledge"])
app.include_router(analytics.router,      prefix="/api", tags=["Analytics"])
app.include_router(conversations.router,  prefix="/api", tags=["Conversations"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "LeadFlow RevOps Engine",
        "version": "2.0.0",
        "status": "running",
        "graph_endpoint": "/api/graph/invoke",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )
