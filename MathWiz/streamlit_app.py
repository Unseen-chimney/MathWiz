"""
Streamlit UI for MathWiz - Interactive Math Problem Solver
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services import Orchestrator, LLMService, RAGService, StateManager
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="MathWiz - AI Math Solver",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .thought-process {
        background-color: #fff3cd;
        padding: 1rem;
        border-left: 4px solid #ffc107;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .reflection {
        background-color: #d1ecf1;
        padding: 1rem;
        border-left: 4px solid #17a2b8;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'state_manager' not in st.session_state:
    st.session_state.state_manager = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
if 'current_convo_id' not in st.session_state:
    st.session_state.current_convo_id = None

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # LLM Selection
    llm_provider = st.selectbox(
        "Select LLM Provider",
        ["Gemini", "OpenAI", "Anthropic", "Mock (Testing)"],
        index=0
    )
    
    if llm_provider == "Gemini":
        model_options = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
        default_model = "gemini-2.5-flash"
    elif llm_provider == "OpenAI":
        model_options = ["gpt-4", "gpt-3.5-turbo"]
        default_model = "gpt-4"
    elif llm_provider == "Anthropic":
        model_options = ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
        default_model = "claude-3-opus-20240229"
    else:
        model_options = ["mock"]
        default_model = "mock"
    
    selected_model = st.selectbox("Model", model_options, index=0)
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.slider("Max Tokens", 500, 4000, 2000, 100)
        enable_reflection = st.checkbox("Enable Reflection", value=True)
        enable_chain_of_thought = st.checkbox("Enable Chain of Thought", value=True)
    
    # API Key input
    st.markdown("---")
    api_key = st.text_input(
        f"{llm_provider} API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY") if llm_provider == "Gemini" else "",
        help="Your API key is stored only for this session"
    )
    
    # Initialize button
    if st.button("🚀 Initialize System"):
        with st.spinner("Initializing MathWiz system..."):
            try:
                llm_service = LLMService(
                    model_name=selected_model if llm_provider != "Mock (Testing)" else "mock",
                    api_key=api_key if api_key else None
                )
                rag_service = RAGService()
                state_manager = StateManager()
                
                st.session_state.orchestrator = Orchestrator(
                    llm_service=llm_service,
                    rag_service=rag_service,
                    state_manager=state_manager
                )
                st.session_state.state_manager = state_manager
                
                # Create/get user in database
                state_manager.create_or_get_user(st.session_state.user_id)
                
                st.success("✅ System initialized successfully!")
                st.info(f"👤 User ID: {st.session_state.user_id}")
            except Exception as e:
                st.error(f"❌ Initialization failed: {e}")
    
    # Agent Info
    st.markdown("---")
    if st.session_state.orchestrator:
        st.markdown("### 🤖 Available Agents")
        capabilities = st.session_state.orchestrator.get_agent_capabilities()
        for agent_name, caps in capabilities.items():
            with st.expander(f"📊 {agent_name.title()}"):
                for cap in caps:
                    st.markdown(f"• {cap}")

# Main Content
st.markdown('<p class="main-header">🎓 MathWiz</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Multi-Agent Math Problem Solver</p>', unsafe_allow_html=True)

# Check if system is initialized
if not st.session_state.orchestrator:
    st.warning("⚠️ Please initialize the system using the sidebar configuration.")
    st.info("👈 Set your LLM provider and API key, then click 'Initialize System'")
    
    # Quick start demo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📐 Calculus Agent")
        st.markdown("Handles derivatives, integrals, limits")
    with col2:
        st.markdown("### 🔢 Algebra Agent")
        st.markdown("Solves equations, polynomials")
    with col3:
        st.markdown("### 📊 Statistics Agent")
        st.markdown("Probability, distributions")
else:
    # Main interaction area
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask a Question", "📚 Conversation History", "📊 Analytics", "🔄 State Management"])
    
    with tab1:
        # Question input
        question = st.text_area(
            "Enter your math question:",
            height=100,
            placeholder="Example: Find the derivative of x^2 + 3x - 5"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            solve_button = st.button("🧮 Solve Problem", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.conversation_history = []
            st.rerun()
        
        if solve_button and question:
            with st.spinner("🤔 Analyzing your question..."):
                try:
                    # Start or continue conversation
                    if not st.session_state.current_convo_id:
                        st.session_state.current_convo_id = f"convo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Process question with orchestrator (includes state saving)
                    result = st.session_state.orchestrator.process_question(
                        question=question,
                        user_id=st.session_state.user_id,
                        convo_id=st.session_state.current_convo_id,
                        use_context=True  # Use conversation history as context
                    )
                    
                    # Add to history
                    st.session_state.conversation_history.append({
                        'question': question,
                        'result': result,
                        'timestamp': datetime.now()
                    })
                    
                    # Display results
                    st.success("✅ Problem solved!")
                    
                    # Agent selection info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Agent Selected", result['agent_used'])
                    with col2:
                        st.metric("Confidence", f"{result['confidence']:.0%}")
                    with col3:
                        st.metric("Method", result['method_source'].split()[0])
                    
                    # Chain of Thought (if enabled)
                    if enable_chain_of_thought:
                        with st.expander("🧠 Chain of Thought Process", expanded=True):
                            st.markdown('<div class="thought-process">', unsafe_allow_html=True)
                            st.markdown("**Reasoning Steps:**")
                            st.markdown(f"""
                            1. **Question Classification**: Identified as {result['agent_used']} problem
                            2. **Context Retrieval**: Queried knowledge base for relevant information
                            3. **Problem Analysis**: Broke down the problem into solvable components
                            4. **Solution Generation**: Applied mathematical principles step-by-step
                            5. **Verification**: Checked answer validity and completeness
                            """)
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Answer
                    st.markdown("### 📝 Solution")
                    st.markdown(result['answer'])
                    
                    # Reflection (if enabled)
                    if enable_reflection and result.get('reflection'):
                        with st.expander("🔍 Reflection & Self-Evaluation", expanded=False):
                            st.markdown('<div class="reflection">', unsafe_allow_html=True)
                            reflection = result['reflection']
                            st.markdown(f"**Evaluation**: {reflection.get('evaluation', 'N/A')}")
                            st.markdown(f"**Suggestions**: {reflection.get('suggestion', 'N/A')}")
                            st.markdown(f"**Final Confidence**: {reflection.get('final_confidence', 0):.0%}")
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Task Log Details
                    with st.expander("📋 Task Log Details"):
                        st.json(result['task_log'])
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    with tab2:
        st.markdown("## 📚 Conversation History")
        
        if not st.session_state.conversation_history:
            st.info("No questions asked yet. Start by asking a math question in the 'Ask a Question' tab.")
        else:
            for idx, item in enumerate(reversed(st.session_state.conversation_history), 1):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**Q{len(st.session_state.conversation_history) - idx + 1}:** {item['question']}")
                    with col2:
                        st.caption(item['timestamp'].strftime("%H:%M:%S"))
                    
                    st.markdown(f"**Agent:** {item['result']['agent_used']} | **Confidence:** {item['result']['confidence']:.0%}")
                    
                    with st.expander("View Answer"):
                        st.markdown(item['result']['answer'])
                    
                    st.markdown("---")
    
    with tab3:
        st.markdown("## 📊 Analytics Dashboard")
        
        if not st.session_state.conversation_history:
            st.info("No data yet. Ask some questions to see analytics.")
        else:
            # Calculate statistics
            total_questions = len(st.session_state.conversation_history)
            agent_usage = {}
            avg_confidence = 0
            
            for item in st.session_state.conversation_history:
                agent = item['result']['agent_used']
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
                avg_confidence += item['result']['confidence']
            
            avg_confidence /= total_questions
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Questions", total_questions)
            with col2:
                st.metric("Average Confidence", f"{avg_confidence:.0%}")
            with col3:
                st.metric("Most Used Agent", max(agent_usage, key=agent_usage.get))
            
            # Agent usage chart
            st.markdown("### Agent Usage Distribution")
            st.bar_chart(agent_usage)
            
            # Recent activity
            st.markdown("### Recent Activity")
            for item in st.session_state.conversation_history[-5:]:
                st.markdown(f"• {item['timestamp'].strftime('%H:%M')} - {item['question'][:50]}... ({item['result']['agent_used']})")
    
    with tab4:
        st.markdown("## 🔄 State Management")
        
        if not st.session_state.state_manager:
            st.info("State manager not initialized. Please initialize the system first.")
        else:
            # Display current state
            st.markdown("### Current Session State")
            state_summary = st.session_state.state_manager.get_state_summary()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("User ID", state_summary.get('current_user_id', 'N/A'))
                st.metric("Current Conversation", state_summary.get('current_convo_id', 'None')[:20] + "..." if state_summary.get('current_convo_id') else 'None')
            with col2:
                st.metric("Messages in Context", state_summary.get('context_messages', 0))
                st.metric("Database", "SQLite" if "sqlite" in state_summary.get('database_url', '') else "Other")
            
            # Conversation controls
            st.markdown("---")
            st.markdown("### Conversation Controls")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🆕 Start New Conversation", use_container_width=True):
                    if st.session_state.state_manager:
                        # End current conversation
                        if st.session_state.current_convo_id:
                            st.session_state.state_manager.end_conversation(st.session_state.current_convo_id)
                        
                        # Start new one
                        new_convo_id = f"convo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        st.session_state.current_convo_id = new_convo_id
                        st.session_state.state_manager.start_conversation(
                            st.session_state.user_id, 
                            new_convo_id
                        )
                        st.success(f"✅ New conversation started: {new_convo_id[:20]}...")
                        st.rerun()
            
            with col2:
                if st.button("💾 Save Current State", use_container_width=True):
                    st.info("State is automatically saved to database after each interaction")
            
            with col3:
                if st.button("🔄 Reset Session", use_container_width=True):
                    st.session_state.conversation_history = []
                    st.session_state.current_convo_id = None
                    if st.session_state.state_manager:
                        st.session_state.state_manager.reset_state()
                    st.success("✅ Session reset!")
                    st.rerun()
            
            # Database history
            st.markdown("---")
            st.markdown("### Database History")
            
            try:
                # Get user's past conversations from database
                past_convos = st.session_state.state_manager.get_user_conversations(
                    st.session_state.user_id,
                    limit=10
                )
                
                if past_convos:
                    st.markdown(f"**Found {len(past_convos)} conversation(s) in database:**")
                    
                    for idx, conv in enumerate(past_convos, 1):
                        with st.expander(f"Conversation {idx} - {conv['started_at'].strftime('%Y-%m-%d %H:%M')}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("ID", conv['convo_id'][:20] + "...")
                            with col2:
                                st.metric("Messages", conv['message_count'])
                            with col3:
                                status = "Active" if not conv['ended_at'] else "Ended"
                                st.metric("Status", status)
                            
                            # Load conversation button
                            if st.button(f"📂 Load Conversation {idx}", key=f"load_{idx}"):
                                st.session_state.current_convo_id = conv['convo_id']
                                
                                # Get messages from this conversation
                                messages = st.session_state.state_manager.get_conversation_history(
                                    conv['convo_id'],
                                    limit=100
                                )
                                
                                st.success(f"✅ Loaded {len(messages)} messages from conversation")
                                st.json(messages)
                else:
                    st.info("No previous conversations found in database")
            
            except Exception as e:
                st.error(f"Error loading database history: {e}")
            
            # State visualization
            st.markdown("---")
            st.markdown("### State Details")
            
            with st.expander("📊 View Full State"):
                st.json({
                    "session_state_keys": list(st.session_state.keys()),
                    "state_manager_summary": state_summary,
                    "in_memory_history_count": len(st.session_state.conversation_history)
                })

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using Multi-Agent AI Architecture | Powered by Gemini & Streamlit</p>
</div>
""", unsafe_allow_html=True)
