"""
Statistics Agent - Specialized in statistics and probability problems.
"""
from typing import Dict, Any
import uuid
from datetime import datetime
from .base_agent import BaseAgent


class StatisticsAgent(BaseAgent):
    """Agent specialized in statistics and probability"""
    
    def __init__(self, llm_service=None):
        super().__init__("Statistics Agent", llm_service)
        self.capabilities = [
            "probability",
            "statistics",
            "data analysis",
            "distributions",
            "hypothesis testing"
        ]
        self.keywords = [
            "probability", "statistics", "mean", "median", "mode",
            "variance", "standard deviation", "distribution", "sample",
            "hypothesis", "confidence interval", "correlation"
        ]
    
    def can_handle(self, problem: str) -> bool:
        """Check if this is a statistics problem"""
        problem_lower = problem.lower()
        return any(keyword in problem_lower for keyword in self.keywords)
    
    def solve(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve a statistics problem using LLM.
        
        Args:
            problem: The statistics problem
            context: Additional context from RAG or conversation
            
        Returns:
            Solution dictionary
        """
        prompt = self._prepare_prompt(problem, context)
        
        if self.llm_service:
            answer = self.llm_service.generate(prompt)
        else:
            answer = f"[Statistics Agent] Solution for: {problem}\n(LLM service not configured)"
        
        solution = {
            "solution_id": str(uuid.uuid4()),
            "question": problem,
            "answer": answer,
            "agent": self.name,
            "method_source": "LLM + Statistics Knowledge",
            "confidence": 0.86,
            "created_at": datetime.utcnow()
        }
        
        return solution
    
    def _prepare_prompt(self, problem: str, context: Dict[str, Any] = None) -> str:
        """Prepare prompt for LLM"""
        prompt = f"""You are a statistics and probability expert. Solve the following problem step by step.

Problem: {problem}
"""
        
        if context and context.get("rag_results"):
            prompt += f"\nRelevant context from textbooks:\n{context['rag_results']}\n"
        
        prompt += "\nProvide a detailed solution with statistical reasoning and calculations."
        
        return prompt
