"""
Test script for MathWiz system.
Run this to test the agents without starting the full API server.
"""
from app.services import Orchestrator, LLMService, RAGService


def main():
    """Test the MathWiz system with sample questions"""
    
    print("=" * 60)
    print("MathWiz - Agentic Math Problem Solving System")
    print("=" * 60)
    print()
    
    # Initialize services
    print("Initializing services...")
    llm_service = LLMService(model_name="gpt-4")
    rag_service = RAGService()
    orchestrator = Orchestrator(llm_service=llm_service, rag_service=rag_service)
    
    print("✓ Services initialized")
    print()
    
    # Test questions for different agents
    test_questions = [
        {
            "question": "Find the derivative of f(x) = x^3 + 2x^2 - 5x + 3",
            "expected_agent": "Calculus Agent"
        },
        {
            "question": "Solve the quadratic equation: 2x^2 + 5x - 3 = 0",
            "expected_agent": "Algebra Agent"
        },
        {
            "question": "What is the probability of rolling two dice and getting a sum of 7?",
            "expected_agent": "Statistics Agent"
        },
        {
            "question": "Calculate the area of a circle with radius 5 cm",
            "expected_agent": "General Math Agent"
        }
    ]
    
    # Process each question
    for i, test in enumerate(test_questions, 1):
        print(f"Question {i}:")
        print(f"  {test['question']}")
        print()
        
        # Process question
        result = orchestrator.process_question(
            question=test['question'],
            user_id="test_user",
            convo_id=f"test_convo_{i}"
        )
        
        print(f"  Agent Selected: {result['agent_used']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Answer Preview:")
        
        # Print first few lines of answer
        answer_lines = result['answer'].split('\n')[:5]
        for line in answer_lines:
            print(f"    {line}")
        
        if len(result['answer'].split('\n')) > 5:
            print("    ...")
        
        print()
        print("-" * 60)
        print()
    
    # Show agent capabilities
    print("\nAvailable Agents and Their Capabilities:")
    print("-" * 60)
    capabilities = orchestrator.get_agent_capabilities()
    
    for agent_name, caps in capabilities.items():
        print(f"\n{agent_name.upper()}:")
        for cap in caps:
            print(f"  • {cap}")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
