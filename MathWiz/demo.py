"""
Simple demo script showing how to use the MathWiz system programmatically.
"""
from app.services import Orchestrator, LLMService, RAGService


def demo():
    """Simple demonstration of the system"""
    
    # Initialize
    llm = LLMService()
    rag = RAGService()
    orchestrator = Orchestrator(llm, rag)
    
    # Ask a question
    question = "What is the integral of x^2?"
    
    print(f"Question: {question}\n")
    
    result = orchestrator.process_question(
        question=question,
        user_id="demo_user"
    )
    
    print(f"Agent: {result['agent_used']}")
    print(f"Answer:\n{result['answer']}")


if __name__ == "__main__":
    demo()
