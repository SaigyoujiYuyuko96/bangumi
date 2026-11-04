from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CollectionBase(BaseModel):
    subject_id: int
    status: str = "wish"
    rate: Optional[int] = None
    ep_status: int = 0
    vol_status: int = 0
    comment: Optional[str] = None
    private: bool = False


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(BaseModel):
    status: Optional[str] = None
    rate: Optional[int] = None
    ep_status: Optional[int] = None
    vol_status: Optional[int] = None
    comment: Optional[str] = None
    private: Optional[bool] = None


class CollectionProgressUpdate(BaseModel):
    ep_status: Optional[int] = None
    vol_status: Optional[int] = None


class Collection(CollectionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
