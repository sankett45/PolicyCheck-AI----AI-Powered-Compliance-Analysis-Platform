import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings class that loads and holds all environment configurations."""

    # -------------------- Groq --------------------
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b")

    # -------------------- Database --------------------
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # -------------------- Qdrant --------------------
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "audit_documents")

    # -------------------- Embeddings --------------------
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

    # -------------------- Directories --------------------
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    REPORT_DIR: str = os.getenv("REPORT_DIR", "reports")

    # -------------------- Phase 4E Human-in-the-Loop --------------------
    RETRIEVAL_CONFIDENCE_REVIEW_THRESHOLD: float = float(os.getenv("RETRIEVAL_CONFIDENCE_REVIEW_THRESHOLD", "0.50"))
    COMPLIANCE_CONFIDENCE_REVIEW_THRESHOLD: float = float(os.getenv("COMPLIANCE_CONFIDENCE_REVIEW_THRESHOLD", "0.50"))
    CRITICAL_RISK_REQUIRES_REVIEW: bool = os.getenv("CRITICAL_RISK_REQUIRES_REVIEW", "true").lower() == "true"

    def __init__(self) -> None:

        """Initialize and validate settings."""
        # Ensure directories exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.REPORT_DIR, exist_ok=True)


# Singleton settings object
settings = Settings()