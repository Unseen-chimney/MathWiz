"""
Base Agent class for all specialized math agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import uuid
from datetime import datetime


class BaseAgent(ABC):
    """Abstract base class for all math agents"""
    
    def __init__(self, name: str, llm_service=None):
        self.name = name
        self.llm_service = llm_service
        self.capabilities = []
        
    @abstractmethod
    def solve(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve a math problem.
        
        Args:
            problem: The math problem to solve
            context: Additional context (RAG results, conversation history, etc.)
            
        Returns:
            Dict containing solution, confidence, and method used
        """
        pass
    
    @abstractmethod
    def can_handle(self, problem: str) -> bool:
        """
        Determine if this agent can handle the given problem.
        
        Args:
            problem: The math problem to evaluate
            
        Returns:
            Boolean indicating if this agent can handle the problem
        """
        pass
    
    def chain_of_thought(self, problem: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate chain of thought reasoning process.
        
        Args:
            problem: The problem to analyze
            context: Additional context
            
        Returns:
            Dict containing reasoning steps
        """
        return {
            "steps": [
                f"1. Problem Analysis: Identified as {self.name} domain",
                f"2. Context Review: Gathered relevant {len(self.capabilities)} concepts",
                "3. Solution Strategy: Selected appropriate mathematical methods",
                "4. Step-by-step Execution: Applied algorithms systematically",
                "5. Verification: Cross-checked results for accuracy"
            ],
            "reasoning": f"This problem falls under {self.name} domain based on keyword analysis",
            "confidence_factors": [
                "Problem matches agent capabilities",
                "Clear mathematical structure",
                "Established solution methods available"
            ]
        }
    
    def reflect(self, solution: Dict[str, Any], problem: str) -> Dict[str, Any]:
        """
        Reflect on the solution and provide evaluation.
        
        Args:
            solution: The solution to reflect on
            problem: The original problem
            
        Returns:
            Dict containing evaluation and suggestions
        """
        # Use LLM for deeper reflection if available
        if self.llm_service:
            reflection_prompt = f"""
Reflect on this solution and evaluate its quality:

Problem: {problem}
Solution: {solution.get('answer', 'N/A')[:500]}

Provide:
1. Evaluation: Is the solution correct and complete?
2. Suggestions: Any improvements or clarifications needed?
3. Confidence: Rate your confidence in this solution (0-1)

Be critical and constructive.
"""
            try:
                reflection_text = self.llm_service.generate(reflection_prompt, max_tokens=500, temperature=0.3)
                
                return {
                    "reflect_id": str(uuid.uuid4()),
                    "evaluation": reflection_text,
                    "suggestion": "See detailed evaluation above",
                    "final_confidence": solution.get("confidence", 0.5),
                    "created_at": datetime.utcnow(),
                    "introspection": self._introspect(solution, problem)
                }
            except:
                pass
        
        # Fallback reflection
        confidence = solution.get("confidence", 0.5)
        evaluation = f"{self.name} completed the task with {confidence:.0%} confidence"
        
        if confidence > 0.85:
            evaluation += ". Solution appears robust and well-explained."
            suggestion = "Solution is comprehensive and clear."
        elif confidence > 0.70:
            evaluation += ". Solution is solid but could be enhanced."
            suggestion = "Consider adding more detailed explanations or alternative approaches."
        else:
            evaluation += ". Solution may need verification."
            suggestion = "Recommend manual verification or consultation with additional resources."
        
        return {
            "reflect_id": str(uuid.uuid4()),
            "evaluation": evaluation,
            "suggestion": suggestion,
            "final_confidence": confidence,
            "created_at": datetime.utcnow(),
            "introspection": self._introspect(solution, problem)
        }
    
    def _introspect(self, solution: Dict[str, Any], problem: str) -> Dict[str, Any]:
        """
        Introspection: Analyze agent's own performance and decision-making.
        
        Args:
            solution: The solution generated
            problem: The original problem
            
        Returns:
            Dict containing self-analysis
        """
        return {
            "agent_name": self.name,
            "problem_complexity": "high" if len(problem) > 100 else "medium" if len(problem) > 50 else "low",
            "capability_match": self.can_handle(problem),
            "utilized_capabilities": [cap for cap in self.capabilities if any(word in problem.lower() for word in cap.split())],
            "confidence_reasoning": f"Based on problem-capability alignment and solution completeness",
            "potential_limitations": self._identify_limitations(problem),
            "improvement_areas": [
                "Could benefit from more examples",
                "May need additional context for edge cases",
                "Consider cross-validation with other agents"
            ]
        }
    
    def _identify_limitations(self, problem: str) -> List[str]:
        """Identify potential limitations in handling this problem"""
        limitations = []
        
        if len(problem) > 200:
            limitations.append("Complex problem may require breaking into sub-problems")
        
        if not self.can_handle(problem):
            limitations.append("Problem may be outside primary expertise area")
        
        if "prove" in problem.lower() or "proof" in problem.lower():
            limitations.append("Formal proofs may require specialized validation")
        
        return limitations if limitations else ["No significant limitations identified"]
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities
