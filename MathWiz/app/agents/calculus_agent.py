"""
Calculus Agent - Specialized in calculus problems.
"""
from typing import Dict, Any
import uuid
from datetime import datetime
from .base_agent import BaseAgent


class CalculusAgent(BaseAgent):
    """Agent specialized in calculus problems"""
    
    def __init__(self, llm_service=None):
        super().__init__("Calculus Agent", llm_service)
        self.capabilities = [
            "derivatives",
            "integrals",
            "limits",
            "differential equations",
            "multivariable calculus"
        ]
        self.keywords = [
            "derivative", "integral", "limit", "differentiate", "integrate",
            "dx", "dy", "calculus", "rate of change", "area under curve"
        ]
    
    def can_handle(self, problem: str) -> bool:
        """Check if this is a calculus problem"""
        problem_lower = problem.lower()
        return any(keyword in problem_lower for keyword in self.keywords)
    
    def solve(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve a calculus problem using LLM with chain of thought.
        
        Args:
            problem: The calculus problem
            context: Additional context from RAG or conversation
            
        Returns:
            Solution dictionary
        """
        # Generate chain of thought
        cot = self.chain_of_thought(problem, context)
        
        # Prepare prompt with chain of thought reasoning
        prompt = self._prepare_prompt_with_cot(problem, context, cot)
        
        # Use LLM to solve
        if self.llm_service:
            answer = self.llm_service.generate(prompt, max_tokens=2000, temperature=0.3)
        else:
            answer = f"[Calculus Agent] Solution for: {problem}\n(LLM service not configured)"
        
        solution = {
            "solution_id": str(uuid.uuid4()),
            "question": problem,
            "answer": answer,
            "agent": self.name,
            "method_source": "LLM + Calculus Knowledge",
            "confidence": 0.85,
            "created_at": datetime.utcnow(),
            "chain_of_thought": cot
        }
        
        return solution
    
    def _prepare_prompt_with_cot(self, problem: str, context: Dict[str, Any] = None, cot: Dict[str, Any] = None) -> str:
        """Prepare prompt with chain of thought reasoning"""
        prompt = f"""You are an expert calculus tutor. Solve this problem step by step with clear reasoning.

Problem: {problem}

Use chain of thought reasoning:
1. Analyze what type of calculus problem this is
2. Identify the relevant theorems and methods
3. Show each step of the solution clearly
4. Explain your reasoning at each step
5. Verify your answer makes sense
"""
        
        if context and context.get("rag_results"):
            prompt += f"\n\nRelevant context from textbooks:\n{context['rag_results']}\n"
        
        prompt += "\n\nProvide a detailed, step-by-step solution with explanations for each step."
        
        return prompt
    
    def _prepare_prompt(self, problem: str, context: Dict[str, Any] = None) -> str:
        """Prepare prompt for LLM"""
        prompt = f"""You are a calculus expert. Solve the following calculus problem step by step.

Problem: {problem}
"""
        
        if context and context.get("rag_results"):
            prompt += f"\nRelevant context from textbooks:\n{context['rag_results']}\n"
        
        prompt += "\nProvide a detailed solution with clear steps."
        
        return prompt
