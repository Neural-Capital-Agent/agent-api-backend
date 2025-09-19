# Coral Protocol Agent Interaction Guide

This document explains how agents interact with each other using the Coral Protocol in the Neural Capital AI system.

## Agent Interaction through Coral Protocol

### 1. **Registration and Discovery** (`coral_registry.py:110-154`)
- Each agent registers with the Coral Server at startup
- Agents advertise their capabilities (e.g., "portfolio_optimization", "market_data")
- Other agents can discover available agents and their capabilities

### 2. **Direct Agent Invocation** (`coral_client.py:186-302`)
The main interaction mechanism is `invoke_agent()`:
```python
await coral_client.invoke_agent(
    target_agent="data_agent",
    method="get_market_context",
    parameters={"timestamp": "2024-01-01"}
)
```

### 3. **Cross-Agent Validation** (`coral_client.py:606-644`)
Agents can validate decisions using multiple other agents:
```python
await coral_client.cross_validate_decision(
    decision=portfolio_decision,
    validators=["data_agent", "planner_agent"]
)
```

### 4. **Specialized Interaction Patterns**

**Data Sharing** (`coral_client.py:494-512`):
```python
# Get market context from Data Agent
market_data = await coral_client.get_market_context_from_data_agent()

# Validate signals with Data Agent
validation = await coral_client.validate_macro_signals(signals)
```

**Decision Explanations** (`coral_client.py:575-604`):
```python
# Gather context from multiple agents for explanations
context = await coral_client.get_explanation_context(action)
```

### 5. **Agent Communication Flow**

```
Portfolio Agent → Data Agent: "get_market_context"
Data Agent → Portfolio Agent: Returns market data

Portfolio Agent → Planner Agent: "validate_strategy"
Planner Agent → Portfolio Agent: Returns validation results

Any Agent → Explainer Agent: "explain_decision"
Explainer Agent → Multiple Agents: Gathers context → Returns explanation
```

### 6. **Network Health Monitoring** (`coral_client.py:666-712`)
Agents can check health of the entire network:
```python
network_health = await coral_client.health_check_all_agents()
```

### 7. **Key Interaction Features**

- **Asynchronous**: All interactions are non-blocking
- **Error Handling**: Fallback responses when agents are unavailable
- **Verification**: Blockchain hashing for decision integrity
- **Payment**: CORAL token payments for services (simulated)
- **Discovery**: Dynamic agent discovery and capability matching

## Quick Setup (3 Steps)

### Step 1: Configure Environment
Add to your `.env` file:
```bash
CORAL_SERVER_URL=http://localhost:5555
CORAL_API_BASE_URL=http://localhost:8000
```

### Step 2: Start Everything
```bash
# 1. Start Coral Server (if not running)
# Make sure Coral Server is at http://localhost:5555

# 2. Start your API
python app.py
```

### Step 3: Check It Works
```bash
python test_coral_integration.py
```

✅ **Success!** Your agents should now appear in Coral Studio.

## Your Agents in Coral Studio

### 📊 Data Agent
- **What it does**: Gets market data and economic indicators
- **Studio Role**: Market Data Provider
- **Capabilities**: Real-time prices, market analysis, economic data

### 💼 Portfolio Agent
- **What it does**: Builds and optimizes investment portfolios
- **Studio Role**: Portfolio Manager
- **Capabilities**: Asset allocation, risk management, rebalancing

### 🎯 Planner Agent
- **What it does**: Understands financial goals and creates plans
- **Studio Role**: Financial Planner
- **Capabilities**: Goal parsing, strategy creation, lifecycle planning

### 💬 Explainer Agent
- **What it does**: Translates complex finance into simple language
- **Studio Role**: Client Advisor
- **Capabilities**: Decision explanations, jargon translation

## Check Status

```bash
# See if agents are connected
curl http://localhost:8000/api/v1/coral/status

# Check individual agent health
curl http://localhost:8000/api/v1/coral/health/data_agent
```

## Troubleshooting

### ❌ Agents Not Showing Up?

**Check the basics:**
```bash
# Is Coral Server running?
curl http://localhost:5555

# Are your agents connected?
curl http://localhost:8000/api/v1/coral/status
```

**Fix common issues:**
1. **Wrong URL**: Check your `.env` file has correct URLs
2. **Server Down**: Make sure Coral Server is running
3. **Firewall**: Check if ports 5555 and 8000 are open

### 🔄 Re-register Agents
If something goes wrong, re-register manually:
```bash
curl -X POST http://localhost:8000/api/v1/coral/register
```

## What's Next?

Once connected, you can:
- **Visualize Workflows**: See your agents working together
- **Monitor Performance**: Track agent response times
- **Create Workflows**: Drag-and-drop financial analysis workflows
- **Connect Networks**: Link with other financial agent networks

## Example Workflow

**Complete Financial Analysis:**
1. 📊 Data Agent → Gets market data
2. 💼 Portfolio Agent → Optimizes allocation
3. 🎯 Planner Agent → Aligns with goals
4. 💬 Explainer Agent → Explains in plain English

## Implementation Details

### Agent Registration Process

Each agent follows this registration flow:

1. **Initialize Coral Client**: Create a `CoralClient` instance with server URL and agent ID
2. **Register Capabilities**: Call `register_agent()` with agent type and capabilities list
3. **Health Monitoring**: Implement health check endpoints for monitoring
4. **Service Discovery**: Use `discover_agents()` to find other available agents

### Message Protocol

Agent communication uses structured messages:

```python
class CoralMessage(BaseModel):
    agent_id: str          # Sender agent ID
    target_agent: str      # Recipient agent ID
    method: str           # Method to invoke
    parameters: Dict      # Method parameters
    timestamp: datetime   # Message timestamp
```

### Error Handling and Fallbacks

The system provides robust error handling:

- **Network Failures**: Automatic fallback to local mock responses
- **Agent Unavailable**: Graceful degradation with error messages
- **Timeout Protection**: 10-second timeouts on all agent calls
- **Health Monitoring**: Continuous health checks detect failed agents

### Security and Verification

Coral Protocol includes several security features:

- **Verification Hashes**: SHA-256 hashes for data integrity
- **Blockchain Storage**: Simulated blockchain verification (ready for production)
- **Token Payments**: CORAL token system for service payments
- **Access Control**: Agent capability-based access control

## Example: Complete Financial Analysis Workflow

Here's how agents collaborate for a complete financial analysis:

```python
# 1. Data Agent gathers market context
market_data = await coral_client.get_market_context_from_data_agent()

# 2. Portfolio Agent processes data and creates allocation
portfolio_decision = await coral_client.invoke_agent(
    target_agent="portfolio_agent",
    method="optimize_portfolio",
    parameters={"market_data": market_data, "risk_profile": "moderate"}
)

# 3. Cross-validate with multiple agents
validation = await coral_client.cross_validate_decision(
    decision=portfolio_decision,
    validators=["data_agent", "planner_agent"]
)

# 4. Generate explanation for client
explanation = await coral_client.invoke_agent(
    target_agent="explainer_agent",
    method="explain_decision",
    parameters={
        "action": portfolio_decision,
        "context": {"market_data": market_data, "validation": validation}
    }
)
```

## Monitoring and Debugging

### Health Checks

Monitor agent network health:

```bash
# Check overall system health
curl http://localhost:8000/api/v1/coral/status

# Check individual agent health
curl http://localhost:8000/api/v1/coral/health/data_agent

# Check Coral Server status
curl http://localhost:5555/health
```

### Debugging Agent Interactions

Use logging to trace agent communications:

```python
logger.info(f"🚀 AGENT INVOCATION: {agent_id} → {target_agent}")
logger.info(f"   🎯 Method: {method}")
logger.info(f"   📦 Parameters: {parameters}")
```

### Common Issues and Solutions

**Agent Not Found**:
- Check agent registration: `await coral_client.discover_agents()`
- Verify agent is running and healthy

**Connection Timeout**:
- Check network connectivity to Coral Server
- Verify agent endpoints are accessible

**Method Not Implemented**:
- Check agent capabilities list
- Ensure target method exists on agent

## Best Practices

1. **Register Early**: Register agents immediately after startup
2. **Handle Failures**: Always implement fallback responses
3. **Monitor Health**: Regularly check agent network health
4. **Validate Inputs**: Validate parameters before agent calls
5. **Log Interactions**: Log all agent communications for debugging
6. **Use Timeouts**: Set appropriate timeouts for all agent calls

## Optional: Coral Studio Integration

Connect your Neural Capital AI agents to Coral Studio for visual monitoring and orchestration.

### What Coral Studio Provides

- **Visual Dashboard**: See all your agents working together
- **Agent Network**: Connect with other financial agents
- **Real-time Monitoring**: Watch your agents in action
- **Easy Orchestration**: Drag-and-drop workflows

Your agents are now part of the Coral ecosystem! 🌊

The Coral Protocol enables a decentralized agent network where each agent can discover, invoke, and validate decisions with other agents while maintaining trust and transparency through blockchain verification.