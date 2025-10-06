# Task 1: LangChain Support Agent

## Scenario
"Build a customer support agent using LangChain tools and memory"

## Why LangChain for Customer Support?

### Advantages:
- **Built-in Tools**: Easy function calling for FAQ lookup, ticket creation
- **Memory Management**: Conversation history out of the box
- **Agent Framework**: Handles tool selection and execution automatically
- **Extensible**: Easy to add new tools and capabilities

### Key LangChain Concepts:
- **Agent**: Autonomous entity that can use tools to accomplish tasks
- **Tools**: Functions the agent can call (FAQ lookup, escalation, etc.)
- **Memory**: Conversation buffer to maintain context
- **Chain**: Sequence of operations for processing requests

## Implementation Strategy
1. Define tools (FAQ lookup, escalation)
2. Create agent with tools and memory
3. Add conversation buffer for context
4. Handle tool execution and responses

## Time: 10-15 minutes

## Points to Discuss

### 1. Agent vs Chain vs Tool Concepts

**Tools** are the building blocks:
- Individual functions the agent can call (e.g., `lookup_faq`, `escalate`)
- Defined with `@tool` decorator, include name, description, and parameters
- The description is crucial - LLM uses it to decide when to use the tool
- Example: `lookup_faq(query: str) -> str` searches FAQ database

**Chains** are deterministic sequences:
- Predefined sequence of operations that always execute in order
- Example: `Input → Prompt → LLM → Output Parser → Response`
- No decision-making - just data transformation pipeline
- Use when workflow is fixed and predictable

**Agents** are autonomous decision-makers:
- Use LLM to decide which tool(s) to use and in what order
- Follow ReAct pattern: Reason → Act → Observe → Repeat
- Can handle multi-step tasks dynamically
- Example: Agent sees "forgot password" → decides to call `lookup_faq("password")` → returns result

**Key Difference**:
- Chain: Always does A → B → C
- Agent: Decides "Should I do A? Maybe B? Let me check C first"

### 2. How LangChain Handles Tool Selection

**ReAct (Reasoning + Acting) Pattern**:
```
Thought: I need to help with a password reset
Action: lookup_faq
Action Input: "password"
Observation: "Click 'Forgot Password' on login page"
Thought: I now have the answer
Final Answer: To reset your password...
```

**Selection Process**:
1. LLM receives user query + tool descriptions
2. LLM reasons about which tool is most appropriate
3. LLM outputs structured action (tool name + input)
4. Framework parses action and executes tool
5. Tool result fed back to LLM as "observation"
6. LLM decides: use another tool or give final answer

**Tool Description is Critical**:
```python
@tool
def lookup_faq(query: str) -> str:
    """Look up FAQ answers for common questions about 
    password, billing, or returns"""  # ← LLM uses this!
```

**Prompt Engineering**:
- Agent prompt includes tool names and descriptions
- LLM trained to follow specific format (Action/Action Input)
- `AgentExecutor` handles parsing and error recovery

### 3. Memory Management Strategies

**ConversationBufferMemory** (Simplest):
```python
memory = ConversationBufferMemory(memory_key="chat_history")
# Stores entire conversation - grows unbounded
```
- Pros: Full context preserved
- Cons: Token limits, expensive for long conversations

**ConversationBufferWindowMemory** (Sliding Window):
```python
memory = ConversationBufferWindowMemory(k=5)  # Last 5 exchanges
```
- Pros: Fixed size, predictable cost
- Cons: Loses older context

**ConversationSummaryMemory** (Compressed):
```python
memory = ConversationSummaryMemory(llm=llm)
# Summarizes old messages, keeps recent ones verbatim
```
- Pros: Scales to long conversations
- Cons: Requires extra LLM calls, may lose details

**ConversationTokenBufferMemory** (Token-based):
```python
memory = ConversationTokenBufferMemory(llm=llm, max_token_limit=500)
```
- Pros: Precise token control
- Cons: More complex, needs token counting

**Best Practice for Production**:
- Use `ConversationSummaryBufferMemory` (hybrid approach)
- Store full history in database (Redis/PostgreSQL)
- Load relevant context on-demand
- Implement session expiration (e.g., 30 minutes)

### 4. Production Considerations

**Rate Limiting**:
```python
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback

# Track token usage
with get_openai_callback() as cb:
    response = agent.run(query)
    print(f"Tokens: {cb.total_tokens}, Cost: ${cb.total_cost}")

# Implement user-level rate limits
rate_limiter = {
    "user123": {"requests": 10, "window": 60}  # 10 req/min
}
```

**Monitoring & Observability**:
```python
# LangSmith integration (LangChain's monitoring tool)
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"

# Custom callbacks for logging
from langchain.callbacks import StdOutCallbackHandler
agent = AgentExecutor(
    agent=agent, 
    tools=tools,
    callbacks=[StdOutCallbackHandler()],  # Log all steps
    verbose=True
)
```

**Error Handling**:
```python
agent = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=5,  # Prevent infinite loops
    max_execution_time=30,  # 30 second timeout
    handle_parsing_errors=True,  # Graceful fallback
    early_stopping_method="generate"  # Stop on first answer
)
```

**Caching**:
```python
from langchain.cache import RedisCache
import langchain

# Cache LLM responses
langchain.llm_cache = RedisCache(redis_url="redis://localhost:6379")

# Semantic cache for similar queries
from langchain.cache import GPTCache
langchain.llm_cache = GPTCache()
```

**Security**:
- Validate tool inputs (prevent injection attacks)
- Sanitize user messages before sending to LLM
- Implement output filtering for sensitive data
- Use separate API keys per environment
- Set up alerts for unusual patterns (spike in errors, costs)

**Cost Optimization**:
- Use cheaper models for simple tasks (gpt-3.5-turbo vs gpt-4)
- Implement fallback to rule-based responses when possible
- Cache frequent queries
- Batch requests when latency allows
- Monitor token usage per user/session

**Scalability**:
- Async execution for concurrent requests
- Queue system for background processing (Celery, RabbitMQ)
- Horizontal scaling with load balancer
- Separate memory storage (Redis cluster)
- CDN for static responses (FAQs)
