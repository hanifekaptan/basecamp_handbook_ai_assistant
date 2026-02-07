"""
Metrics endpoints for system monitoring and analytics.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import psutil
from datetime import datetime

from backend.app.api.endpoints.health import get_rag_pipeline
from backend.app.core.logging import get_logger
from backend.app.core.metrics_tracker import get_metrics_tracker
from backend.app.database.connection import get_db

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/performance",
    summary="Performance Metrics",
    description="Get system performance metrics including response times, LLM speed, and vector search performance",
    response_model=Dict[str, Any]
)
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get detailed performance metrics for monitoring.
    
    Returns:
        Dict: Performance metrics including:
            - avg_response_time_ms: Average total response time
            - min_response_time_ms: Fastest response
            - max_response_time_ms: Slowest response
            - llm_performance:
                - avg_generation_time_ms: LLM inference time
                - avg_tokens_per_second: Token generation speed
            - vector_search_performance:
                - avg_search_time_ms: Vector DB search time
                
    Raises:
        HTTPException 500: If metrics collection fails
    """
    try:
        tracker = get_metrics_tracker()
        return tracker.get_performance_metrics()
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get(
    "/usage",
    summary="Usage Statistics",
    description="Get query usage statistics including total queries and success rate",
    response_model=Dict[str, Any]
)
async def get_usage_statistics() -> Dict[str, Any]:
    """
    Get usage statistics for query tracking.
    
    Returns:
        Dict: Usage statistics including:
            - total_queries: Total number of queries processed
            - success_rate: Percentage of successful queries
            - query_distribution:
                - success: Number of successful queries
                - error: Number of failed queries
                
    Raises:
        HTTPException 500: If statistics collection fails
    """
    try:
        tracker = get_metrics_tracker()
        return tracker.get_usage_metrics()
    except Exception as e:
        logger.error(f"Failed to get usage statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get usage statistics: {str(e)}"
        )


@router.get(
    "/system",
    summary="System Health",
    description="Get system resource usage",
    response_model=Dict[str, Any]
)
async def get_system_health() -> Dict[str, Any]:
    """
    Get system resource usage.
    
    Returns:
        Dict: System health information
    """
    try:
        tracker = get_metrics_tracker()
        return tracker.get_system_metrics()
    except Exception as e:
        logger.error(f"Failed to get system health: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )