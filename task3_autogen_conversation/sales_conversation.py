#!/usr/bin/env python3
"""
AutoGen Sales Conversation with Google Gemini
"""

import os
import requests
import autogen
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

def call_gemini(prompt: str) -> str:
    """Call Google Gemini API"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}
    }
    
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GOOGLE_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        parts = result["candidates"][0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "").strip()
    except Exception as e:
        print(f"⚠️  Gemini API failed: {e}")
    
    return "I'm here to help! What can I assist you with?"

class GeminiAgent(autogen.ConversableAgent):
    """Custom AutoGen agent using Google Gemini"""
    
    def generate_reply(self, messages=None, sender=None, **kwargs):
        if not messages:
            return None
        
        last_message = messages[-1].get("content", "")
        
        prompt = f"You are Sarah, a friendly sales specialist. Customer says: '{last_message}'. Respond briefly (1-2 sentences) and ask a relevant question."
        
        response = call_gemini(prompt)
        return response

def demo():
    print("=== AutoGen Sales Conversation ===\n")
    print(f"✅ Using AutoGen with Google Gemini ({GEMINI_MODEL})\n")
    
    sales_agent = GeminiAgent(
        name="SalesAgent",
        system_message="You are Sarah, a friendly sales specialist.",
        human_input_mode="NEVER"
    )
    
    customer = autogen.UserProxyAgent(
        name="Customer",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=0,
        code_execution_config=False
    )
    
    print("Sales Agent: Hi! I'm Sarah, a sales specialist. What brings you here today?\n")
    
    try:
        customer.initiate_chat(
            sales_agent,
            message="I'm interested in your product",
            max_turns=3
        )
    except KeyboardInterrupt:
        print("\n\nConversation ended.")
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        print("Conversation ended.")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    print("""
=== AutoGen Sales Conversation ===

📦 Installation:
   pip install pyautogen requests

    """)
    
    demo()