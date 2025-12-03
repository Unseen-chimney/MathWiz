"""
Test Gemini API integration with MathWiz
"""
import os
import sys
sys.path.insert(0, '/Users/praisewashere/Documents/MathWiz')

from app.services.llm_service import LLMService
from app.services.orchestrator import Orchestrator


def test_gemini():
    print("🧪 Testing Gemini API Integration\n")
    print("=" * 60)
    
    # Get API key from environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("\nTo set it up:")
        print("1. Create a .env file (copy from .env.example)")
        print("2. Add: GEMINI_API_KEY=your_actual_key")
        print("3. Run: source venv/bin/activate")
        return
    
    print(f"✅ Found Gemini API key: {gemini_key[:20]}...")
    print("\n" + "=" * 60)
    
    # Test LLM Service directly
    print("\n1. Testing LLM Service with Gemini 2.5 Flash")
    print("-" * 60)
    
    llm = LLMService(model_name="gemini-2.5-flash")
    
    test_prompt = "Solve this simple math problem: What is 15 + 27?"
    print(f"Prompt: {test_prompt}\n")
    
    try:
        response = llm.generate(test_prompt, max_tokens=500, temperature=0.3)
        print("Response:")
        print(response)
        print("\n✅ Gemini API is working!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test with Orchestrator
    print("\n" + "=" * 60)
    print("2. Testing Full System with Gemini")
    print("-" * 60)
    
    orchestrator = Orchestrator(llm_service=llm, rag_service=None)
    
    test_question = "Find the derivative of x^2 + 3x - 5"
    print(f"Question: {test_question}\n")
    
    try:
        result = orchestrator.process_question(
            question=test_question,
            user_id="test_user",
            convo_id="test_gemini"
        )
        
        print(f"Agent Selected: {result['agent_used']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"\nAnswer:\n{result['answer']}")
        print("\n✅ Full system test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Gemini integration test complete!")


if __name__ == "__main__":
    test_gemini()
