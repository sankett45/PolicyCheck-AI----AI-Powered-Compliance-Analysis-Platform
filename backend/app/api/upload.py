import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.models.document_models import DocumentResponse, UploadSummaryResponse
from app.services.postgres import postgres_service
from app.services.parser import parser_service
from app.services.chunker import chunker_service
from app.services.vectordb import vectordb_service
from app.utils.logger import logger

router = APIRouter()

SUPPORTED_DOCUMENT_TYPES = {"company_policy", "regulation", "contract", "sop"}
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload", response_model=UploadSummaryResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    document_version: str = Form("1.0.0"),
    db: Session = Depends(get_db)
):
    """Ingest and index a document (PDF, DOCX, TXT) into database metadata and vector indexing."""
    logger.info(f"Upload Started: Received file '{file.filename}' (v{document_version}) with type '{document_type}'")

    # 1. Validation
    if document_type not in SUPPORTED_DOCUMENT_TYPES:
        logger.error(f"Upload Rejected: Unsupported document type '{document_type}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported document type. Supported types: {list(SUPPORTED_DOCUMENT_TYPES)}"
        )

    if not file.filename:
        logger.error("Upload Rejected: Filename is empty")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a valid filename."
        )

    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in SUPPORTED_EXTENSIONS:
        logger.error(f"Upload Rejected: Unsupported format '{ext}' for file '{file.filename}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: {list(SUPPORTED_EXTENSIONS)}"
        )

    # 2. Setup ID and Local Storage Path
    doc_id = uuid.uuid4()
    saved_filename = f"{doc_id}{ext.lower()}"
    local_file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    # Save the file to disk
    try:
        content = await file.read()
        if not content or not content.strip():
            raise ValueError("Uploaded file is empty.")
        
        with open(local_file_path, "wb") as f:
            f.write(content)
    except ValueError as ve:
        logger.error(f"Upload Failed: {ve}")
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Upload Failed: Failed to save file to disk: {e}", exc_info=True)
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file on server disk: {e}"
        )

    # 3. Pipeline Ingestion (Parse -> Chunk -> VectorDB -> DB Save)
    db_doc = None
    try:
        # A. Parsing
        logger.info(f"Parsing Started for file: {file.filename}")
        parsed_pages = parser_service.parse_pages(local_file_path, ext)

        # B. Chunking
        logger.info(f"Chunking Started for file: {file.filename}")
        chunks = chunker_service.chunk_document(parsed_pages)
        if not chunks:
            raise ValueError("Document yielded zero text chunks.")

        # C. PostgreSQL Ingestion (Initial metadata record in 'processing' status)
        db_doc = postgres_service.create_document(
            db=db,
            filename=file.filename,
            document_type=document_type,
            document_version=document_version,
            file_path=local_file_path,
            chunk_count=len(chunks),
            status="processing",
            doc_id=doc_id
        )

        # D. Qdrant Indexing
        logger.info(f"Embedding and Qdrant Indexing Started for file: {file.filename}")
        vectordb_service.index_document(
            document_id=doc_id,
            filename=file.filename,
            document_type=document_type,
            document_version=document_version,
            chunks=chunks
        )

        # E. Update status to 'indexed'
        postgres_service.update_document_status(db, doc_id, "indexed")
        logger.info(f"Upload Completed: Document '{file.filename}' successfully processed and indexed.")

        return UploadSummaryResponse(
            document_id=doc_id,
            filename=file.filename,
            document_type=document_type,
            document_version=document_version,
            chunk_count=len(chunks),
            status="indexed"
        )

    except ValueError as ve:
        # Rollback local file and metadata on validation failure
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
        if db_doc:
            postgres_service.delete_document(db, doc_id)
        logger.error(f"Ingestion failed due to validation: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        # Full rollback on execution exception
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
        try:
            vectordb_service.delete_document(doc_id)
        except Exception as qe:
            logger.warning(f"Failed Qdrant rollback during error recovery: {qe}")
        if db_doc:
            postgres_service.delete_document(db, doc_id)

        logger.error(f"Document ingestion pipeline failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {e}"
        )


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """Retrieve all indexed documents metadata from PostgreSQL."""
    try:
        return postgres_service.get_documents(db)
    except Exception as e:
        logger.error(f"Failed to list documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {e}"
        )


@router.delete("/documents/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete document from PostgreSQL, Qdrant and local file system."""
    logger.info(f"Delete request received for document: {document_id}")

    # 1. Fetch metadata to get file path
    db_doc = postgres_service.get_document_by_id(db, document_id)
    if not db_doc:
        logger.error(f"Delete failed: Document {document_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found."
        )

    errors = []
    # 2. Delete file from disk
    file_path = db_doc.file_path
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Successfully deleted local file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete local file {file_path}: {e}")
            errors.append(f"Disk file deletion failed: {e}")
    else:
        logger.warning(f"File path {file_path} did not exist on disk.")

    # 3. Delete vectors from Qdrant
    try:
        vectordb_service.delete_document(document_id)
    except Exception as e:
        logger.error(f"Failed to delete points from Qdrant for document {document_id}: {e}")
        errors.append(f"Qdrant deletion failed: {e}")

    # 4. Delete metadata from PostgreSQL
    try:
        postgres_service.delete_document(db, document_id)
    except Exception as e:
        logger.error(f"Failed to delete PostgreSQL metadata for document {document_id}: {e}")
        errors.append(f"PostgreSQL metadata deletion failed: {e}")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document deletion encountered errors: {', '.join(errors)}"
        )

    logger.info(f"Delete Completed: Document {document_id} deleted successfully.")
    return {"message": f"Document {document_id} deleted successfully."}
