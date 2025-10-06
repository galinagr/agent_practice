#!/usr/bin/env python3
"""
Workflow Agent with Google Gemini
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

class WorkflowState:
    def __init__(self):
        self.data = {}

class WorkflowAgent:
    def __init__(self, api_key: str, use_llm: bool = True):
        self.api_key = api_key
        self.use_llm = use_llm
        
        if use_llm:
            self.api_url = f"{GEMINI_API_URL}?key={api_key}"
            print(f"✅ Using Google Gemini ({GEMINI_MODEL})")
    
    def validate_input(self, state: WorkflowState) -> WorkflowState:
        print("→ Validating input...")
        if len(state.data.get("message", "")) < 5:
            state.data["error"] = "Message too short"
        return state
    
    def categorize_request(self, state: WorkflowState) -> WorkflowState:
        print("→ Categorizing request...")
        message = state.data.get("message", "").lower()
        
        if "password" in message:
            state.data["category"] = "auth"
        elif "billing" in message:
            state.data["category"] = "billing"
        else:
            state.data["category"] = "general"
        
        return state
    
    def generate_response(self, state: WorkflowState) -> WorkflowState:
        print("→ Generating response...")
        
        if self.use_llm:
            try:
                message = state.data.get("message", "")
                category = state.data.get("category", "")
                
                prompt = f"Customer message: '{message}' (Category: {category}). Provide a brief, helpful support response (1-2 sentences)."
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}
                }
                
                response = requests.post(self.api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                parts = result["candidates"][0].get("content", {}).get("parts", [])
                if parts:
                    state.data["response"] = parts[0].get("text", "").strip()
                    return state
            except Exception as e:
                print(f"⚠️  LLM failed: {e}, using fallback")
        
        category = state.data.get("category")
        responses = {
            "auth": "Reset your password on the login page",
            "billing": "Contact billing@company.com",
            "general": "Thanks for contacting us"
        }
        state.data["response"] = responses.get(category, "We'll help you")
        
        return state
    
    def run_workflow(self, message: str) -> str:
        state = WorkflowState()
        state.data["message"] = message
        
        state = self.validate_input(state)
        state = self.categorize_request(state)
        state = self.generate_response(state)
        
        return state.data.get("response", "Error processing request")

def demo():
    print("=== Workflow Agent Demo ===\n")
    
    agent = WorkflowAgent(GOOGLE_API_KEY, use_llm=True)
    
    test_messages = [
        "I forgot my password",
        "Question about my bill",
        "Need help with my account"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"Message: {msg}")
        print('='*60)
        response = agent.run_workflow(msg)
        print(f"\nResponse: {response}\n")
    
    print("✅ Demo completed!")

if __name__ == "__main__":
    demo()