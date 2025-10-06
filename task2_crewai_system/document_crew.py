#!/usr/bin/env python3
"""
Document Processing Multi-Agent System with Google Gemini 
use extractor and analyzer without llm, but summarizer with llm for simplicity
"""

import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

def extract_text_from_document(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  📄 Read {len(content)} characters from {file_path}")
            return content
    except FileNotFoundError:
        print(f"  ⚠️  File not found: {file_path}, using simulated content")
        if file_path.endswith('.pdf'):
            return "Quarterly financial results show 15% revenue growth. Market analysis indicates strong performance."
        elif file_path.endswith('.docx'):
            return "Project requirements: Implement new customer portal with authentication and billing features."
        else:
            return "Customer feedback: Product quality is excellent. Delivery was fast and reliable."
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return "Error reading document."

def analyze_document_content(text: str) -> str:
    text_lower = text.lower()
    topics = []
    
    if any(word in text_lower for word in ['financial', 'revenue', 'profit']):
        topics.append('Finance')
    if any(word in text_lower for word in ['project', 'requirements']):
        topics.append('Project Management')
    if any(word in text_lower for word in ['customer', 'feedback']):
        topics.append('Customer Relations')
    if any(word in text_lower for word in ['market', 'analysis']):
        topics.append('Market Research')
    
    percentages = re.findall(r'(\d+)%', text)
    
    sentiment = "Neutral"
    if any(word in text_lower for word in ['growth', 'success', 'excellent', 'strong']):
        sentiment = "Positive"
    elif any(word in text_lower for word in ['risk', 'challenge', 'decline']):
        sentiment = "Negative"
    
    result = f"Topics: {', '.join(topics) if topics else 'General'}. "
    if percentages:
        result += f"Metrics: {len(percentages)} percentages found. "
    result += f"Sentiment: {sentiment}."
    
    return result

class DocumentAgent:
    def __init__(self, role: str, goal: str, api_key: str, use_llm: bool = True):
        self.role = role
        self.goal = goal
        self.api_key = api_key
        self.use_llm = use_llm
        
        if use_llm:
            self.api_url = f"{GEMINI_API_URL}?key={api_key}"
    
    def execute_task(self, task: str, context: str = "") -> str:
        print(f"\n🤖 {self.role} executing: {task}")
        
        if self.role == "Document Extractor":
            return extract_text_from_document(task)
        
        elif self.role == "Content Analyzer":
            return analyze_document_content(context)
        
        elif self.role == "Document Summarizer":
            if self.use_llm:
                try:
                    return self._get_llm_summary(context, task)
                except Exception as e:
                    print(f"⚠️  LLM failed: {e}, using fallback")
            
            return self._get_fallback_summary(context, task)
        
        return f"{self.role} completed: {task}"
    
    def _get_llm_summary(self, content: str, analysis: str) -> str:
        prompt = f"Summarize this document in 2-3 sentences:\n\nContent: {content[:500]}\n\nAnalysis: {analysis}\n\nSummary:"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 200}
        }
        
        response = requests.post(self.api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        parts = result["candidates"][0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "").strip()
        
        raise RuntimeError("Invalid response")
    
    def _get_fallback_summary(self, content: str, analysis: str) -> str:
        words = content.split()[:50]
        preview = ' '.join(words) + "..."
        return f"Document summary: {preview}\n\nAnalysis: {analysis}"

class DocumentCrew:
    def __init__(self, api_key: str, use_llm: bool = True):
        self.extractor = DocumentAgent("Document Extractor", "Extract text from documents", api_key, use_llm)
        self.analyzer = DocumentAgent("Content Analyzer", "Analyze document content", api_key, use_llm)
        self.summarizer = DocumentAgent("Document Summarizer", "Create document summaries", api_key, use_llm)
    
    def process_document(self, file_path: str) -> dict:
        print(f"\n{'='*60}")
        print(f"Processing: {file_path}")
        print('='*60)
        
        text = self.extractor.execute_task(file_path)
        
        analysis = self.analyzer.execute_task("Analyze content", context=text)
        print(f"  ✅ Analysis: {analysis}")
        
        summary = self.summarizer.execute_task(analysis, context=text)
        print(f"  ✅ Summary generated")
        
        return {
            "file": file_path,
            "text_length": len(text),
            "analysis": analysis,
            "summary": summary
        }

def demo():
    print("=== Document Processing Crew Demo ===\n")
    print(f"✅ Using Google Gemini ({GEMINI_MODEL})\n")
    
    crew = DocumentCrew(GOOGLE_API_KEY, use_llm=True)
    
    documents = [
        "financial_report.pdf",
        "project_spec.docx",
        "customer_feedback.txt"
    ]
    
    results = []
    for doc in documents:
        result = crew.process_document(doc)
        results.append(result)
    
    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print('='*60)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['file']}")
        print(f"   Length: {result['text_length']} chars")
        print(f"   Analysis: {result['analysis']}")
        print(f"   Summary: {result['summary'][:100]}...")
    
    print("\n✅ All documents processed!")

if __name__ == "__main__":
    demo()