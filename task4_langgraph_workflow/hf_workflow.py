#!/usr/bin/env python3
"""
LangGraph Workflow with Google Gemini
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

class WorkflowState:
    def __init__(self, message: str):
        self.message: str = message
        self.category: str | None = None
        self.priority: str | None = None
        self.response: str | None = None
        self.escalated: bool = False

class GeminiWorkflow:
    def __init__(self, api_key: str, use_llm: bool = True):
        self.api_key = api_key
        self.use_llm = use_llm
        
        if use_llm:
            self.api_url = f"{GEMINI_API_URL}?key={api_key}"
            print(f"✅ Using Google Gemini ({GEMINI_MODEL})")
    
    def categorize(self, state: WorkflowState) -> WorkflowState:
        print("→ Categorizing request...")
        message_lower = state.message.lower()
        
        if any(word in message_lower for word in ["password", "login", "auth"]):
            state.category = "authentication"
        elif any(word in message_lower for word in ["bill", "payment", "charge"]):
            state.category = "billing"
        elif any(word in message_lower for word in ["bug", "error", "broken"]):
            state.category = "technical"
        else:
            state.category = "general"
        
        print(f"   Category: {state.category}")
        return state
    
    def set_priority(self, state: WorkflowState) -> WorkflowState:
        print("→ Setting priority...")
        message_lower = state.message.lower()
        
        if any(word in message_lower for word in ["urgent", "asap", "critical"]):
            state.priority = "high"
        elif state.category in ["billing", "technical"]:
            state.priority = "medium"
        else:
            state.priority = "low"
        
        print(f"   Priority: {state.priority}")
        return state
    
    def generate_response(self, state: WorkflowState) -> WorkflowState:
        print("→ Generating response...")
        
        if self.use_llm:
            try:
                state.response = self._get_llm_response(state)
                print("   ✅ LLM response generated")
                return state
            except Exception as e:
                print(f"   ⚠️  LLM failed: {e}, using fallback")
        
        state.response = self._get_fallback_response(state)
        print("   ✅ Fallback response generated")
        return state
    
    def check_escalation(self, state: WorkflowState) -> WorkflowState:
        print("→ Checking escalation...")
        message_lower = state.message.lower()
        
        if any(word in message_lower for word in ["angry", "frustrated", "manager"]):
            state.escalated = True
            if state.response:
                state.response += "\n\nI'm escalating this to a senior agent who will contact you shortly."
            print("   ⚠️  Escalated to human agent")
        else:
            print("   ✅ No escalation needed")
        
        return state
    
    def _get_llm_response(self, state: WorkflowState) -> str:
        prompt = f"You are a helpful support agent. Customer message: '{state.message}' (Category: {state.category}, Priority: {state.priority}). Provide a brief, helpful response (1-2 sentences)."
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}
        }
        
        response = requests.post(self.api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        parts = result["candidates"][0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "").strip()
        
        raise RuntimeError("Invalid response")
    
    def _get_fallback_response(self, state: WorkflowState) -> str:
        responses: dict[str, str] = {
            "authentication": "To reset your password, click 'Forgot Password' on the login page.",
            "billing": "For billing questions, contact billing@company.com or check your account settings.",
            "technical": "Please describe the issue in detail and we'll investigate. You can also check our troubleshooting guide.",
            "general": "Thanks for contacting us. How can we help you today?"
        }
        return responses.get(state.category or "", "We're here to help!")
    
    def run(self, message: str) -> WorkflowState:
        state = WorkflowState(message)
        
        state = self.categorize(state)
        state = self.set_priority(state)
        state = self.generate_response(state)
        state = self.check_escalation(state)
        
        return state

def demo():
    print("=== LangGraph-style Workflow Demo ===\n")
    
    workflow = GeminiWorkflow(GOOGLE_API_KEY, use_llm=True)
    
    test_messages = [
        "I forgot my password and need help urgently",
        "Why was I charged twice on my bill?",
        "The app keeps crashing, this is terrible!"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"Message: {msg}")
        print('='*60)
        
        result = workflow.run(msg)
        
        print(f"\n📊 Results:")
        print(f"   Category: {result.category}")
        print(f"   Priority: {result.priority}")
        print(f"   Escalated: {result.escalated}")
        print(f"   Response: {result.response}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    demo()