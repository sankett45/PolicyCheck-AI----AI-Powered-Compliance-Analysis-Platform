import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Pydantic model representing document metadata in API responses."""

    id: uuid.UUID
    filename: str
    document_type: str
    document_version: str
    file_path: str
    chunk_count: int
    uploaded_at: datetime
    status: str

    class Config:
        from_attributes = True


class UploadSummaryResponse(BaseModel):
    """Pydantic model representing the response for a successful upload ingestion."""

    document_id: uuid.UUID
    filename: str
    document_type: str
    document_version: str
    chunk_count: int
    status: str


class EvidenceResponse(BaseModel):
    """Pydantic model representing structured search evidence returned by retrieval services."""

    document_id: uuid.UUID
    document_version: str
    filename: str
    document_type: str
    page_number: Optional[int] = None
    chunk_index: int
    similarity_score: float
    text: str

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Validation schema for document semantic search requests."""

    query: str = Field(..., min_length=1, description="Semantic text query to search for")
    document_type: Optional[str] = Field(None, description="Optional document type to filter by")
    document_version: Optional[str] = Field(None, description="Optional document version to retrieve from")


class RetrieveRequest(BaseModel):
    """Validation schema for RAG retrieve requests."""

    question: str = Field(..., min_length=1, description="Compliance question to find evidence for")


class RetrieveResponse(BaseModel):
    """Validation schema for RAG retrieve responses containing partitioned evidence packages."""

    company_policy: List[EvidenceResponse]
    regulations: List[EvidenceResponse]
