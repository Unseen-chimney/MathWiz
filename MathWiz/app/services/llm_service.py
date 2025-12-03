"""
LLM Service for interfacing with language models.
Supports multiple LLM providers (OpenAI, Anthropic, Google Gemini)
"""
import os
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        self.model_name = model_name
        
        # Determine API key based on model
        if not api_key:
            if "gemini" in model_name.lower():
                api_key = os.getenv("GEMINI_API_KEY")
            elif "claude" in model_name.lower():
                api_key = os.getenv("ANTHROPIC_API_KEY")
            else:
                api_key = os.getenv("OPENAI_API_KEY")
        
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client based on configuration"""
        try:
            if "gpt" in self.model_name.lower():
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            elif "claude" in self.model_name.lower():
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            elif "gemini" in self.model_name.lower():
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
        except ImportError:
            print(f"Warning: LLM client for {self.model_name} not installed")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: The prompt to send to LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response text
        """
        if not self.client:
            return self._mock_response(prompt)
        
        try:
            if "gpt" in self.model_name.lower():
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            
            elif "claude" in self.model_name.lower():
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif "gemini" in self.model_name.lower():
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
                response = self.client.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_response(prompt)
        
        return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """Mock response when LLM is not available"""
        return f"""[Mock LLM Response]
For the problem in the prompt, here's a sample solution:

Step 1: Analyze the problem
Step 2: Apply relevant mathematical principles
Step 3: Perform calculations
Step 4: Verify the answer

(Note: This is a mock response. Configure LLM API keys for actual solutions)
"""
    
    def create_llm_call_record(self, task_id: str, request: str, response: str, cost: float = 0.0) -> Dict[str, Any]:
        """Create LLM call record for tracking"""
        return {
            "llm_call_id": str(uuid.uuid4()),
            "task_id": task_id,
            "model_name": self.model_name,
            "request_payload": request,
            "response_payload": response,
            "cost_estimate": cost,
            "timestamp": datetime.utcnow()
        }
