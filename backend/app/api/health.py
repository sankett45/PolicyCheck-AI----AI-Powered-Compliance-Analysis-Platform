from fastapi import APIRouter
from sqlalchemy import text
from app.database.connection import SessionLocal
from app.services.llm import llm_service
from app.services.embeddings import embeddings_service
from app.services.vectordb import vectordb_service
from app.utils.logger import logger

router = APIRouter()


@router.get("")
@router.get("/")
def health() -> dict:
    """Verify health status of all external services and the FastAPI application."""
    status = "healthy"
    services = {
        "groq": "disconnected",
        "postgres": "disconnected",
        "qdrant": "disconnected",
        "embeddings": "failed"
    }

    # 1. Neon PostgreSQL check
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        services["postgres"] = "connected"
    except Exception as e:
        logger.error(f"Healthcheck: PostgreSQL check failed: {e}")
        services["postgres"] = "disconnected"
        status = "unhealthy"
    finally:
        if db:
            db.close()

    # 2. Qdrant check
    try:
        if vectordb_service.check_health():
            services["qdrant"] = "connected"
        else:
            services["qdrant"] = "disconnected"
            status = "unhealthy"
    except Exception as e:
        logger.error(f"Healthcheck: Qdrant check failed: {e}")
        services["qdrant"] = "disconnected"
        status = "unhealthy"

    # 3. Embedding model check
    try:
        embeddings_service.embed_query("healthcheck")
        services["embeddings"] = "loaded"
    except Exception as e:
        logger.error(f"Healthcheck: Embeddings model check failed: {e}")
        services["embeddings"] = "failed"
        status = "unhealthy"

    # 4. Groq LLM check
    try:
        llm_service.invoke("ping")
        services["groq"] = "connected"
    except Exception as e:
        logger.error(f"Healthcheck: Groq LLM check failed: {e}")
        services["groq"] = "disconnected"
        status = "unhealthy"

    return {
        "status": status,
        "services": services
    }