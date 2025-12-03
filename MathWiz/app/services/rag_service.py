"""
RAG (Retrieval-Augmented Generation) Service.
Handles vector search and context retrieval from PDF documents.
"""
import os
from typing import List, Dict, Any
import uuid


class RAGService:
    """Service for RAG operations with vector database"""
    
    def __init__(self, collection_name: str = "math_textbooks", persist_directory: str = "./chroma_db"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB and embedding function"""
        try:
            import chromadb
            from chromadb.utils import embedding_functions
            
            # Create ChromaDB client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Initialize embedding function (sentence transformers)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            
            print(f"RAG Service initialized with collection: {self.collection_name}")
        
        except ImportError:
            print("Warning: ChromaDB not installed. Install with: pip install chromadb")
            self.client = None
    
    def add_document_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Add document chunks to vector database.
        
        Args:
            chunks: List of dicts with 'chunk_id', 'text', 'metadata'
            
        Returns:
            List of chunk IDs added
        """
        if not self.collection:
            print("Warning: Vector database not initialized")
            return []
        
        chunk_ids = []
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            chunk_id = chunk.get('chunk_id', str(uuid.uuid4()))
            chunk_ids.append(chunk_id)
            documents.append(chunk['text'])
            metadatas.append(chunk.get('metadata', {}))
            ids.append(chunk_id)
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(chunk_ids)} chunks to vector database")
        except Exception as e:
            print(f"Error adding chunks: {e}")
        
        return chunk_ids
    
    def query_relevant_context(self, question: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query vector database for relevant context.
        
        Args:
            question: The question to search for
            n_results: Number of results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        if not self.collection:
            return self._mock_results(question)
        
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
        
        except Exception as e:
            print(f"Error querying vector database: {e}")
            return self._mock_results(question)
    
    def _mock_results(self, question: str) -> List[Dict[str, Any]]:
        """Mock results when vector DB is not available"""
        return [
            {
                'text': f"[Mock Context] Relevant information about: {question}",
                'metadata': {'source': 'mock', 'page': 1},
                'distance': 0.5
            }
        ]
    
    def format_context_for_prompt(self, results: List[Dict[str, Any]]) -> str:
        """Format RAG results into a context string for LLM prompt"""
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Context {i}: {result['text']}")
        
        return "\n\n".join(context_parts)
