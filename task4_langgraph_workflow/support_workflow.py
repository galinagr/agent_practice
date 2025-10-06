#!/usr/bin/env python3
"""
LangGraph Support Workflow Agent - 10-15 minute implementation
Demonstrates: Stateful workflows, conditional routing, error handling
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END, START
import os

# Set up OpenAI (optional)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Define workflow state - this persists across all nodes
class SupportWorkflowState(TypedDict):
    """State that flows through the support workflow"""
    request_id: str
    user_message: str
    category: Optional[str]
    priority: Optional[str]
    response: Optional[str]
    escalated: bool
    ticket_created: bool
    error_message: Optional[str]
    step_count: int

# Workflow nodes - each represents a processing step
def validate_request(state: SupportWorkflowState) -> SupportWorkflowState:
    """Validate incoming support request"""
    print(f"🔍 Validating request {state['request_id']}")
    
    # Simple validation logic
    message = state["user_message"]
    if not message or len(message.strip()) == 0:
        state["error_message"] = "Message is empty"
        return state
    
    # Allow short greetings like "Hi", "Hello"
    if len(message) < 2:
        state["error_message"] = "Message too short"
        return state
    
    if len(message) > 1000:
        state["error_message"] = "Message too long (max 1000 characters)"
        return state
    
    state["step_count"] = state.get("step_count", 0) + 1
    print(f"✅ Request validated successfully")
    return state

def categorize_request(state: SupportWorkflowState) -> SupportWorkflowState:
    """Categorize the support request"""
    print(f"📂 Categorizing request {state['request_id']}")
    
    message = state["user_message"].lower()
    
    # Simple categorization logic
    if any(word in message for word in ["password", "login", "access"]):
        state["category"] = "authentication"
        state["priority"] = "medium"
    elif any(word in message for word in ["billing", "payment", "invoice"]):
        state["category"] = "billing"
        state["priority"] = "high"
    elif any(word in message for word in ["bug", "error", "crash", "broken"]):
        state["category"] = "technical"
        state["priority"] = "high"
    elif any(word in message for word in ["angry", "frustrated", "terrible"]):
        state["category"] = "complaint"
        state["priority"] = "urgent"
    else:
        state["category"] = "general"
        state["priority"] = "low"
    
    state["step_count"] = state.get("step_count", 0) + 1
    print(f"✅ Categorized as: {state['category']} (Priority: {state['priority']})")
    return state

def generate_response(state: SupportWorkflowState) -> SupportWorkflowState:
    """Generate appropriate response based on category"""
    print(f"💬 Generating response for {state['request_id']}")
    
    category = state.get("category") or "general"
    
    # Response templates based on category
    responses = {
        "authentication": "To reset your password, please click 'Forgot Password' on the login page and follow the instructions.",
        "billing": "For billing inquiries, please check your account settings or contact our billing team at billing@company.com",
        "technical": "I've logged this technical issue for our engineering team. You should receive an update within 24 hours.",
        "complaint": "I sincerely apologize for your experience. Let me escalate this to our customer success team immediately.",
        "general": "Thank you for contacting us. I'll make sure you get the help you need."
    }
    
    state["response"] = responses.get(category, "Thank you for your message. We'll get back to you soon.")
    state["step_count"] = state.get("step_count", 0) + 1
    print(f"✅ Response generated")
    return state

def check_escalation_needed(state: SupportWorkflowState) -> SupportWorkflowState:
    """Check if request needs escalation to human agent"""
    print(f"🚨 Checking escalation for {state['request_id']}")
    
    # Escalation logic
    escalation_needed = (
        state["priority"] in ["urgent", "high"] or
        state["category"] in ["complaint", "technical"] or
        any(word in state["user_message"].lower() for word in ["manager", "supervisor", "human"])
    )
    
    state["escalated"] = escalation_needed
    state["step_count"] = state.get("step_count", 0) + 1
    
    if escalation_needed:
        print(f"🚨 Escalation required - routing to human agent")
    else:
        print(f"✅ No escalation needed")
    
    return state

def create_ticket(state: SupportWorkflowState) -> SupportWorkflowState:
    """Create support ticket for escalated requests"""
    print(f"🎫 Creating support ticket for {state['request_id']}")
    
    # Simulate ticket creation
    ticket_id = f"TICKET-{hash(state['user_message']) % 10000}"
    
    state["ticket_created"] = True
    current_response = state.get("response") or ""
    state["response"] = current_response + f"\n\nSupport ticket {ticket_id} has been created. A human agent will contact you within 2 hours."
    state["step_count"] = state.get("step_count", 0) + 1
    
    print(f"✅ Ticket {ticket_id} created")
    return state

def handle_error(state: SupportWorkflowState) -> SupportWorkflowState:
    """Handle workflow errors"""
    print(f"❌ Handling error for {state['request_id']}: {state['error_message']}")
    
    state["response"] = f"I'm sorry, there was an issue processing your request: {state['error_message']}. Please try again or contact support directly."
    state["escalated"] = True
    state["step_count"] = state.get("step_count", 0) + 1
    
    return state

def send_response(state: SupportWorkflowState) -> SupportWorkflowState:
    """Send final response to user"""
    print(f"📤 Sending response for {state['request_id']}")
    
    # In real system, would send email/SMS/chat response
    print(f"Response: {state['response']}")
    
    state["step_count"] = state.get("step_count", 0) + 1
    print(f"✅ Response sent (Total steps: {state['step_count']})")
    return state

# Conditional routing functions
def should_escalate(state: SupportWorkflowState) -> Literal["escalate", "respond"]:
    """Determine if request should be escalated"""
    return "escalate" if state["escalated"] else "respond"

def has_error(state: SupportWorkflowState) -> Literal["error", "continue"]:
    """Check if there's an error to handle"""
    return "error" if state.get("error_message") else "continue"

# Create the LangGraph workflow
def create_support_workflow():
    """Create a LangGraph workflow for support request processing"""
    
    # Initialize the state graph
    workflow = StateGraph(SupportWorkflowState)
    
    # Add nodes (processing steps)
    workflow.add_node("validate", validate_request)
    workflow.add_node("categorize", categorize_request)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("check_escalation", check_escalation_needed)
    workflow.add_node("create_ticket", create_ticket)
    workflow.add_node("send_response", send_response)
    workflow.add_node("handle_error", handle_error)
    
    # Add edges (workflow flow)
    workflow.add_edge(START, "validate")
    
    # Conditional routing after validation
    workflow.add_conditional_edges(
        "validate",
        has_error,
        {
            "error": "handle_error",
            "continue": "categorize"
        }
    )
    
    workflow.add_edge("categorize", "generate_response")
    workflow.add_edge("generate_response", "check_escalation")
    
    # Conditional routing after escalation check
    workflow.add_conditional_edges(
        "check_escalation",
        should_escalate,
        {
            "escalate": "create_ticket",
            "respond": "send_response"
        }
    )
    
    workflow.add_edge("create_ticket", "send_response")
    workflow.add_edge("send_response", END)
    workflow.add_edge("handle_error", END)
    
    # Compile the workflow
    return workflow.compile()

# Mock workflow for demo without LangGraph
class MockSupportWorkflow:
    """Mock workflow for demo without dependencies"""
    
    def __init__(self):
        self.steps = [
            validate_request,
            categorize_request,
            generate_response,
            check_escalation_needed,
            create_ticket,  # Only if escalated
            send_response
        ]
    
    def process_request(self, request_id: str, user_message: str) -> SupportWorkflowState:
        """Process support request through workflow steps"""
        
        print(f"=== Mock Support Workflow Processing ===")
        print(f"Request ID: {request_id}")
        print(f"Message: {user_message}\n")
        
        # Initialize state
        state = SupportWorkflowState(
            request_id=request_id,
            user_message=user_message,
            category=None,
            priority=None,
            response=None,
            escalated=False,
            ticket_created=False,
            error_message=None,
            step_count=0
        )
        
        # Process through workflow steps
        try:
            # Step 1: Validate
            state = validate_request(state)
            if state.get("error_message"):
                return handle_error(state)
            
            # Step 2: Categorize
            state = categorize_request(state)
            
            # Step 3: Generate response
            state = generate_response(state)
            
            # Step 4: Check escalation
            state = check_escalation_needed(state)
            
            # Step 5: Create ticket if needed
            if state["escalated"]:
                state = create_ticket(state)
            
            # Step 6: Send response
            state = send_response(state)
            
        except Exception as e:
            state["error_message"] = str(e)
            state = handle_error(state)
        
        return state

# Demo function
def demo_langgraph_workflow():
    """Demo the LangGraph support workflow"""
    
    print("=== LangGraph Support Workflow Demo ===\n")
    
    # Test cases
    test_requests = [
        ("REQ001", "I forgot my password and can't log in"),
        ("REQ002", "This app is terrible! It keeps crashing!"),
        ("REQ003", "How do I update my billing information?"),
        ("REQ004", "Hi"),  # Too short - should error
    ]
    
    try:
        # Try real LangGraph workflow
        workflow = create_support_workflow()
        
        for request_id, message in test_requests:
            print(f"\n{'='*60}")
            initial_state = SupportWorkflowState(
                request_id=request_id,
                user_message=message,
                category=None,
                priority=None,
                response=None,
                escalated=False,
                ticket_created=False,
                error_message=None,
                step_count=0
            )
            
            result = workflow.invoke(initial_state)
            print(f"Final State: {result}")
            print(f"{'='*60}")
            
    except Exception as e:
        print(f"LangGraph not available: {e}")
        print("Running mock workflow instead...\n")
        
        # Use mock workflow
        mock_workflow = MockSupportWorkflow()
        
        for request_id, message in test_requests:
            print(f"\n{'='*60}")
            result = mock_workflow.process_request(request_id, message)
            print(f"{'='*60}")

if __name__ == "__main__":
    demo_langgraph_workflow()
