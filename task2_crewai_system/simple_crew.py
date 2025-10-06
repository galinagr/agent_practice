#!/usr/bin/env python3
"""
Multi-Agent Crew with Google Gemini
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

class Agent:
    def __init__(self, role: str, goal: str, api_key: str | None = None, use_llm: bool = True):
        self.role = role
        self.goal = goal
        self.api_key = api_key
        self.use_llm = use_llm and api_key
        
        if self.use_llm:
            self.api_url = f"{GEMINI_API_URL}?key={api_key}"
    
    def work(self, task: str) -> str:
        if self.use_llm:
            try:
                return self._get_llm_response(task)
            except Exception as e:
                print(f"⚠️  LLM failed for {self.role}: {e}")
                return self._get_fallback_response(task)
        
        return self._get_fallback_response(task)
    
    def _get_llm_response(self, task: str) -> str:
        prompt = f"You are a {self.role}. Your goal: {self.goal}\n\nTask: {task}\n\nProvide a concise response (2-3 sentences):"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 150}
        }
        
        response = requests.post(self.api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        parts = result["candidates"][0].get("content", {}).get("parts", [])
        if parts:
            text = parts[0].get("text", "").strip()
            return f"{self.role}: {text}"
        
        raise RuntimeError("Invalid response")
    
    def _get_fallback_response(self, task: str) -> str:
        return f"{self.role}: Completed task - {task}"

class Crew:
    def __init__(self, agents: list):
        self.agents = agents
    
    def kickoff(self, tasks: list) -> list:
        results = []
        for i, task in enumerate(tasks):
            agent = self.agents[i % len(self.agents)]
            print(f"\n🤖 {agent.role} working on task {i+1}...")
            result = agent.work(task)
            results.append(result)
            print(f"✅ Completed")
        return results

def create_crew(api_key: str, use_llm: bool = True):
    extractor = Agent("Text Extractor", "Extract text from documents", api_key, use_llm)
    analyzer = Agent("Content Analyzer", "Analyze document content", api_key, use_llm) 
    summarizer = Agent("Summarizer", "Create document summaries", api_key, use_llm)
    
    return Crew([extractor, analyzer, summarizer])

def demo():
    print("=== Multi-Agent Crew Demo ===\n")
    
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        return
    
    print(f"✅ Using Google Gemini ({GEMINI_MODEL})\n")
    
    crew = create_crew(GOOGLE_API_KEY, use_llm=True)
    
    tasks = [
        "Extract text from report.pdf",
        "Analyze content for key topics", 
        "Generate executive summary"
    ]
    
    print("📋 Tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task}")
    
    print("\n" + "="*60)
    results = crew.kickoff(tasks)
    
    print("\n" + "="*60)
    print("\n📊 Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result}")

if __name__ == "__main__":
    demo()