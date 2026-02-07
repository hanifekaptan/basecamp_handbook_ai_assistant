"""
Vector store for document storage and semantic search using ChromaDB.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger
from backend.app.database.connection import get_db
from backend.app.utils.text_processing import load_markdown_files, clean_text

logger = get_logger(__name__)


class VectorStore:
    """Manages document embeddings and semantic search operations."""
    
    def __init__(self):
        """Initialize embedding model and database connection."""
        self.settings = get_settings()
        self.db = get_db()
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {self.settings.embedding_model}")
        self.embedding_model = SentenceTransformer(self.settings.embedding_model)
        
        # Get collection
        self.collection = self.db.get_collection()
        
        logger.info("VectorStore initialized")
    
    def _chunk_document_by_headers(
        self, 
        content: str, 
        source: str
    ) -> List[Dict[str, Any]]:
        """
        Chunk document using markdown header hierarchy for semantic coherence.
        
        Uses two-stage chunking:
        1. MarkdownHeaderTextSplitter: Split on #, ##, ### headers
        2. RecursiveCharacterTextSplitter: Further split if chunk > chunk_size
        
        Args:
            content: Raw markdown document content
            source: Source file path for metadata
            
        Returns:
            List[Dict]: Chunks with structure:
                - content: Cleaned text content
                - metadata: {source, source_path, Header 1/2/3, chunk_index}
        """
        # Define header hierarchy to split on
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        
        # First split by headers
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )
        
        try:
            header_splits = markdown_splitter.split_text(content)
        except Exception as e:
            logger.warning(f"Header splitting failed for {source}: {e}. Using fallback.")
            # Create a Document-like object for consistency
            from langchain.schema import Document
            header_splits = [Document(page_content=content, metadata={})]
        
        # Further split long sections using recursive splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = []
        for idx, doc in enumerate(header_splits):
            # Access Document attributes directly (not .get())
            text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            
            # Skip empty chunks
            if not text.strip():
                continue
            
            # If chunk is small enough, keep it as is
            if len(text) <= self.settings.chunk_size:
                chunks.append({
                    "content": clean_text(text),
                    "metadata": {
                        "source": Path(source).name,
                        "source_path": source,
                        **metadata,
                        "chunk_index": idx
                    }
                })
            else:
                # Split further if too large
                sub_chunks = text_splitter.split_text(text)
                for sub_idx, sub_chunk in enumerate(sub_chunks):
                    chunks.append({
                        "content": clean_text(sub_chunk),
                        "metadata": {
                            "source": Path(source).name,
                            "source_path": source,
                            **metadata,
                            "chunk_index": f"{idx}_{sub_idx}"
                        }
                    })
        
        return chunks
    
    def index_documents(self, force_reindex: bool = False) -> int:
        """
        Index all markdown documents from the configured directory.
        Smart indexing: only indexes if database is empty or force_reindex is True.
        
        Args:
            force_reindex: If True, clear existing collection and reindex
            
        Returns:
            int: Number of chunks indexed
        """
        # Check if already indexed (smart indexing)
        existing_count = self.collection.count()
        
        if existing_count > 0:
            if not force_reindex:
                logger.info(f"✓ Smart indexing: Database already contains {existing_count} documents. Skipping indexing.")
                return existing_count
            else:
                logger.info(f"Force reindex requested. Resetting collection with {existing_count} existing documents...")
                self.db.reset_collection()
                self.collection = self.db.get_collection()
        else:
            logger.info("Database is empty. Starting initial indexing...")
        
        # Load documents
        logger.info(f"Loading documents from: {self.settings.docs_directory}")
        documents = load_markdown_files(self.settings.docs_directory)
        
        if not documents:
            logger.warning("No documents found to index!")
            return 0
        
        logger.info(f"Found {len(documents)} markdown files")
        
        # Process and chunk all documents
        all_chunks = []
        for source, content in documents:
            chunks = self._chunk_document_by_headers(content, source)
            all_chunks.extend(chunks)
            logger.info(f"Processed {Path(source).name}: {len(chunks)} chunks")
        
        logger.info(f"Total chunks to index: {len(all_chunks)}")
        
        # Generate embeddings and store in ChromaDB
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            
            # Extract content and metadata
            contents = [chunk["content"] for chunk in batch]
            metadatas = [chunk["metadata"] for chunk in batch]
            ids = [f"chunk_{i + j}" for j in range(len(batch))]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(
                contents, 
                show_progress_bar=False,
                convert_to_numpy=True
            ).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Indexed batch {i // batch_size + 1}/{(len(all_chunks) + batch_size - 1) // batch_size}")
        
        total_indexed = self.collection.count()
        logger.info(f"Successfully indexed {total_indexed} chunks")
        return total_indexed
    
    def search(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return (defaults to settings.top_k_results)
            
        Returns:
            List[Dict]: List of relevant documents with metadata
        """
        if top_k is None:
            top_k = self.settings.top_k_results
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query,
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ):
                # Convert distance to similarity score (cosine similarity)
                similarity = 1 - (distance / 2)  # Normalize L2 distance to [0, 1]
                
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "relevance_score": round(similarity, 3)
                })
        
        logger.info(f"Found {len(formatted_results)} relevant documents for query")
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database collection.
        
        Returns:
            Dict: Collection statistics
        """
        doc_count = self.collection.count()
        return {
            "total_documents": doc_count,
            "is_indexed": doc_count > 0,
            "collection_name": self.settings.chroma_collection_name,
            "embedding_model": self.settings.embedding_model
        }
