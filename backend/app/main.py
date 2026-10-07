from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.audit import router as audit_router
from app.api.review import router as review_router
from app.api.reports import router as reports_router
from app.database.connection import engine, Base
from app.database import schema  # Required to register models with Base.metadata
from app.utils.logger import logger



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager for startup and shutdown event lifecycle."""
    # Automatically create database tables if they do not exist
    Base.metadata.create_all(bind=engine)

    # Initialize checkpointer database tables (if supported)
    from app.graph.workflow import checkpointer
    if hasattr(checkpointer, "setup"):
        try:
            logger.info("Initializing Postgres checkpointer database tables...")
            checkpointer.setup()
            logger.info("Postgres checkpointer database tables initialized.")
        except Exception as e:
            logger.error(f"Failed to setup Postgres checkpointer: {e}", exc_info=True)

    yield


app = FastAPI(
    title="AuditFlow AI",
    version="1.0.0",
    description="Enterprise-grade AI Compliance & Audit Assistant",
    lifespan=lifespan
)

# Enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints and routers
app.include_router(
    health_router,
    prefix="/health",
    tags=["Health"]
)

app.include_router(
    upload_router,
    tags=["Document Ingestion"]
)

app.include_router(
    search_router,
    tags=["RAG Retrieval"]
)

app.include_router(
    audit_router,
    tags=["Audit Workflow"]
)

app.include_router(
    review_router,
    tags=["Audit Workflow"]
)

app.include_router(
    reports_router,
    tags=["Audit Workflow"]
)







@app.get("/")
def root() -> dict:
    """Root GET endpoint returning a running message."""
    return {
        "message": "AuditFlow AI Backend Running"
    }
