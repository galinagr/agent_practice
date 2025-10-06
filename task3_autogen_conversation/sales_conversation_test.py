#!/usr/bin/env python3

import os, requests, autogen
from sys import last_exc
from dotenv import load_dotenv


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flesh"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models{GEMINI_MODEL}:generateContent"

def call_gemini(prompt: str) -> str:
    """Call Google Gemini API"""

    payload = {
        "contents": [
            {"parts": [{
                "text": prompt

        }]}],
        "generationConfig": {
            "temperature": 0.7, 
            "maxOutputTokens": 150
        }
    }
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GOOGLE_API_KEY}",
            headers={"Content-Type": "appliation/json"},
            json=payload,
            timeout=30
        )
        response.saise_for_status()
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

    prompt = f"You are Sarah, a friedly sales specialist. Customer says: '{last_message}"
    response = call_gemini(prompt)
    return response

def demo():
    print(f"=== AutoGen used for Sales Conversation ===")
    print(f"✅ Using Google Gemini ({GEMINI_MODEL})\n")


    sales_agent = GeminiAgent(
        name="SalesAgent",
        system_message="You are Sarah, a friendly sales specialist."
        human_input_mode="NEVER"
    )

    customer = autogen.UserProxyAgent(
        name="Customer",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=0,
        code_execution_config=False
    )

    print("Sales Agent: 'Hi! 'Im Sarah, a sales specialist. What's up?\n")

    try:
        customer.initiate_chat(
            sales_agent,
            message="I am interested in your product.",
            max_turns=3
        )
    except KeyboardInterrupt:
         print("\n\nConversation ended.")
    except Exception as e:
         print(f"\n⚠️  Error: {e}")
         print("Conversation ended.")
    
    print("\n✅ Demo completed!")






if __name__ == "__main__":
    demo()