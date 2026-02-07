"""
Request schemas for API endpoints.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class QuestionRequest(BaseModel):
    """Schema for question request."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The question to ask about the Basecamp Employee Handbook"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "What are the vacation policies?"
            }
        }
    )
