#!/usr/bin/env python3
"""
Ultra-Simple FastAPI Agent
"""

from fastapi import FastAPI
from pydantic import BaseModel

# Simple models
class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    escalated: bool = False

# Simple agent logic
def process_message(message: str) -> ChatResponse:
    message_lower = message.lower()
    
    # Simple FAQ matching
    if "password" in message_lower:
        return ChatResponse(response="Reset password on login page")
    elif "billing" in message_lower:
        return ChatResponse(response="Contact billing@company.com")
    elif any(word in message_lower for word in ["angry", "terrible"]):
        return ChatResponse(response="Let me escalate to human agent", escalated=True)
    else:
        return ChatResponse(response="How can I help you?")

# FastAPI app
app = FastAPI(title="Simple Support Agent API")

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    return process_message(request.message)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Support Agent API", "docs": "/docs"}

# Demo without server
def demo():
    print("=== FastAPI Agent Demo ===")
    
    test_requests = [
        ChatRequest(message="I forgot my password", user_id="user1"),
        ChatRequest(message="This is terrible!", user_id="user2"),
        ChatRequest(message="Hello", user_id="user3")
    ]
    
    for req in test_requests:
        response = process_message(req.message)
        print(f"User: {req.message}")
        print(f"Agent: {response.response} (Escalated: {response.escalated})")
        print()

if __name__ == "__main__":
    print("To run server: uvicorn simple_api:app --reload")
    print("API docs: http://localhost:8000/docs")
    print()
    demo()
