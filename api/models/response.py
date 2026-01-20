"""API response models"""

from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response"""
    success: bool = True
    data: Optional[T] = None
    count: Optional[int] = None
    message: Optional[str] = None
