import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.schema import Document
from app.utils.logger import logger


class PostgresService:
    """Service to handle CRUD database operations for document ingestion metadata."""

    def create_document(
        self,
        db: Session,
        filename: str,
        document_type: str,
        file_path: str,
        chunk_count: int,
        document_version: str = "1.0.0",
        status: str = "processing",
        doc_id: Optional[uuid.UUID] = None
    ) -> Document:
        """Create a new document ingestion record in PostgreSQL.

        Args:
            db (Session): Database session.
            filename (str): Original filename of the uploaded document.
            document_type (str): Type of the document.
            file_path (str): File storage path on disk.
            chunk_count (int): Number of text chunks generated.
            document_version (str): The document version string.
            status (str): Current processing status.
            doc_id (Optional[uuid.UUID]): Document identifier.

        Returns:
            Document: The created Document database model instance.
        """
        logger.info(f"PostgreSQL Save: Creating record for {filename} (v{document_version})")
        try:
            db_doc = Document(
                id=doc_id or uuid.uuid4(),
                filename=filename,
                document_type=document_type,
                document_version=document_version,
                file_path=file_path,
                chunk_count=chunk_count,
                status=status
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)
            return db_doc
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create document record for {filename}: {e}", exc_info=True)
            raise e

    def get_documents(self, db: Session) -> List[Document]:
        """Retrieve all document ingestion records.

        Args:
            db (Session): Database session.

        Returns:
            List[Document]: List of all Document metadata records.
        """
        try:
            return db.query(Document).all()
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}", exc_info=True)
            raise e

    def get_document_by_id(self, db: Session, document_id: uuid.UUID) -> Optional[Document]:
        """Retrieve a specific document ingestion record by UUID.

        Args:
            db (Session): Database session.
            document_id (uuid.UUID): ID of the document.

        Returns:
            Optional[Document]: The Document instance if found, else None.
        """
        try:
            return db.query(Document).filter(Document.id == document_id).first()
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {e}", exc_info=True)
            raise e

    def delete_document(self, db: Session, document_id: uuid.UUID) -> bool:
        """Delete a document record by UUID.

        Args:
            db (Session): Database session.
            document_id (uuid.UUID): ID of the document to delete.

        Returns:
            bool: True if deleted successfully, False if document did not exist.
        """
        logger.info(f"PostgreSQL Delete: Removing record for document {document_id}")
        try:
            db_doc = self.get_document_by_id(db, document_id)
            if db_doc:
                db.delete(db_doc)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete document record {document_id}: {e}", exc_info=True)
            raise e

    def update_document_status(self, db: Session, document_id: uuid.UUID, status: str) -> Optional[Document]:
        """Update the ingestion status of a document.

        Args:
            db (Session): Database session.
            document_id (uuid.UUID): ID of the document.
            status (str): The new status string to apply.

        Returns:
            Optional[Document]: The updated Document instance if found, else None.
        """
        try:
            db_doc = self.get_document_by_id(db, document_id)
            if db_doc:
                db_doc.status = status
                db.commit()
                db.refresh(db_doc)
                return db_doc
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update document status for {document_id}: {e}", exc_info=True)
            raise e

    def get_latest_documents(self, db: Session) -> List[Document]:
        """Retrieve the latest version of each document grouped by filename.

        Args:
            db (Session): Database session.

        Returns:
            List[Document]: List of the latest version of each document.
        """
        try:
            from sqlalchemy import func
            subq = db.query(
                Document.filename,
                func.max(Document.uploaded_at).label("max_uploaded_at")
            ).group_by(Document.filename).subquery()

            return db.query(Document).join(
                subq,
                (Document.filename == subq.c.filename) &
                (Document.uploaded_at == subq.c.max_uploaded_at)
            ).all()
        except Exception as e:
            logger.error(f"Failed to retrieve latest documents: {e}", exc_info=True)
            raise e


# Singleton service instance
postgres_service = PostgresService()

