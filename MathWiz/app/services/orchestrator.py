"""
Orchestrator - Coordinates the multi-agent system workflow.
Classifies questions and delegates to appropriate agents.
"""
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
from ..agents import CalculusAgent, AlgebraAgent, GeneralMathAgent, StatisticsAgent


class Orchestrator:
    """Main orchestrator for the agentic math system"""
    
    def __init__(self, llm_service=None, rag_service=None, state_manager=None):
        self.llm_service = llm_service
        self.rag_service = rag_service
        self.state_manager = state_manager
        
        # Initialize specialized agents
        self.agents = {
            "calculus": CalculusAgent(llm_service),
            "algebra": AlgebraAgent(llm_service),
            "statistics": StatisticsAgent(llm_service),
            "general": GeneralMathAgent(llm_service)
        }
    
    def process_question(self, question: str, user_id: str, convo_id: str = None, use_context: bool = True) -> Dict[str, Any]:
        """
        Main workflow for processing a math question with state management.
        
        Args:
            question: The math question from user
            user_id: User ID
            convo_id: Conversation ID (creates new if not provided)
            use_context: Whether to include conversation context
            
        Returns:
            Complete response with solution, agent info, and metadata
        """
        convo_id = convo_id or str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        
        # Initialize state if state manager is available
        if self.state_manager:
            self.state_manager.create_or_get_user(user_id)
            self.state_manager.start_conversation(user_id, convo_id)
            # Save user message
            self.state_manager.save_message(convo_id, 'user', question)
        
        # Step 1: Classify question and select agent
        selected_agent = self._classify_and_select_agent(question)
        
        # Step 2: Query RAG for relevant context (if available)
        context = self._get_context_from_rag(question)
        
        # Step 2.5: Add conversation context if enabled
        if use_context and self.state_manager:
            conversation_context = self.state_manager.get_conversation_context(convo_id, last_n=3)
            if context:
                context['conversation_history'] = conversation_context
            else:
                context = {'conversation_history': conversation_context}
        
        # Step 3: Agent solves the problem with chain of thought
        solution = selected_agent.solve(question, context)
        
        # Step 4: Enhanced reflection and introspection
        reflection = selected_agent.reflect(solution, question)
        
        # Step 5: Create task log
        task_log = self._create_task_log(
            task_id=task_id,
            convo_id=convo_id,
            agent_name=selected_agent.name,
            status="completed",
            confidence=solution.get("confidence", 0.5)
        )
        
        # Prepare final response
        response = {
            "task_id": task_id,
            "convo_id": convo_id,
            "user_id": user_id,
            "question": question,
            "answer": solution.get("answer"),
            "agent_used": selected_agent.name,
            "confidence": solution.get("confidence"),
            "method_source": solution.get("method_source"),
            "reflection": reflection,
            "task_log": task_log,
            "solution_record": solution,
            "timestamp": datetime.utcnow()
        }
        
        # Save to database if state manager is available
        if self.state_manager:
            # Save agent response
            self.state_manager.save_message(convo_id, 'agent', solution.get("answer", ""))
            # Save task result
            self.state_manager.save_task_result(response)
        
        return response
    
    def _classify_and_select_agent(self, question: str) -> Any:
        """
        Classify the question and select appropriate agent.
        Uses keyword matching and agent capabilities.
        
        Args:
            question: The math question
            
        Returns:
            Selected agent instance
        """
        # Try each specialized agent in order
        for agent_name, agent in self.agents.items():
            if agent_name == "general":
                continue  # Save general agent as fallback
            
            if agent.can_handle(question):
                print(f"Selected agent: {agent.name}")
                return agent
        
        # Fallback to general math agent
        print(f"Selected agent: {self.agents['general'].name} (fallback)")
        return self.agents["general"]
    
    def _get_context_from_rag(self, question: str) -> Dict[str, Any]:
        """Query RAG service for relevant context"""
        if not self.rag_service:
            return {"rag_results": None}
        
        try:
            results = self.rag_service.query_relevant_context(question, n_results=3)
            formatted_context = self.rag_service.format_context_for_prompt(results)
            
            return {
                "rag_results": formatted_context,
                "rag_chunks": results
            }
        except Exception as e:
            print(f"Error querying RAG: {e}")
            return {"rag_results": None}
    
    def _create_task_log(self, task_id: str, convo_id: str, agent_name: str, 
                         status: str, confidence: float) -> Dict[str, Any]:
        """Create task log entry"""
        return {
            "task_id": task_id,
            "convo_id": convo_id,
            "agent_name": agent_name,
            "tool_used": "LLM + RAG",
            "task_type": "math_problem_solving",
            "status": status,
            "confidence": confidence,
            "created_at": datetime.utcnow()
        }
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all agents"""
        return {
            name: agent.get_capabilities() 
            for name, agent in self.agents.items()
        }
