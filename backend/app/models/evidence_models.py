import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Pydantic model representing structured compliance evidence."""

    document_id: uuid.UUID = Field(..., description="UUID of the parent document")
    document_version: str = Field(..., description="Version of the document")
    filename: str = Field(..., description="Name of the file from which chunk was extracted")
    document_type: str = Field(..., description="Type of the document (e.g. company_policy, regulation)")
    page_number: Optional[int] = Field(None, description="Page number of the chunk, if available")
    chunk_index: int = Field(..., description="Index of the chunk in the document")
    similarity_score: float = Field(..., description="Similarity score calculated by the search engine")
    text: str = Field(..., description="Text content of the evidence chunk")
    source: str = Field(..., description="Source identifier, usually the filename")

    class Config:
        from_attributes = True


class RetrievalResult(BaseModel):
    """Pydantic model representing the complete structured retrieval response."""

    question: str = Field(..., description="Original question asked")
    company_policy: List[Evidence] = Field(..., description="List of matched company policy evidence objects")
    regulations: List[Evidence] = Field(..., description="List of matched regulation evidence objects")
    confidence: float = Field(..., description="Calculated retrieval confidence score")
    confidence_level: str = Field(..., description="Descriptive confidence level (low, medium, high)")


class SearchRequest(BaseModel):
    """Validation schema for semantic search requests."""

    query: str = Field(..., min_length=1, description="Semantic text query to search for")
    document_type: Optional[str] = Field(None, description="Optional document type to filter by")
    top_k: Optional[int] = Field(5, ge=1, le=100, description="Maximum number of results to return")


class RetrieveRequest(BaseModel):
    """Validation schema for structured retrieve requests."""

    question: str = Field(..., min_length=1, description="Compliance question to find evidence for")
