#!/usr/bin/env python3
"""
FastAPI Production Agent API with Google Gemini
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import requests
import time
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()quit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    escalated: bool = False
    confidence: float
    processing_time_ms: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    uptime_seconds: float
    version: str

class ProductionAgent:
    def __init__(self, api_key: str, use_llm: bool = True):
        self.api_key = api_key
        self.use_llm = use_llm
        self.start_time = time.time()
        
        if use_llm:
            self.api_url = f"{GEMINI_API_URL}?key={api_key}"
        
        self.faq = {
            "password": "To reset your password, click 'Forgot Password' on the login page.",
            "billing": "For billing questions, contact billing@company.com.",
            "shipping": "Standard shipping takes 3-5 business days.",
            "return": "You can return items within 30 days. Go to Orders > Return Item.",
            "cancel": "To cancel your order, go to Orders and click 'Cancel'."
        }
        
        self.escalation_keywords = ["angry", "frustrated", "complaint", "terrible", "manager"]
        
        self.metrics = {
            "total_requests": 0,
            "successful_responses": 0,
            "escalations": 0,
            "errors": 0
        }
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        try:
            self.metrics["total_requests"] += 1
            
            message_lower = request.message.lower()
            
            escalated = any(keyword in message_lower for keyword in self.escalation_keywords)
            
            if escalated:
                response_text = "I understand your frustration. Let me connect you with a human agent."
                confidence = 0.9
                self.metrics["escalations"] += 1
            else:
                response_text = None
                confidence = 0.3
                
                for keyword, answer in self.faq.items():
                    if keyword in message_lower:
                        response_text = answer
                        confidence = 0.95
                        break
                
                if not response_text and self.use_llm:
                    try:
                        response_text = await self._get_llm_response(request.message)
                        confidence = 0.85
                    except Exception as e:
                        logger.error(f"LLM error: {e}")
                        response_text = self._get_fallback_response(message_lower)
                        confidence = 0.6
                
                if not response_text:
                    response_text = self._get_fallback_response(message_lower)
                    confidence = 0.6
            
            self.metrics["successful_responses"] += 1
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return ChatResponse(
                response=response_text,
                session_id=request.session_id or f"session_{int(time.time())}",
                escalated=escalated,
                confidence=confidence,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error processing message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_llm_response(self, message: str) -> str:
        prompt = f"You are a helpful customer support agent. Customer says: '{message}'. Provide a brief, helpful response (1-2 sentences)."
        
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
    
    def _get_fallback_response(self, message_lower: str) -> str:
        if any(word in message_lower for word in ["ship", "delivery", "track"]):
            return "Track your order in 'My Orders'. Standard shipping takes 3-5 business days."
        
        if any(word in message_lower for word in ["refund", "money back"]):
            return "Refunds are processed within 5-7 business days after we receive the return."
        
        return "I can help with passwords, billing, returns, and shipping. What do you need?"
    
    def get_health(self) -> HealthResponse:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            uptime_seconds=time.time() - self.start_time,
            version="1.0.0"
        )
    
    def get_metrics(self) -> dict:
        return {
            **self.metrics,
            "uptime_seconds": time.time() - self.start_time,
            "success_rate": self.metrics["successful_responses"] / max(self.metrics["total_requests"], 1)
        }

app = FastAPI(title="Production Support Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ProductionAgent(GOOGLE_API_KEY, use_llm=True)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Chat request from user {request.user_id}: {request.message[:50]}...")
    return await agent.process_message(request)

@app.get("/health", response_model=HealthResponse)
async def health():
    return agent.get_health()

@app.get("/metrics")
async def metrics():
    return agent.get_metrics()

@app.get("/")
async def root():
    return {
        "service": "Production Support Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print(f"""
=== Production Agent API ===

✅ Using Google Gemini ({GEMINI_MODEL})

Starting server...
API Docs: http://localhost:8000/docs
Health: http://localhost:8000/health
Metrics: http://localhost:8000/metrics

    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)