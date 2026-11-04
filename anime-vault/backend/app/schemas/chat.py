from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    role: str
    content: str


class ChatMessageCreate(ChatMessageBase):
    session_id: str
    metadata: Optional[Dict[str, Any]] = None


class ChatMessage(ChatMessageBase):
    id: int
    session_id: str
    user_id: int
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="message_meta")
    tokens_used: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    session_id: str
    last_message: Optional[str] = None
    last_time: Optional[datetime] = None
    message_count: int = 0
