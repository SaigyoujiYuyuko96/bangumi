from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageResult(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    page_size: int


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
