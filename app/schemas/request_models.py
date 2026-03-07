from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    user_id: Optional[str] = Field(None, description="Optional user identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "message": "Summarize the complaints in the uploaded documents",
                "user_id": "user_42",
            }
        }


class UploadMetadata(BaseModel):
    session_id: Optional[str] = Field(None, description="Associate doc with session")
    description: Optional[str] = Field(None, max_length=500)
