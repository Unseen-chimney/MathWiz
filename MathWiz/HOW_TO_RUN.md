# How to Run MathWiz

## 🎨 STREAMLIT UI (Recommended - Best Experience!)

The easiest way to use MathWiz with a beautiful web interface:

```bash
# 1. Navigate to project directory
cd /Users/praisewashere/Documents/MathWiz

# 2. Activate virtual environment
source venv/bin/activate

# 3. Set your API key (if using Gemini)
export GEMINI_API_KEY="AIzaSyBX3yVZ8tFuiBTdK2lYfFhDObXOB655Sv8"

# 4. Run Streamlit app
streamlit run streamlit_app.py
```

Then open your browser to: **http://localhost:8501**

### Features in the Streamlit UI:
- ✨ Beautiful interactive interface
- 🧠 Chain of thought visualization
- 🔍 Reflection and introspection details
- 📊 Analytics dashboard
- 💬 Conversation history
- ⚙️ Live configuration (switch LLMs, adjust settings)

---

## Quick Start (Demo Mode)

The quickest way to see the system in action:

```bash
# 1. Navigate to project directory
cd /Users/praisewashere/Documents/MathWiz

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run the quickstart demo
python quickstart.py
```

This will demonstrate the multi-agent system with mock LLM responses.

## Running the API Server

To start the full FastAPI server:

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## API Usage Examples

### Ask a Math Question

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the derivative of x^2 + 3x?",
    "user_id": "user123"
  }'
```

### Get Available Agents

```bash
curl "http://localhost:8000/api/v1/agents"
```

## Adding LLM Support (Optional)

For real LLM-powered answers instead of mock responses:

1. **Create `.env` file**:
```bash
cp .env.example .env
```

2. **Add your API key** to `.env`:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

3. **Install LLM package**:
```bash
pip install openai
# OR
pip install anthropic
```

4. **Restart the server**

## Adding RAG Support (Optional)

For document-based context retrieval:

```bash
# Install RAG dependencies
pip install chromadb sentence-transformers

# Upload a PDF
curl -X POST "http://localhost:8000/api/v1/pdf/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "/path/to/math_textbook.pdf"
  }'
```

## Project Structure

```
MathWiz/
├── app/
│   ├── agents/           # Specialized math agents
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   └── api/              # FastAPI routes
├── main.py              # Application entry point
├── quickstart.py        # Quick demo script
├── requirements.txt     # Dependencies
├── .env.example         # Configuration template
└── README.md            # Full documentation
```

## Testing Individual Components

```python
# Test a specific agent
from app.agents import CalculusAgent
from app.services import LLMService

llm = LLMService()
agent = CalculusAgent(llm)

result = agent.solve("Find derivative of x^2")
print(result['answer'])
```

## Troubleshooting

**No LLM responses**: System uses mock responses when no API key is configured. This is normal for testing.

**Import errors**: Make sure virtual environment is activated:
```bash
source venv/bin/activate
```

**Port already in use**: Change the port:
```bash
python main.py --port 8001
```

## System Overview

The MathWiz system:
1. Receives a math question from the user
2. Classifies the question type (Calculus, Algebra, Statistics, General)
3. Routes to the appropriate specialized agent
4. Queries RAG system for relevant textbook context (if available)
5. Agent solves using LLM + domain knowledge
6. Returns solution with confidence score and reflection

All interactions are logged to support feedback and continuous improvement.
