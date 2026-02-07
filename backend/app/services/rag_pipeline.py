"""
RAG (Retrieval-Augmented Generation) pipeline orchestration.
"""
from typing import Dict, Any, List, AsyncGenerator

from backend.app.database.vector_store import VectorStore
from backend.app.llm.client import LLMClient
from backend.app.core.logging import get_logger
from backend.app.llm.prompt_manager import get_prompt_manager

logger = get_logger(__name__)


class RAGPipeline:
    """Orchestrates the RAG pipeline: retrieval + generation."""
    
    def __init__(self):
        """Initialize RAG pipeline with vector store and LLM client."""
        self.vector_store = VectorStore()
        self.llm_client = LLMClient()
        self.prompt_manager = get_prompt_manager()
        logger.info("RAG Pipeline initialized")
    
    def initialize(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Initialize the RAG pipeline by indexing documents if needed.
        
        Smart indexing: Only reindexes if database is empty or forced.
        
        Args:
            force_reindex: If True, delete existing data and reindex all documents
            
        Returns:
            Dict: Stats with keys:
                - documents_indexed: Number of documents processed
                - status: "ready" if successful, "no_documents" if no docs found
        """
        logger.info("Initializing RAG pipeline...")
        
        # Index documents
        indexed_count = self.vector_store.index_documents(force_reindex=force_reindex)
        
        stats = {
            "documents_indexed": indexed_count,
            "status": "ready" if indexed_count > 0 else "no_documents"
        }
        
        logger.info(f"RAG pipeline initialized: {stats}")
        return stats
    
    async def answer_question(
        self, 
        question: str,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            question: User's question
            include_sources: Whether to include source documents in response
            
        Returns:
            Dict: Answer with sources and metadata
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        logger.info(f"Processing question: {question}")
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self.vector_store.search(question)
        
        if not relevant_docs:
            logger.warning("No relevant documents found")
            no_context_msg = self.prompt_manager.get_no_context_message()
            return {
                "answer": no_context_msg,
                "sources": [],
                "question": question,
                "metadata": {
                    "documents_retrieved": 0,
                    "confidence": "low"
                }
            }
        
        logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
        
        # Step 2: Generate answer using LLM
        answer = await self.llm_client.generate_answer(
            question, 
            relevant_docs
        )
        
        # Step 3: Format response
        response = {
            "answer": answer,
            "sources": [],
            "question": question,
            "metadata": {
                "documents_retrieved": len(relevant_docs),
                "confidence": "high" if len(relevant_docs) >= 3 else "medium"
            }
        }
        
        # Add source documents if requested
        if include_sources:
            response["sources"] = [
                {
                    "content": doc["content"][:300] + "..." if len(doc["content"]) > 300 else doc["content"],
                    "source": doc["metadata"].get("source", "unknown"),
                    "relevance_score": doc.get("relevance_score", 0.0),
                    "section": doc["metadata"].get("Header 1", "")
                }
                for doc in relevant_docs[:3]  # Only top 3 sources
            ]
        
        logger.info("Question answered successfully")
        return response
    
    async def answer_question_stream(
        self, 
        question: str
    ) -> AsyncGenerator[str, None]:
        """
        Answer a question using the RAG pipeline with streaming response.
        
        Args:
            question: User's question
            
        Yields:
            str: Answer chunks
        """
        if not question or not question.strip():
            yield "Error: Question cannot be empty"
            return
        
        logger.info(f"Processing streaming question: {question}")
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self.vector_store.search(question)
        
        if not relevant_docs:
            logger.warning("No relevant documents found")
            no_context_msg = self.prompt_manager.get_no_context_message()
            yield no_context_msg
            return
        
        logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
        
        # Step 2: Stream answer from LLM
        async for chunk in self.llm_client.generate_answer_stream(
            question, 
            relevant_docs
        ):
            yield chunk
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the RAG pipeline.
        
        Returns:
            Dict: Pipeline status information
        """
        from backend.app.core.config import get_settings
        settings = get_settings()
        
        db_stats = self.vector_store.get_collection_stats()
        ollama_available = await self.llm_client.check_availability()
        
        return {
            "vector_db": db_stats,
            "ollama_available": ollama_available,
            "ollama_url": settings.ollama_base_url,
            "status": "healthy" if ollama_available and db_stats["total_documents"] > 0 else "degraded"
        }
