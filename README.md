# Agent Practice - Multi-Agent Systems

This project contains 5 practical tasks demonstrating multi-agent systems using the AGNTCY ACP (Agent Connect Protocol) framework with Google Gemini.

## Agent Framework Overview

Practical agent implementations using industry-standard patterns:

- **LangChain**: Agent tools, memory, and chains
- **CrewAI**: Multi-agent collaboration and task delegation  
- **AutoGen**: Conversational multi-agent systems
- **LangGraph**: Workflow orchestration and state management
- **FastAPI**: Production deployment patterns

## Why These Frameworks?

### Key Benefits:
- **Industry Standard**: Widely used in production
- **Quick Implementation**: Simple, memorable patterns
- **Extensible**: Easy to add complexity
- **Production Ready**: Real frameworks used in business

### Skills Demonstrated:
- **Agent Tools**: Function calling and external integrations
- **Memory Management**: Conversation history and context
- **Multi-Agent Systems**: Coordination and task delegation
- **Workflow Design**: State machines and process automation

## Tasks

### Task 1: LangChain Support Agent
**Build a customer support agent with tools and memory**
- **File**: `task1_langchain_agent/`
- **Model**: Google Gemini 2.0 Flash
- **Skills**: Agent tools, function calling, memory management

### Task 2: CrewAI Multi-Agent System  
**Create a document processing crew with specialized agent roles**
- **File**: `task2_crewai_system/`
- **Model**: Google Gemini 2.0 Flash
- **Skills**: Multi-agent coordination, role definition, task management

### Task 3: AutoGen Conversation System
**Build a sales qualification system with AutoGen conversational agents**
- **File**: `task3_autogen_conversation/`
- **Model**: Google Gemini 2.0 Flash (via custom AutoGen agent)
- **Skills**: AutoGen framework, custom LLM integration, multi-turn dialogue

### Task 4: LangGraph Workflow Agent
**Create a workflow agent that processes requests through multiple steps**
- **File**: `task4_langgraph_workflow/`
- **Model**: Google Gemini 2.0 Flash
- **Skills**: Workflow design, state machines, conditional logic

### Task 5: FastAPI Production Agent
**Deploy an agent as a production API with proper error handling**
- **File**: `task5_fastapi_deployment/`
- **Model**: Google Gemini 2.0 Flash
- **Skills**: API deployment, error handling, production patterns

## Google Gemini Integration

All tasks use **Google Gemini 2.0 Flash** for real LLM inference:
- Fast response times
- High-quality conversational AI
- Reliable and production-ready
- Free tier available

## Prerequisites

- Python 3.11+ (recommended) or 3.9+
- Google AI API key (free from https://makersuite.google.com/app/apikey)
- Basic understanding of async/await
- Familiarity with agent concepts

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google API key
# Or use the provided default key for testing
```

## Configuration

The project uses a `.env` file for configuration:

```bash
# .env file
GOOGLE_API_KEY=your-api-key-here

# Or set as environment variable:
export GOOGLE_API_KEY="your-api-key-here"
```

**Get your free API key from:** https://makersuite.google.com/app/apikey

**Note:** The `.env` file is gitignored for security. Use `.env.example` as a template.

## How to Run Each Task

### Task 1: LangChain Support Agent
```bash
cd task1_langchain_agent
python3 support_agent.py
```
**What it does**: Shows agent tools and simple agent logic with FAQ lookup
**Output**: Processes 3 test messages and shows LLM-powered responses

### Task 2: CrewAI Multi-Agent System
```bash
cd task2_crewai_system

# Simple crew
python3 simple_crew.py

# Document processing crew
python3 document_crew.py
```
**What it does**: Demonstrates multi-agent coordination with specialized agents
**Output**: Shows how agents work together on tasks

### Task 3: AutoGen Conversation System
```bash
cd task3_autogen_conversation
python3 sales_conversation.py
```
**What it does**: AutoGen-powered sales conversation with custom Gemini agent
**Output**: Interactive conversation using AutoGen's agent framework

### Task 4: LangGraph Workflow Agent
```bash
cd task4_langgraph_workflow

# Simple workflow (rule-based)
python3 simple_workflow.py

# LLM-powered workflow
python3 hf_workflow.py
```
**What it does**: Stateful workflow with validation → categorization → response
**Output**: Processes support requests through workflow steps with LLM integration

### Task 5: FastAPI Production Agent
```bash
cd task5_fastapi_deployment

# Simple API (rule-based)
python3 simple_api.py

# Production API with LLM
python3 production_api.py
# Or: uvicorn production_api:app --reload --port 8000
# Then visit: http://localhost:8000/docs
```
**What it does**: Production API with LLM integration, monitoring, async processing
**Output**: Interactive API docs with real-time Gemini-powered responses

## Quick Test All Tasks

```bash
cd agent_practice

echo "=== Testing Task 1 ==="
cd task1_langchain_agent && python3 support_agent.py && cd ..

echo "=== Testing Task 2 ==="
cd task2_crewai_system && python3 simple_crew.py && cd ..

echo "=== Testing Task 3 ==="
cd task3_autogen_conversation && python3 sales_conversation.py && cd ..

echo "=== Testing Task 4 ==="
cd task4_langgraph_workflow && python3 simple_workflow.py && cd ..

echo "=== Testing Task 5 ==="
cd task5_fastapi_deployment && python3 simple_api.py && cd ..
```

## Expected Output Summary

- **Task 1**: Shows FAQ matching, escalation logic, and LLM responses
- **Task 2**: Shows 3 agents processing document tasks with LLM summaries
- **Task 3**: Shows sales conversation with Gemini-powered responses
- **Task 4**: Shows workflow steps: validate → categorize → respond (with LLM)
- **Task 5**: Shows API demo with health check and LLM chat processing

## Architecture Concepts

### Agent Characteristics:
- **Autonomy**: Operates without constant human intervention
- **Reactivity**: Responds to environmental changes
- **Proactivity**: Takes initiative to achieve goals
- **Social Ability**: Communicates with other agents

### Design Patterns:
- **Reactive Agents**: Respond to stimuli (Task 1, 5)
- **Deliberative Agents**: Plan and reason (Task 2, 4)
- **Hybrid Agents**: Combine reactive and deliberative (Task 3)

### Production Considerations:
- **Monitoring**: Health checks, metrics, logging
- **Scaling**: Async processing, multiple workers
- **Fault Tolerance**: Error handling, fallbacks
- **Security**: API authentication, rate limiting

## Common Questions

**Q: What makes this an agent vs just a service?**
A: Agents have autonomy, can make decisions, maintain state, and coordinate with other agents.

**Q: How do agents coordinate?**
A: Through message passing, shared state, or orchestration layers (like in CrewAI).

**Q: When to use agents vs microservices?**
A: Use agents when you need autonomous decision-making and dynamic coordination. Use microservices for well-defined, stateless operations.

**Q: How to handle agent failures?**
A: Implement fallback logic, health checks, retry mechanisms, and graceful degradation.

Each task folder contains a complete solution demonstrating these concepts.

## Environment Variables

All tasks support environment variable configuration:

```bash
# Required for LLM features
export GOOGLE_API_KEY="your-api-key-here"

# Default value (for reference):
# GOOGLE_API_KEY="AIzaSyDROlweOncKwmyFx3Rp8WUbBzJMuNoiP_A"
```

## License

See LICENSE file for details.