"""
Database models for MathWiz system.
Based on the database schema diagram.
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "user"
    
    user_id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")


class PDFDocument(Base):
    """PDF Document model"""
    __tablename__ = "pdf_document"
    
    pdf_id = Column(String, primary_key=True)
    title = Column(String)
    filepath = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunks = relationship("PDFChunk", back_populates="document")


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversation"
    
    convo_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.user_id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    tasks = relationship("TaskLog", back_populates="conversation")


class Feedback(Base):
    """Feedback model"""
    __tablename__ = "feedback"
    
    feedback_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("user.user_id"))
    message = Column(Text)
    rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")


class PDFChunk(Base):
    """PDF Chunk model for RAG system"""
    __tablename__ = "pdf_chunk"
    
    chunk_id = Column(String, primary_key=True)
    pdf_id = Column(String, ForeignKey("pdf_document.pdf_id"))
    chunk_text = Column(Text)
    chunk_index = Column(Integer)
    
    # Relationships
    document = relationship("PDFDocument", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False)


class Message(Base):
    """Message model"""
    __tablename__ = "message"
    
    message_id = Column(String, primary_key=True)
    convo_id = Column(String, ForeignKey("conversation.convo_id"))
    sender = Column(String)  # 'user' or 'agent'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class TaskLog(Base):
    """Task log for tracking agent operations"""
    __tablename__ = "task_log"
    
    task_id = Column(String, primary_key=True)
    convo_id = Column(String, ForeignKey("conversation.convo_id"))
    agent_name = Column(String)
    tool_used = Column(String)
    task_type = Column(String)
    status = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="tasks")
    solution = relationship("SolutionRecord", back_populates="task", uselist=False)
    reflection = relationship("ReflectionLog", back_populates="task", uselist=False)
    llm_calls = relationship("LLMCall", back_populates="task")


class SolutionRecord(Base):
    """Solution record for math problems"""
    __tablename__ = "solution_record"
    
    solution_id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("task_log.task_id"))
    question = Column(Text)
    answer = Column(Text)
    method_source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("TaskLog", back_populates="solution")


class ReflectionLog(Base):
    """Reflection log for agent self-evaluation"""
    __tablename__ = "reflection_log"
    
    reflect_id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("task_log.task_id"))
    evaluation = Column(Text)
    suggestion = Column(Text)
    final_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("TaskLog", back_populates="reflection")


class Embedding(Base):
    """Embedding model for vector storage"""
    __tablename__ = "embedding"
    
    embedding_id = Column(String, primary_key=True)
    chunk_id = Column(String, ForeignKey("pdf_chunk.chunk_id"))
    vector = Column(Text)  # Stored as JSON string
    
    # Relationships
    chunk = relationship("PDFChunk", back_populates="embedding")


class LLMCall(Base):
    """LLM call tracking for cost and monitoring"""
    __tablename__ = "llm_call"
    
    llm_call_id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("task_log.task_id"))
    model_name = Column(String)
    request_payload = Column(Text)
    response_payload = Column(Text)
    cost_estimate = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("TaskLog", back_populates="llm_calls")
