"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

from backend.app.api.router import api_router
from backend.app.core import get_settings, setup_logging, get_logger
from backend.app.core.rate_limiting import get_limiter, rate_limit_exceeded_handler

# Setup logging
settings = get_settings()
setup_logging(
    log_level=settings.log_level,
    log_dir=settings.log_dir
)
logger = get_logger(__name__)
limiter = get_limiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Basecamp Handbook RAG API v2.0...")
    logger.info(f"Configuration: {settings.app_title} v{settings.app_version}")
    logger.info(f"Ollama: {settings.ollama_base_url}")
    logger.info(f"Model: {settings.ollama_model}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down Basecamp Handbook RAG API...")
    logger.info("=" * 60)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description="""
        # Local RAG API for Basecamp Employee Handbook
        
        This API enables question-answering over the Basecamp Employee Handbook using 
        a local LLM (Ollama llama3.2:3b) and vector-based semantic search (ChromaDB + all-MiniLM-L6-v2).
        
        ## 🎯 Key Features
        
        - **Semantic Search**: ChromaDB with sentence-transformers for contextual retrieval
        - **Markdown-Aware Chunking**: Preserves document structure using header-based splitting
        - **Local LLM**: Ollama integration - no external API costs or privacy concerns
        - **Streaming Responses**: Real-time answer generation with SSE
        - **Source Attribution**: Every answer includes source documents with relevance scores
        - **Grounding**: Answers strictly based on retrieved context to prevent hallucinations
        
        ## 🏗️ Architecture
        
        **RAG Pipeline:**
        1. **Question** → Embedding (all-MiniLM-L6-v2)
        2. **Retrieval** → Top-K similar chunks from ChromaDB
        3. **Context Building** → Format with source attribution
        4. **Generation** → Llama 3.1 8B produces grounded answer
        
        **Tech Stack:**
        - Vector DB: ChromaDB (persistent storage)
        - Embeddings: sentence-transformers/all-MiniLM-L6-v2
        - LLM: Ollama (llama3.2:3b - faster, efficient)
        - Chunking: LangChain MarkdownHeaderTextSplitter
        
        ## 📚 Endpoints
        
        ### System Health
        - `GET /api/v1/health` - Service status, Ollama availability, indexed docs count
        
        ### RAG Operations
        - `POST /api/v1/ask` - Ask a question (JSON response)
        - `POST /api/v1/ask/stream` - Ask a question (streaming SSE response)
        
        ### Metrics & Monitoring
        - `GET /api/v1/metrics/performance` - CPU, memory, disk usage
        - `GET /api/v1/metrics/usage` - Vector DB and LLM usage statistics
        - `GET /api/v1/metrics/system` - Overall system health score
        
        ## 🚀 Quick Start
        
        ```bash
        # 1. Check health
        GET /api/v1/health
        
        # 2. Ask a question
        POST /api/v1/ask
        {
          "question": "What is the vacation policy?"
        }
        
        # 3. Get streaming response
        POST /api/v1/ask/stream
        {
          "question": "Tell me about employee benefits"
        }
        ```
        
        ## 📖 Documentation
        
        - OpenAPI Docs: `/docs` (this page)
        - ReDoc: `/redoc`
        - GitHub: [Repository Link]
        """,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    
    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Basecamp Handbook RAG API v2.0",
            "version": settings.app_version,
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
            "api_prefix": settings.api_v1_prefix
        }
    
    logger.info("FastAPI application created successfully")
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    logger.info("Starting Uvicorn server...")
    logger.info(f"Server URL: http://0.0.0.0:8000")
    logger.info(f"API Docs: http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
