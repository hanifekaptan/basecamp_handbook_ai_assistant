"""
Rate limiting middleware using slowapi.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from typing import Callable

from backend.app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute", "1000/hour"],
    storage_uri="memory://"
)


def get_limiter() -> Limiter:
    """
    Get rate limiter instance.
    
    Returns:
        Limiter: Rate limiter instance
    """
    return limiter


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        request: FastAPI request
        exc: Rate limit exceeded exception
        
    Returns:
        Response: Error response
    """
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}: {exc.detail}")
    return await _rate_limit_exceeded_handler(request, exc)
