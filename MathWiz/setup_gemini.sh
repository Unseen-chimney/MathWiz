#!/bin/bash
# Quick setup script for using Gemini API with MathWiz

echo "🎓 Setting up MathWiz with Gemini API..."
echo ""

# Install Google Generative AI package
echo "📦 Installing google-generativeai package..."
pip install google-generativeai

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure your .env file has: GEMINI_API_KEY=your_key_here"
echo "2. Use model names like: 'gemini-pro' or 'gemini-1.5-flash'"
echo ""
echo "🚀 Example usage:"
echo ""
echo "from app.services import LLMService"
echo "llm = LLMService(model_name='gemini-pro')"
echo "result = llm.generate('What is 2+2?')"
echo ""
