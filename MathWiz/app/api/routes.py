"""
FastAPI routes for MathWiz API.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from ..services import Orchestrator, LLMService, RAGService, PDFProcessor

router = APIRouter()

# Initialize services
llm_service = LLMService()
rag_service = RAGService()
pdf_processor = PDFProcessor()
orchestrator = Orchestrator(llm_service=llm_service, rag_service=rag_service)


# Request/Response Models
class QuestionRequest(BaseModel):
    question: str
    user_id: str
    convo_id: Optional[str] = None


class QuestionResponse(BaseModel):
    task_id: str
    convo_id: str
    question: str
    answer: str
    agent_used: str
    confidence: float
    timestamp: datetime


class FeedbackRequest(BaseModel):
    user_id: str
    message: str
    rating: int


class PDFUploadRequest(BaseModel):
    pdf_path: str
    pdf_id: Optional[str] = None


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Main endpoint for asking math questions.
    Orchestrator processes the question through the multi-agent system.
    """
    try:
        result = orchestrator.process_question(
            question=request.question,
            user_id=request.user_id,
            convo_id=request.convo_id
        )
        
        return QuestionResponse(
            task_id=result["task_id"],
            convo_id=result["convo_id"],
            question=result["question"],
            answer=result["answer"],
            agent_used=result["agent_used"],
            confidence=result["confidence"],
            timestamp=result["timestamp"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_agents():
    """Get information about available agents and their capabilities."""
    return {
        "agents": orchestrator.get_agent_capabilities()
    }


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback."""
    feedback_id = str(uuid.uuid4())
    
    return {
        "feedback_id": feedback_id,
        "status": "received",
        "message": "Thank you for your feedback!"
    }


@router.post("/pdf/upload")
async def upload_pdf(request: PDFUploadRequest):
    """
    Process and index a PDF document for RAG.
    """
    try:
        # Process PDF
        result = pdf_processor.process_pdf(
            pdf_path=request.pdf_path,
            pdf_id=request.pdf_id
        )
        
        # Add chunks to vector database
        chunk_ids = rag_service.add_document_chunks(result["chunks"])
        
        return {
            "pdf_id": result["pdf_id"],
            "title": result["title"],
            "total_chunks": result["total_chunks"],
            "chunks_indexed": len(chunk_ids),
            "status": "success"
        }
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MathWiz API",
        "timestamp": datetime.utcnow()
    }
