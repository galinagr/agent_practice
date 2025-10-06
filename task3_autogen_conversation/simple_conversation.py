#!/usr/bin/env python3
"""
Ultra-Simple Conversation Agent with Hugging Face - 5 minute implementation
"""

from huggingface_hub import InferenceClient

# Configuration
HF_TOKEN = "hf_YOUR_TOKEN_HERE"  # Replace with your token
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

class ConversationAgent:
    def __init__(self, name, role, use_llm=True):
        self.name = name
        self.role = role
        self.conversation = []
        self.use_llm = use_llm
        
        # Initialize HF client if token is set
        if use_llm and HF_TOKEN != "hf_YOUR_TOKEN_HERE":
            try:
                self.client = InferenceClient(token=HF_TOKEN)
                self.llm_ready = True
                print(f"✅ {name} initialized with Hugging Face LLM\n")
            except Exception as e:
                print(f"⚠️  LLM initialization failed: {e}")
                self.llm_ready = False
        else:
            self.llm_ready = False
            if use_llm:
                print(f"⚠️  No HF token set - using rule-based responses\n")
    
    def respond_with_llm(self, message):
        """Get LLM-powered response"""
        try:
            # Build conversation context
            context = f"You are {self.name}, a {self.role}.\n"
            context += "Your goal: Qualify sales leads using BANT (Budget, Authority, Need, Timeline).\n"
            context += "Be friendly and conversational. Ask one relevant question.\n\n"
            
            # Add conversation history (last 3 exchanges)
            if len(self.conversation) > 0:
                context += "Conversation so far:\n"
                for line in self.conversation[-6:]:
                    context += f"{line}\n"
            
            context += f"Customer: {message}\n{self.name}:"
            
            # Get LLM response
            response = self.client.text_generation(
                context,
                model=MODEL,
                max_new_tokens=100,
                temperature=0.7,
                stop_sequences=["\n", "Customer:"]
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"LLM error: {e}, falling back to rules")
            return self.respond_with_rules(message)
    
    def respond_with_rules(self, message):
        """Fallback rule-based response"""
        msg_lower = message.lower()
        
        if "budget" in msg_lower:
            return "What's your budget range for this project?"
        elif "timeline" in msg_lower or "month" in msg_lower:
            return "When do you need this implemented?"
        elif "decision" in msg_lower or "purchasing" in msg_lower:
            return "Are you the decision maker for this purchase?"
        elif "need" in msg_lower or "problem" in msg_lower:
            return "What specific challenges are you trying to solve?"
        elif any(word in msg_lower for word in ["hi", "hello", "interested"]):
            return "Great to meet you! Tell me about your business and what you're looking for."
        else:
            return "Tell me more about your business needs."
    
    def respond(self, message):
        """Get response using LLM or rules"""
        if self.llm_ready:
            return self.respond_with_llm(message)
        else:
            return self.respond_with_rules(message)
    
    def chat(self, customer_message):
        """Process customer message and respond"""
        self.conversation.append(f"Customer: {customer_message}")
        response = self.respond(customer_message)
        self.conversation.append(f"{self.name}: {response}")
        return response
    
    def analyze_qualification(self):
        """Quick BANT analysis"""
        conv_text = " ".join(self.conversation).lower()
        
        score = {
            "Budget": "✅" if any(w in conv_text for w in ["budget", "50k", "thousand", "$"]) else "❌",
            "Authority": "✅" if any(w in conv_text for w in ["decision", "ceo", "cto", "manager"]) else "❌",
            "Need": "✅" if any(w in conv_text for w in ["need", "problem", "challenge"]) else "❌",
            "Timeline": "✅" if any(w in conv_text for w in ["month", "quarter", "timeline", "asap"]) else "❌"
        }
        
        return score

# Demo conversation
def demo():
    print("=== Ultra-Simple Conversation Agent Demo ===\n")
    
    # Create agent
    sales_agent = ConversationAgent("Sarah", "Sales Agent", use_llm=True)
    
    customer_messages = [
        "Hi, I'm interested in your product",
        "We have about 50k budget allocated",
        "We need it within 3 months",
        "Yes, I make the purchasing decisions"
    ]
    
    print("Starting conversation...\n")
    print("="*60)
    
    for msg in customer_messages:
        print(f"\n💬 Customer: {msg}")
        response = sales_agent.chat(msg)
        print(f"🤖 Sales Agent: {response}")
    
    print("\n" + "="*60)
    print("\n=== Conversation Summary ===")
    
    # Show BANT analysis
    bant_score = sales_agent.analyze_qualification()
    print("\nBANT Qualification:")
    for criteria, status in bant_score.items():
        print(f"  {criteria}: {status}")
    
    qualified = sum(1 for v in bant_score.values() if v == "✅")
    print(f"\nScore: {qualified}/4")
    print(f"Status: {'QUALIFIED ✅' if qualified >= 3 else 'NEEDS MORE INFO ⚠️'}")
    
    print("\n=== Full Conversation History ===")
    for line in sales_agent.conversation:
        print(line)

def demo_interactive():
    """Interactive mode"""
    print("=== Interactive Conversation Mode ===")
    print("You are the customer. Type 'quit' to end.\n")
    
    sales_agent = ConversationAgent("Sarah", "Sales Agent", use_llm=True)
    
    print(f"🤖 {sales_agent.name}: Hi! I'm Sarah. Tell me about your business needs.\n")
    
    while True:
        customer_input = input("💬 You: ").strip()
        
        if customer_input.lower() in ['quit', 'exit', 'bye']:
            print(f"\n🤖 {sales_agent.name}: Thanks for your time! I'll follow up soon.")
            
            # Show qualification
            bant_score = sales_agent.analyze_qualification()
            print("\n=== BANT Score ===")
            for criteria, status in bant_score.items():
                print(f"{criteria}: {status}")
            break
        
        if not customer_input:
            continue
        
        response = sales_agent.chat(customer_input)
        print(f"\n🤖 {sales_agent.name}: {response}\n")

if __name__ == "__main__":
    print("""
📦 Installation (optional):
   pip install huggingface_hub

🔑 Setup:
   1. Get free token from huggingface.co (Settings → Access Tokens)
   2. Replace 'hf_YOUR_TOKEN_HERE' with your token
   3. Run! (Works without token too - uses rules)

Choose mode:
1. Automated demo (pre-set messages)
2. Interactive mode (you chat)
    """)
    
    choice = input("Enter 1 or 2: ").strip()
    
    print()
    if choice == "2":
        demo_interactive()
    else:
        demo()