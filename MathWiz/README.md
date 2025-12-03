# MathWiz - Agentic Math Problem Solving System

A sophisticated multi-agent system for solving mathematical problems using specialized AI agents and RAG (Retrieval-Augmented Generation) technology.

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for different math domains
  - Calculus Agent (derivatives, integrals, limits)
  - Algebra Agent (equations, polynomials, factoring)
  - Statistics Agent (probability, distributions, hypothesis testing)
  - General Math Agent (fallback for general problems)

- **RAG System**: Vector-based retrieval from PDF textbooks for enhanced context
- **LLM Integration**: Support for OpenAI GPT and Anthropic Claude models
- **Question Classification**: Automatic routing to appropriate specialist agents
- **Reflection & Feedback**: Self-evaluation and continuous improvement
- **RESTful API**: FastAPI-based backend for easy integration

## 📋 System Architecture

```
User Question → Orchestrator → [Question Classification]
                    ↓
        Select Appropriate Agent
                    ↓
        Query RAG for Context
                    ↓
        Agent Solves Problem (LLM)
                    ↓
        Reflection & Evaluation
                    ↓
        Return Solution to User
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or navigate to the project directory**:
```bash
cd /Users/praisewashere/Documents/MathWiz
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Configuration

Edit the `.env` file with your settings:

```env
# Required: Add at least one LLM API key
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=your-key-here

# Optional: Customize settings
DEFAULT_LLM_MODEL=gpt-4
VECTOR_DB_PATH=./chroma_db
```

### Running the Application

1. **Start the FastAPI server**:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the API**:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

## 📚 API Usage

### Ask a Math Question

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Find the derivative of x^2 + 3x + 5",
    "user_id": "user123"
  }'
```

Response:
```json
{
  "task_id": "abc-123",
  "convo_id": "xyz-789",
  "question": "Find the derivative of x^2 + 3x + 5",
  "answer": "The derivative is 2x + 3...",
  "agent_used": "Calculus Agent",
  "confidence": 0.95,
  "timestamp": "2025-12-02T10:30:00"
}
```

### Upload PDF for RAG

```bash
curl -X POST "http://localhost:8000/api/v1/pdf/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "/path/to/your/math_textbook.pdf"
  }'
```

### Get Available Agents

```bash
curl "http://localhost:8000/api/v1/agents"
```

## 🧪 Testing

### Interactive Testing

You can test the system interactively using Python:

```python
from app.services import Orchestrator, LLMService, RAGService

# Initialize services
llm_service = LLMService(model_name="gpt-4")
rag_service = RAGService()
orchestrator = Orchestrator(llm_service, rag_service)

# Ask a question
result = orchestrator.process_question(
    question="Solve the equation: 2x + 5 = 15",
    user_id="test_user"
)

print(result["answer"])
```

## 📊 Database Schema

The system uses SQLAlchemy ORM with the following models:
- User
- Conversation
- Message
- TaskLog
- SolutionRecord
- ReflectionLog
- PDFDocument
- PDFChunk
- Embedding
- Feedback
- LLMCall

## 🛠️ Project Structure

```
MathWiz/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── agents/                # Specialized math agents
│   │   ├── base_agent.py
│   │   ├── calculus_agent.py
│   │   ├── algebra_agent.py
│   │   ├── statistics_agent.py
│   │   └── general_math_agent.py
│   ├── models/                # Database models
│   │   └── database.py
│   ├── services/              # Business logic
│   │   ├── orchestrator.py   # Main coordinator
│   │   ├── llm_service.py    # LLM integration
│   │   ├── rag_service.py    # Vector search
│   │   └── pdf_processor.py  # PDF handling
│   └── api/                   # FastAPI routes
│       └── routes.py
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🔧 Advanced Configuration

### Using Different LLM Models

```python
from app.services import LLMService

# OpenAI GPT-4
llm = LLMService(model_name="gpt-4")

# Anthropic Claude
llm = LLMService(model_name="claude-3-opus-20240229")
```

### Customizing Agents

You can add new specialized agents by extending `BaseAgent`:

```python
from app.agents import BaseAgent

class GeometryAgent(BaseAgent):
    def __init__(self, llm_service):
        super().__init__("Geometry Agent", llm_service)
        self.capabilities = ["shapes", "angles", "area", "volume"]
    
    def can_handle(self, problem: str) -> bool:
        # Implement classification logic
        pass
    
    def solve(self, problem: str, context=None):
        # Implement solution logic
        pass
```

## 📝 Notes

- The system works with mock responses if no LLM API key is configured
- RAG functionality requires PDF files to be processed and indexed first
- Vector embeddings are stored in ChromaDB for fast semantic search
- All conversations and solutions are logged for analysis

## 🤝 Contributing

This is a prototype system. Feel free to extend it with:
- Additional specialized agents
- More sophisticated question classification
- Database persistence layer
- User authentication
- Web frontend
- More LLM providers

## 📄 License

This project is provided as-is for educational and development purposes.

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the logs for error messages
3. Ensure all dependencies are installed correctly
4. Verify your API keys are configured properly

---

Built with ❤️ using FastAPI, LangChain concepts, and Multi-Agent Architecture
