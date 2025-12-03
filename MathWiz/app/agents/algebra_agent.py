"""
Algebra Agent - Specialized in algebra problems.
"""
from typing import Dict, Any
import uuid
from datetime import datetime
from .base_agent import BaseAgent


class AlgebraAgent(BaseAgent):
    """Agent specialized in algebra problems"""
    
    def __init__(self, llm_service=None):
        super().__init__("Algebra Agent", llm_service)
        self.capabilities = [
            "linear equations",
            "quadratic equations",
            "polynomials",
            "factoring",
            "systems of equations"
        ]
        self.keywords = [
            "solve", "equation", "variable", "algebra", "factor",
            "polynomial", "quadratic", "linear", "x =", "y ="
        ]
    
    def can_handle(self, problem: str) -> bool:
        """Check if this is an algebra problem"""
        problem_lower = problem.lower()
        return any(keyword in problem_lower for keyword in self.keywords)
    
    def solve(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve an algebra problem using LLM.
        
        Args:
            problem: The algebra problem
            context: Additional context from RAG or conversation
            
        Returns:
            Solution dictionary
        """
        prompt = self._prepare_prompt(problem, context)
        
        if self.llm_service:
            answer = self.llm_service.generate(prompt)
        else:
            answer = f"[Algebra Agent] Solution for: {problem}\n(LLM service not configured)"
        
        solution = {
            "solution_id": str(uuid.uuid4()),
            "question": problem,
            "answer": answer,
            "agent": self.name,
            "method_source": "LLM + Algebra Knowledge",
            "confidence": 0.88,
            "created_at": datetime.utcnow()
        }
        
        return solution
    
    def _prepare_prompt(self, problem: str, context: Dict[str, Any] = None) -> str:
        """Prepare prompt for LLM"""
        prompt = f"""You are an algebra expert. Solve the following algebra problem step by step.

Problem: {problem}
"""
        
        if context and context.get("rag_results"):
            prompt += f"\nRelevant context from textbooks:\n{context['rag_results']}\n"
        
        prompt += "\nProvide a detailed solution showing all algebraic steps."
        
        return prompt
