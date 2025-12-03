"""
Demo: State Management in MathWiz
Shows how conversation state is persisted and retrieved
"""
import sys
sys.path.insert(0, '/Users/praisewashere/Documents/MathWiz')

from app.services import Orchestrator, LLMService, RAGService, StateManager
from datetime import datetime
import time


def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    print_section("🔄 MathWiz State Management Demo")
    
    # Initialize services with state manager
    print("Initializing services with state management...")
    llm_service = LLMService(model_name="gemini-2.5-flash")
    rag_service = RAGService()
    state_manager = StateManager()  # Creates/connects to mathwiz.db
    
    orchestrator = Orchestrator(
        llm_service=llm_service,
        rag_service=rag_service,
        state_manager=state_manager
    )
    
    print("✅ Services initialized with state persistence")
    
    # Create a user
    print_section("👤 Creating User")
    user_id = f"demo_user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    state_manager.create_or_get_user(user_id, name="Demo User")
    print(f"Created user: {user_id}")
    
    # Start a conversation
    print_section("💬 Starting Conversation")
    convo_id = f"convo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    conversation = state_manager.start_conversation(user_id, convo_id)
    print(f"Started conversation: {convo_id}")
    
    # Ask multiple questions to build context
    questions = [
        "What is 15 + 27?",
        "Now multiply that result by 3",
        "What's the derivative of x^2?"
    ]
    
    print_section("🤔 Asking Questions with Context")
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question}")
        print("-" * 70)
        
        # Process with context from previous messages
        result = orchestrator.process_question(
            question=question,
            user_id=user_id,
            convo_id=convo_id,
            use_context=True  # This uses conversation history
        )
        
        print(f"Agent: {result['agent_used']}")
        print(f"Answer Preview: {result['answer'][:150]}...")
        
        # Messages are automatically saved to database
        print(f"✅ Saved to database (task_id: {result['task_id'][:20]}...)")
        
        time.sleep(1)  # Brief pause between questions
    
    # Retrieve conversation history from database
    print_section("📚 Retrieving Conversation History from Database")
    
    history = state_manager.get_conversation_history(convo_id, limit=10)
    print(f"Found {len(history)} messages in database:")
    
    for msg in history:
        sender = msg['sender'].upper()
        content_preview = msg['content'][:80]
        timestamp = msg['timestamp'].strftime('%H:%M:%S')
        print(f"\n[{timestamp}] {sender}: {content_preview}...")
    
    # Get formatted context for LLM
    print_section("🧠 Formatted Context for LLM")
    context_text = state_manager.get_conversation_context(convo_id, last_n=3)
    print(context_text)
    
    # End conversation
    print_section("🏁 Ending Conversation")
    state_manager.end_conversation(convo_id)
    print(f"Conversation {convo_id} ended and saved to database")
    
    # Show all conversations for this user
    print_section("📊 User's All Conversations")
    all_convos = state_manager.get_user_conversations(user_id, limit=5)
    
    print(f"User {user_id} has {len(all_convos)} conversation(s):")
    for conv in all_convos:
        status = "Active" if not conv['ended_at'] else "Ended"
        print(f"\n• {conv['convo_id'][:30]}...")
        print(f"  Started: {conv['started_at']}")
        print(f"  Status: {status}")
        print(f"  Messages: {conv['message_count']}")
    
    # Show state summary
    print_section("📈 State Summary")
    summary = state_manager.get_state_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print_section("✅ Demo Complete!")
    print("""
State Management Features Demonstrated:
✅ User creation and persistence
✅ Conversation tracking
✅ Message history storage
✅ Automatic state saving
✅ Context retrieval for LLM
✅ Multi-conversation support
✅ Database persistence (SQLite)

All data is saved in: mathwiz.db
You can inspect it with any SQLite browser!
""")


if __name__ == "__main__":
    main()
