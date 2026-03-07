from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


def _uuid():
    return str(uuid.uuid4())


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="session", cascade="all, delete")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    role = Column(String, nullable=False)         # "user" | "assistant"
    content = Column(Text, nullable=False)
    tool_used = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_uuid)
    filename = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    session_id = Column(String, nullable=True)
    chunks_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class ToolLog(Base):
    __tablename__ = "tool_logs"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, nullable=False)
    message_id = Column(String, nullable=True)
    tool_name = Column(String, nullable=False)
    input_data = Column(JSON, nullable=True)
    output_summary = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
