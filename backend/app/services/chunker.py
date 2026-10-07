from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.logger import logger


class ChunkerService:
    """Service to divide extracted text into small semantic chunks for embedding and RAG indexing."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100) -> None:
        """Initialize the RecursiveCharacterTextSplitter.

        Args:
            chunk_size (int): Max character count per chunk.
            chunk_overlap (int): Overlap character count between chunks.
        """
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True
        )

    def chunk_document(self, parsed_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split document pages into ordered, metadata-enriched text chunks.

        Args:
            parsed_pages (List[Dict[str, Any]]): Pages with keys 'page_number' and 'text'.

        Returns:
            List[Dict[str, Any]]: List of dictionary chunks:
                {
                    "chunk_index": int,
                    "page_number": int,
                    "text": str
                }
        """
        logger.info("Chunking Started...")
        chunks = []
        chunk_index = 0

        for page in parsed_pages:
            page_num = page.get("page_number")
            text = page.get("text", "")
            if not text.strip():
                continue

            # Split page text
            split_texts = self._splitter.split_text(text)
            for chunk_text in split_texts:
                chunks.append({
                    "chunk_index": chunk_index,
                    "page_number": page_num,
                    "text": chunk_text
                })
                chunk_index += 1

        logger.info(f"Chunking Completed: Generated {len(chunks)} chunks.")
        return chunks


# Singleton service instance
chunker_service = ChunkerService()
