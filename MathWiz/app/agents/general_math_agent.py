"""
General Math Agent - Handles general math problems.
"""
from typing import Dict, Any
import uuid
from datetime import datetime
from .base_agent import BaseAgent


class GeneralMathAgent(BaseAgent):
    """Agent for general math problems"""
    
    def __init__(self, llm_service=None):
        super().__init__("General Math Agent", llm_service)
        self.capabilities = [
            "arithmetic",
            "geometry",
            "trigonometry",
            "word problems",
            "general mathematics"
        ]
        self.keywords = [
            "calculate", "compute", "find", "what is", "math",
            "geometry", "triangle", "circle", "angle", "area", "volume"
        ]
    
    def can_handle(self, problem: str) -> bool:
        """General math agent can handle any problem as fallback"""
        return True  # Fallback agent
    
    def solve(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve a general math problem using LLM.
        
        Args:
            problem: The math problem
            context: Additional context from RAG or conversation
            
        Returns:
            Solution dictionary
        """
        prompt = self._prepare_prompt(problem, context)
        
        if self.llm_service:
            answer = self.llm_service.generate(prompt)
        else:
            answer = f"[General Math Agent] Solution for: {problem}\n(LLM service not configured)"
        
        solution = {
            "solution_id": str(uuid.uuid4()),
            "question": problem,
            "answer": answer,
            "agent": self.name,
            "method_source": "LLM + General Math Knowledge",
            "confidence": 0.80,
            "created_at": datetime.utcnow()
        }
        
        return solution
    
    def _prepare_prompt(self, problem: str, context: Dict[str, Any] = None) -> str:
        """Prepare prompt for LLM"""
        prompt = f"""You are a mathematics expert. Solve the following problem step by step.

Problem: {problem}
"""
        
        if context and context.get("rag_results"):
            prompt += f"\nRelevant context from textbooks:\n{context['rag_results']}\n"
        
        prompt += "\nProvide a clear, step-by-step solution."
        
        return prompt
