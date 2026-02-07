"""
Question answering endpoints.
"""
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import StreamingResponse
import time

from backend.app.schemas import (
    QuestionRequest,
    AnswerResponse,
    ErrorResponse,
    SourceDocument
)
from backend.app.api.endpoints.health import get_rag_pipeline
from backend.app.core.logging import get_logger
from backend.app.core.rate_limiting import get_limiter
from backend.app.core.metrics_tracker import get_metrics_tracker

logger = get_logger(__name__)
router = APIRouter()
limiter = get_limiter()


@router.post(
    "/ask",
    response_model=AnswerResponse,
    summary="Ask Question",
    description="Ask a question about the Basecamp Employee Handbook and get an answer with source citations",
    tags=["RAG"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request (empty question, etc.)"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded (20 req/min)"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
@limiter.limit("20/minute")
async def ask_question(request: Request, question_request: QuestionRequest) -> AnswerResponse:
    """
    Ask a question and get an AI-generated answer based on the employee handbook.
    
    The system:
    1. Validates the question
    2. Searches for relevant document chunks (vector similarity)
    3. Generates answer using LLM with retrieved context
    4. Returns answer with source citations and metadata
    
    Rate limited to 20 requests per minute per IP address.
    
    Args:
        request: FastAPI request (for rate limiting)
        question_request: Question request containing the question text
        
    Returns:
        AnswerResponse: Generated answer with sources and metadata:
            - answer: Natural language response
            - sources: Top 3 relevant document chunks
            - metadata: Confidence, document count, response time
        
    Raises:
        HTTPException 400: If question is empty or invalid
        HTTPException 429: If rate limit is exceeded
        HTTPException 500: If processing fails
    """
    try:
        # Track performance
        start_time = time.time()
        
        # Validate question
        if not question_request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        logger.info(f"Processing question: {question_request.question[:100]}...")
        
        # Get pipeline and process question
        pipeline = get_rag_pipeline()
        result = await pipeline.answer_question(
            question_request.question
        )
        
        # Calculate elapsed time
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Format response
        response = AnswerResponse(
            answer=result["answer"],
            sources=[
                SourceDocument(
                    content=src["content"],
                    source=src["source"],
                    relevance_score=src["relevance_score"]
                )
                for src in result.get("sources", [])
            ],
            question=question_request.question
        )
        
        # Track metrics
        tracker = get_metrics_tracker()
        tracker.track_query(
            question=question_request.question,
            response_time_ms=elapsed_ms,
            success=True,
            llm_time_ms=result.get("llm_time_ms", 0),
            vector_search_time_ms=result.get("vector_search_time_ms", 0),
            tokens_generated=len(result["answer"].split())  # Rough estimate
        )
        
        logger.info(f"Question answered successfully in {elapsed_ms:.0f}ms")
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        # Track failed query
        tracker = get_metrics_tracker()
        tracker.track_query(
            question=question_request.question,
            response_time_ms=0,
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        # Track failed query
        tracker = get_metrics_tracker()
        tracker.track_query(
            question=question_request.question,
            response_time_ms=0,
            success=False
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )


@router.post(
    "/ask/stream",
    summary="Ask Question (Streaming)",
    description="Ask a question and get a streaming response",
    tags=["RAG"],
    responses={
        200: {
            "description": "Streaming response",
            "content": {"text/plain": {"example": "This is a streaming answer..."}}
        },
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def ask_question_stream(request: QuestionRequest):
    """
    Ask a question and get a streaming answer.
    
    Args:
        request: Question request containing the question text
        
    Returns:
        StreamingResponse: Server-sent events stream with answer chunks
        
    Raises:
        HTTPException: If question is invalid
    """
    try:
        # Validate question
        if not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        logger.info(f"Processing streaming question: {request.question[:100]}...")
        
        # Get pipeline
        pipeline = get_rag_pipeline()
        
        # Create streaming response
        async def generate():
            try:
                async for chunk in pipeline.answer_question_stream(request.question):
                    yield chunk
                logger.info("Streaming completed successfully")
            except Exception as e:
                logger.error(f"Streaming error: {e}", exc_info=True)
                yield f"\n\n[Error: {str(e)}]"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid streaming request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process streaming request: {str(e)}"
        )
