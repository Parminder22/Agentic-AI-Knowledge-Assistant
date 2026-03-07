from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    answer: str
    tool_used: Optional[str] = None
    sources: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UploadResponse(BaseModel):
    success: bool
    filename: str
    chunks_created: int
    doc_id: str
    message: str


class HistoryMessage(BaseModel):
    message_id: str
    role: str  # "user" or "assistant"
    content: str
    tool_used: Optional[str] = None
    timestamp: datetime


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[HistoryMessage]
    total: int


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict[str, str]
