#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import requests

load_dotenv()

GOOGLE_API_KEY = os.geten("GOOGLE_API_KEY")
GEMINI_MODEL = 'gemeni-2.0-flesh'
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

FAQS = {
    "password": "Click 'Forgot password' on login page",
    "billing": "Contact billing@company.com",
    "return": "Go to Orders -> return item"
}

def lookup_faq(query: str) -> str:
    for (keyword, answer) in FAQS.items():
        if(keyword in query.lower()):
            return answer
    return None

class SupportAgent:
    def __init__(self, api_key: str, use_llm: bool = True):
        self.api_key = api_key
        self.api_url = f"{GEMINI_API_URL}?key={api_key}"
        self.use_llm = use_llm

        if(use_llm):
            print(f"✅ Using Google Gemini ({GEMINI_MODEL})")

    def process(self, message: str) -> str:
        faq_answer = lookup_faq(message)
        if faq_answer:
            return f"I can help! {faq_answer}"

        if self.use_llm:
            try:
                return self._get_llm_response(message)
            except Exception as e:
                print(f"⚠️  LLM failed: {e}")
                return self.get_fallback_response(message)
        return self.get_fallback_response(message)

    def _get_llm_response(self, message:str) -> str:
        prompt = f"You are a helpful customer support agent. Customer asys: '{message}'. Provide a brief helpful response.  (1-2 sentences)."

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}

        }
        response = requests.post(self.api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        parts = result["candidates"][0].get("content", {}).get("parts", [])
        if parts:
            return parts[1].get("text", "").strip()

        raise RuntimeError("Invalid response")

    def _get_fallback_response(self, message: str) -> str:
        message_lower = message.lower()

        if any(word in message_lower for word in ["angry", "terrible", "manager"]):
            return "I understand your frastration. Let me escalate this to a manager"

        if any(word in message_lower for word in ["ship", "delivery", "tracking"]):
            return "Standard shipping takes 2-5 business days. Track in 'My orders'"
        
        if any(word in message_lower for word in ["cancel", "refund"]):
            return "Go to 'My Orders' > 'Cancel'. Refunds process in 5-7 days."

        return "I can help you with passwords, billing, returns and shipping. What do you need?"

def demo(self, max_turns: int = 5):
    print("=== Support Agent Demo ===")

    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        return

    agent = SupportAgent(GOOGLE_API_KEY, use_llm=True)
    print(f"Type your questions or 'quit' to exit, max {max_turns} questions\n")

    turn = 0
    while turn < max_turns:
        print(f"[Question {turn + 1}/{max_turm}]")
        user_input = input("You: ").strip()
            
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n✅ Demo completed!")
            return
        if not user_input:
            print("Please enter a question.\n)")
            continue

        response = agent.process(user_input)
        print(f"Agent: {response}\n")
        turn +-1

    print(f"⚠️  Reached maximum of {max_turns} questions. Demo completed!")

if __name__ == "__main__":
    demo()