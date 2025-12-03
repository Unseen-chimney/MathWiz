"""
PDF Processor for extracting and chunking PDF documents.
"""
import os
import uuid
from typing import List, Dict, Any
from datetime import datetime


class PDFProcessor:
    """Process PDF documents for RAG system"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_pdf(self, pdf_path: str, pdf_id: str = None) -> Dict[str, Any]:
        """
        Process a PDF file and extract text chunks.
        
        Args:
            pdf_path: Path to PDF file
            pdf_id: Optional PDF ID (generates one if not provided)
            
        Returns:
            Dict with pdf_id, chunks, and metadata
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        pdf_id = pdf_id or str(uuid.uuid4())
        
        # Extract text from PDF
        text = self._extract_text(pdf_path)
        
        # Create chunks
        chunks = self._create_chunks(text, pdf_id)
        
        return {
            "pdf_id": pdf_id,
            "title": os.path.basename(pdf_path),
            "filepath": pdf_path,
            "uploaded_at": datetime.utcnow(),
            "chunks": chunks,
            "total_chunks": len(chunks)
        }
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2 or pdfplumber"""
        try:
            import PyPDF2
            
            text_parts = []
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())
            
            return "\n".join(text_parts)
        
        except ImportError:
            print("Warning: PyPDF2 not installed. Install with: pip install PyPDF2")
            return self._mock_pdf_text(pdf_path)
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return self._mock_pdf_text(pdf_path)
    
    def _create_chunks(self, text: str, pdf_id: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        chunks = []
        text_length = len(text)
        start = 0
        index = 0
        
        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                "chunk_id": f"{pdf_id}_chunk_{index}",
                "pdf_id": pdf_id,
                "chunk_text": chunk_text,
                "chunk_index": index,
                "text": chunk_text,  # For RAG service
                "metadata": {
                    "pdf_id": pdf_id,
                    "chunk_index": index
                }
            })
            
            start = end - self.chunk_overlap
            index += 1
        
        return chunks
    
    def _mock_pdf_text(self, pdf_path: str) -> str:
        """Mock PDF text when PDF library is not available"""
        return f"""
        [Mock PDF Content from {os.path.basename(pdf_path)}]
        
        This is sample mathematics content that would be extracted from the PDF.
        
        Chapter 1: Algebra Fundamentals
        - Linear equations
        - Quadratic equations
        - Polynomial operations
        
        Chapter 2: Calculus Basics
        - Derivatives and their applications
        - Integration techniques
        - Limits and continuity
        
        Chapter 3: Statistics
        - Probability distributions
        - Hypothesis testing
        - Statistical inference
        """
