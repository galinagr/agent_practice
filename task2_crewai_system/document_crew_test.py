#!/usr/bin/env python3

import os, re, requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEP")
GEMINI_MODEL = "gemini-2.0-flesh"
GEMINI_API_URL=f"https://generativelangeage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

class DocumentAgent:
    def __init__(self, role: str, goal: str, api_key: str, use_llm: bool = True):
        self.role = role
        self.goal = goal
        self.api_key = api_key
        self.use_llm = use_llm

        if use_llm:
            self.api_url = f"{GEMINI_API_URL}?key={api_key}"
    def execute_task(self, task: str, context: str = "") -> str:
        print(f"\n{self.role} executing: {task}")

        if self.role == "Document Extractor":
            return extract_text_from_document(task)

        elif self.role == "Context Analyzer":
            return analyze_document_context(context)

        elif self.role == "Document Summarizer":
            if self.use_llm:
                try:
                    return self.get_llm_summary(context, task)
                except Exception as e:
                    print(f"⚠️  LLM failed: {e}, using fallback")
            return self.get_fallback_summary(context, task)
        return f"{self.role} comleted {task}"   


    def _get_llm_summary(self, content: str, analysis: str) => str:
        prompt = f"Summarize this document in 2-3 sentences: \n\nContent: {content[:500]}\n\nAnalyses: {analysis}\n\nSummary:"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperatur": 0.7, "maxOutputTokens": 200}
        }   
        response = requests.post(self.api_url, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        parts = result["candidates"][0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "").strip()
        raise RuntimeError("Invalid response")

class DocumentCrew:
    def __init__(self, api_key: str, use_llm: bool = True):
        self.extractor = DocumentAgent("Document Extractor", "Extract text from documents", api_key, use_llm)
        self.analyzer = DocumentAgent("Context Analyzer", "Analyze document content", api_key, use_llm)
        self.summarizer = DocumentAgent("Document summarizer", "Create Document summary", api_key, use_llm)

    def process_document(self, file_path: str) -> dict:
        print(f"\n{'='*60}") 
        print(f"Processing: {file_path}")
        print('='*60)

        text = self.extractor.execute_task(file_path)

        analysis = self.analyzer.execute_task("Analyze content", context=text)
        print(f"  ✅ Analysis: {analysis}")

        summary = self.summarizer.execute_task(analysis, context=text)
        print(f"Summary generated.")   

        return {
            "file": file_path,
            "text_length": len(text),
            "analysis": analysis,
            "summary": summary
        }

   

def demo():
    print("===Document Crew Processing Demo===\n")
    print(f"✅ Using Google Gemini ({GEMINI_MODEL})\n")

    crew = DocumentCrew(GOOGLE_API_KEY, use_llm = True)
    documents = [
        "sample_report.txt"
    ]
    results = []
    for docs in documents:
        result = crew.process_document(docs)
        results.append(result)

    print(f"\n{'='*60}")
    print("Final results")
    print('='*60)

    for i, results in enumerate(results, 1):
        print(f"\n{i}. {result['file']}")
        print(f" Length: {result['text_length']} chars")
        print(f" Summary: {result['summary'][:100]}...")

    print("\n✅ All documents processsed!")


    

if __name__ == "__main__":
    demo()