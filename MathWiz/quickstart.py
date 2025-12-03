"""
Quick Start Demo - Run this to test the MathWiz system without LLM APIs.
This uses mock responses to demonstrate the multi-agent architecture.
"""
import sys
sys.path.insert(0, '/Users/praisewashere/Documents/MathWiz')

from app.services.orchestrator import Orchestrator
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService


def print_separator():
    print("\n" + "=" * 70 + "\n")


def main():
    print_separator()
    print("🎓 MathWiz - Agentic Math Problem Solving System")
    print("   Demo Mode (Mock LLM Responses)")
    print_separator()
    
    # Initialize services (without API keys - will use mock responses)
    print("Initializing services...")
    llm_service = LLMService(model_name="gpt-4")  # Uses mock if no API key
    rag_service = RAGService()  # Uses mock if chromadb not installed
    orchestrator = Orchestrator(llm_service=llm_service, rag_service=rag_service)
    print("✅ Services initialized successfully")
    print_separator()
    
    # Test questions that trigger different agents
    test_cases = [
        {
            "question": "Find the derivative of f(x) = x^3 + 2x^2 - 5x + 3",
            "description": "Calculus Problem - Testing Calculus Agent"
        },
        {
            "question": "Solve the quadratic equation: 2x^2 + 5x - 3 = 0",
            "description": "Algebra Problem - Testing Algebra Agent"
        },
        {
            "question": "What is the probability of rolling a sum of 7 with two dice?",
            "description": "Statistics Problem - Testing Statistics Agent"
        },
        {
            "question": "Calculate the area of a circle with radius 5 cm",
            "description": "General Math Problem - Testing General Math Agent"
        }
    ]
    
    # Process each test case
    for i, test in enumerate(test_cases, 1):
        print(f"Test Case #{i}: {test['description']}")
        print(f"Question: {test['question']}")
        print()
        
        # Process the question through the orchestrator
        result = orchestrator.process_question(
            question=test['question'],
            user_id="demo_user",
            convo_id=f"demo_convo_{i}"
        )
        
        # Display results
        print(f"✓ Agent Selected: {result['agent_used']}")
        print(f"✓ Confidence Score: {result['confidence']:.2%}")
        print(f"✓ Method: {result['method_source']}")
        print()
        print("Answer Preview:")
        print("-" * 70)
        
        # Show first few lines of the answer
        answer_lines = result['answer'].split('\n')
        for j, line in enumerate(answer_lines[:6], 1):
            if line.strip():
                print(f"  {line}")
        
        if len(answer_lines) > 6:
            print("  [...answer continues...]")
        
        print("-" * 70)
        print_separator()
    
    # Show agent capabilities
    print("📊 Available Agents and Their Capabilities:")
    print_separator()
    
    capabilities = orchestrator.get_agent_capabilities()
    for agent_name, caps in capabilities.items():
        print(f"🤖 {agent_name.upper()}:")
        for cap in caps:
            print(f"   • {cap}")
        print()
    
    print_separator()
    print("✅ Demo completed successfully!")
    print()
    print("Next Steps:")
    print("  1. Add your LLM API key to .env file for real responses")
    print("  2. Run: python main.py  (to start the API server)")
    print("  3. Visit: http://localhost:8000/docs  (for interactive API)")
    print_separator()


if __name__ == "__main__":
    main()
