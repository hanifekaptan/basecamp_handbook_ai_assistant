"""
Health check endpoint.
"""
from fastapi import APIRouter, HTTPException, status

from backend.app.schemas import HealthResponse
from backend.app.services.rag_pipeline import RAGPipeline
from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Singleton RAG pipeline
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
        _rag_pipeline.initialize()
    return _rag_pipeline


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the service is running and all components (Ollama, ChromaDB) are available",
    tags=["System"]
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status and component availability.
    
    Checks:
    - API service is running
    - Ollama LLM is reachable and model is loaded
    - ChromaDB has indexed documents
    
    Returns:
        HealthResponse: Service health status with:
            - status: "healthy" or "degraded"
            - version: API version string
            - ollama_available: Whether LLM is ready
            - documents_indexed: Number of documents in vector DB
        
    Raises:
        HTTPException 503: If service is unavailable or components are down
    """
    try:
        settings = get_settings()
        pipeline = get_rag_pipeline()
        status_info = await pipeline.get_status()
        
        return HealthResponse(
            status="healthy" if status_info["status"] == "healthy" else "degraded",
            version=settings.app_version,
            ollama_available=status_info["ollama_available"],
            documents_indexed=status_info["vector_db"]["total_documents"]
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )
