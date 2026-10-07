import uuid
from typing import List, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import settings
from app.services.embeddings import embeddings_service
from app.utils.logger import logger


class VectorDBService:
    """Service class to manage connections and operations on Qdrant Vector DB."""

    def __init__(self) -> None:
        """Initialize the VectorDBService instance.

        Note: The actual connection is verified lazily.
        """
        self._client: QdrantClient | None = None
        self._initialized = False

    def init_client(self) -> None:
        """Initialize the Qdrant Client, verify connection, and ensure collection exists."""
        if self._initialized:
            return

        logger.info(f"Initializing QdrantClient targeting {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        try:
            self._client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )
            # Verify server connection
            self._client.get_collections()
            logger.info("Successfully verified connection to Qdrant vector database.")

            # Ensure the collection exists
            self._ensure_collection()
            self._initialized = True
        except Exception as e:
            logger.error(f"Qdrant connection/initialization error: {e}", exc_info=True)
            self._client = None
            self._initialized = False
            raise e

    def _ensure_collection(self) -> None:
        """Verify if the configured collection exists, and create it using Cosine distance if missing."""
        if not self._client:
            raise ValueError("QdrantClient is not initialized.")

        collection_name = settings.QDRANT_COLLECTION
        try:
            # Check existing collections
            collections_list = self._client.get_collections().collections
            collection_names = [col.name for col in collections_list]

            if collection_name not in collection_names:
                # Retrieve vector dimension dynamically from embeddings_service
                vector_size = embeddings_service.get_dimension()
                logger.info(
                    f"Collection '{collection_name}' does not exist. "
                    f"Creating collection with vector size: {vector_size} and Cosine distance."
                )
                self._client.create_collection(
                    collection_name=collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=vector_size,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                logger.info(f"Collection '{collection_name}' created successfully.")
            else:
                logger.info(f"Collection '{collection_name}' already exists.")
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection '{collection_name}': {e}", exc_info=True)
            raise e

    def get_client(self) -> QdrantClient:
        """Retrieve the initialized QdrantClient instance.

        Returns:
            QdrantClient: The connection client to the vector DB.

        Raises:
            Exception: If client initialization fails.
        """
        if not self._initialized:
            self.init_client()
        if not self._client:
            raise ValueError("Qdrant client could not be obtained.")
        return self._client

    def check_health(self) -> bool:
        """Check the connection to Qdrant without raising exceptions.

        Returns:
            bool: True if connection is alive, False otherwise.
        """
        try:
            client = self.get_client()
            client.get_collections()
            return True
        except Exception as e:
            logger.warning(f"Healthcheck: Qdrant connectivity test failed: {e}")
            return False

    def index_document(
        self,
        document_id: uuid.UUID,
        filename: str,
        document_type: str,
        document_version: str,
        chunks: List[dict]
    ) -> None:
        """Embed and index document chunks to Qdrant vector database.

        Args:
            document_id (uuid.UUID): ID of the document.
            filename (str): Name of the file.
            document_type (str): Type of the document.
            document_version (str): The document version string.
            chunks (List[dict]): Parsed and ordered document chunks.
        """
        logger.info(f"Embedding Started: Generating embeddings for {filename}")
        client = self.get_client()
        collection_name = settings.QDRANT_COLLECTION

        try:
            # Extract text elements
            texts = [chunk["text"] for chunk in chunks]

            # Generate embeddings in batch
            embeddings = embeddings_service.embed_documents(texts)

            logger.info(f"Qdrant Indexing: Upserting points for {filename}")
            points = []
            for i, chunk in enumerate(chunks):
                vector = embeddings[i]
                # Construct unique point ID from document_id and chunk_index to avoid collisions
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{document_id}_{chunk['chunk_index']}"))

                payload = {
                    "document_id": str(document_id),
                    "document_version": document_version,
                    "filename": filename,
                    "document_type": document_type,
                    "chunk_index": chunk["chunk_index"],
                    "page_number": chunk["page_number"],
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "source": filename,
                    "text": chunk["text"]
                }

                points.append(
                    qmodels.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                )

            # Upsert batch in Qdrant
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Qdrant Indexing Successful: {len(points)} points upserted.")
        except Exception as e:
            logger.error(f"Failed to index document in Qdrant: {e}", exc_info=True)
            raise e

    def delete_document(self, document_id: uuid.UUID) -> None:
        """Delete all points associated with a document ID from Qdrant.

        Args:
            document_id (uuid.UUID): ID of the document to delete.
        """
        logger.info(f"Qdrant Deleting: Removing points for document {document_id}")
        client = self.get_client()
        collection_name = settings.QDRANT_COLLECTION
        try:
            client.delete(
                collection_name=collection_name,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="document_id",
                                match=qmodels.MatchValue(value=str(document_id))
                            )
                        ]
                    )
                )
            )
            logger.info(f"Qdrant Deletion Successful for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to delete document from Qdrant: {e}", exc_info=True)
            raise e

    def search(self, query: str, limit: int = 5) -> List[dict]:
        """Search Qdrant for matching points based on query text semantic similarity.

        Args:
            query (str): The search query string.
            limit (int): The maximum number of points to return.

        Returns:
            List[dict]: Scored results with payload details.
        """
        return self.search_with_filter(query=query, filters={}, limit=limit)

    def search_with_filter(
        self,
        query: str,
        filters: dict,
        limit: int = 5
    ) -> List[dict]:
        """Search Qdrant for matching points based on semantic similarity and metadata filters.

        Args:
            query (str): The search query string.
            filters (dict): Dictionary of metadata filters:
                - document_type
                - document_id
                - filename
                - document_version
                - document_ids (List of valid document IDs, used for latest version filtering)
            limit (int): The maximum number of points to return.

        Returns:
            List[dict]: Scored results with payload details.
        """
        logger.info(f"Searching Qdrant for query: '{query[:50]}' with filters: {filters}")
        client = self.get_client()
        collection_name = settings.QDRANT_COLLECTION
        try:
            # Generate query embedding
            query_vector = embeddings_service.embed_query(query)

            # Construct dynamic filters
            must_conditions = []

            if filters:
                if "document_type" in filters and filters["document_type"]:
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key="document_type",
                            match=qmodels.MatchValue(value=filters["document_type"])
                        )
                    )
                if "document_id" in filters and filters["document_id"]:
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchValue(value=str(filters["document_id"]))
                        )
                    )
                if "filename" in filters and filters["filename"]:
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key="filename",
                            match=qmodels.MatchValue(value=filters["filename"])
                        )
                    )
                if "document_version" in filters and filters["document_version"]:
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key="document_version",
                            match=qmodels.MatchValue(value=filters["document_version"])
                        )
                    )
                if "document_ids" in filters and filters["document_ids"]:
                    must_conditions.append(
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchAny(any=[str(d_id) for d_id in filters["document_ids"]])
                        )
                    )

            query_filter = qmodels.Filter(must=must_conditions) if must_conditions else None

            # Perform query points search
            results = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit
            )

            search_results = []
            for hit in results.points:
                search_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
            return search_results
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}", exc_info=True)
            raise e

    def get_document_chunks(self, document_id: uuid.UUID) -> List[dict]:
        """Retrieve all vector points associated with a specific document ID.

        Args:
            document_id (uuid.UUID): ID of the document.

        Returns:
            List[dict]: List of points containing payload.
        """
        logger.info(f"Retrieving Qdrant chunks for document {document_id}")
        client = self.get_client()
        collection_name = settings.QDRANT_COLLECTION
        try:
            # Scroll points with filter
            scroll_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="document_id",
                        match=qmodels.MatchValue(value=str(document_id))
                    )
                ]
            )

            points, _ = client.scroll(
                collection_name=collection_name,
                scroll_filter=scroll_filter,
                limit=10000,
                with_payload=True,
                with_vectors=False
            )

            # Sort by chunk_index to maintain order
            chunks = []
            for pt in points:
                chunks.append({
                    "id": pt.id,
                    "payload": pt.payload
                })

            chunks.sort(key=lambda x: x["payload"].get("chunk_index", 0))
            return chunks
        except Exception as e:
            logger.error(f"Failed to scroll document chunks in Qdrant: {e}", exc_info=True)
            raise e


# Singleton instance
vectordb_service = VectorDBService()