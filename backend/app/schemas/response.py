"""
Standard response schemas for API endpoints.
"""

from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class StandardResponse(GenericModel, Generic[T]):
    """Standard API response model with consistent structure."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {}
            }
        }
