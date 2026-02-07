"""
Response schemas for API endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SourceDocument(BaseModel):
    """Schema for source document metadata."""
    content: str = Field(..., description="Document content snippet")
    source: str = Field(..., description="Source file name")
    relevance_score: Optional[float] = Field(None, description="Relevance score")


class AnswerResponse(BaseModel):
    """Schema for answer response."""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(
        default_factory=list,
        description="List of source documents used"
    )
    question: str = Field(..., description="Original question")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer": "At Basecamp, employees receive...",
                "sources": [
                    {
                        "content": "Vacation policy details...",
                        "source": "benefits-and-perks.md",
                        "relevance_score": 0.89
                    }
                ],
                "question": "What are the vacation policies?"
            }
        }
    )


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    ollama_available: bool = Field(..., description="Ollama service availability")
    documents_indexed: int = Field(..., description="Number of indexed documents")


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Error type")
