# Coral Studio Integration Setup

This guide explains how to make your Neural Capital agents visible and accessible in Coral Studio for orchestration and monitoring.

## Overview

Your Neural Capital agents are now configured for Coral Studio integration with the following components:

- **4 Financial Agents**: Data, Portfolio, Planner, and Explainability agents
- **Coral Registry Service**: Manages agent registration with Coral Server
- **API Endpoints**: RESTful APIs for Coral Studio integration
- **Automatic Registration**: Agents register automatically on startup

## Quick Start

### 1. Environment Configuration

Add these environment variables to your `.env` file:

```bash
# Coral Protocol Configuration
CORAL_SERVER_URL=http://localhost:5555
CORAL_API_BASE_URL=http://localhost:8000
```

### 2. Start Coral Server

Ensure Coral Server is running at the configured URL:

```bash
# Default Coral Server location
http://localhost:5555
```

### 3. Start Your API Server

```bash
python app.py
```

The agents will automatically register with Coral Server during startup.

### 4. Verify Integration

Run the test script to verify everything is working:

```bash
python test_coral_integration.py
```

## API Endpoints

Your agents are now accessible through these Coral-specific endpoints:

### Registration & Status
- `POST /api/v1/coral/register` - Register all agents with Coral Server
- `GET /api/v1/coral/status` - Get agent registry status
- `GET /api/v1/coral/studio-config` - Get Coral Studio configuration

### Discovery & Health
- `GET /api/v1/coral/discover` - Discover agents in Coral network
- `GET /api/v1/coral/health/{agent_id}` - Check specific agent health
- `GET /api/v1/coral/network-health` - Check entire network health

### Capabilities
- `GET /api/v1/coral/capabilities` - List all agent capabilities

## Agent Configuration

Your agents are configured with the following capabilities:

### Data Agent (`data_agent`)
- **Type**: `data_provider`
- **Capabilities**:
  - Real-time market data
  - Macro economic indicators
  - Market context analysis
  - Signal validation
  - Asset universe data

### Portfolio Agent (`portfolio_agent`)
- **Type**: `portfolio_optimizer`
- **Capabilities**:
  - Portfolio optimization
  - Risk-based allocation
  - Dynamic rebalancing
  - Performance analytics
  - Backtest analysis

### Planner Agent (`planner_agent`)
- **Type**: `financial_planner`
- **Capabilities**:
  - Goal parsing
  - Strategy generation
  - Lifecycle planning
  - Natural language processing
  - Investment planning

### Explainability Agent (`explainability_agent`)
- **Type**: `explanation_generator`
- **Capabilities**:
  - Decision explanation
  - Jargon translation
  - Risk communication
  - Plain English conversion
  - Decision rationale

## Coral Studio Setup

### 1. Open Coral Studio

Navigate to your Coral Studio interface and ensure it's connected to your Coral Server.

### 2. Configure Session

Use the configuration from `/api/v1/coral/studio-config`:

```json
{
  "coral_server": {
    "url": "http://localhost:5555"
  },
  "api_server": {
    "url": "http://localhost:8000"
  },
  "agents": [
    {
      "id": "data_agent",
      "type": "data_provider",
      "endpoint": "http://localhost:8000/api/v1/agents/data",
      "capabilities": ["real_time_market_data", "macro_economic_indicators", ...]
    },
    // ... other agents
  ]
}
```

### 3. Verify Agent Visibility

Your agents should now appear in Coral Studio with status indicators:
- **Listening**: Agent is connected and waiting for commands
- **Busy**: Agent is processing a request
- **Disconnected**: Agent is not reachable

## Testing & Verification

### Manual Testing

1. **Check Registration Status**:
   ```bash
   curl http://localhost:8000/api/v1/coral/status
   ```

2. **Discover Agents**:
   ```bash
   curl http://localhost:8000/api/v1/coral/discover
   ```

3. **Check Agent Health**:
   ```bash
   curl http://localhost:8000/api/v1/coral/health/data_agent
   ```

### Automated Testing

Run the comprehensive test suite:

```bash
python test_coral_integration.py
```

## Troubleshooting

### Agents Not Visible in Coral Studio

1. **Check Coral Server Connection**:
   - Verify Coral Server is running at `CORAL_SERVER_URL`
   - Check network connectivity

2. **Verify Agent Registration**:
   ```bash
   curl http://localhost:8000/api/v1/coral/status
   ```

3. **Check Agent Health**:
   - Ensure all agents report "healthy" status
   - Verify API endpoints are accessible

### Registration Failures

1. **Check Environment Variables**:
   - Verify `CORAL_SERVER_URL` is correct
   - Ensure `CORAL_API_BASE_URL` matches your API server

2. **Network Issues**:
   - Confirm Coral Server is reachable
   - Check firewall settings

3. **Re-register Manually**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/coral/register
   ```

### Agent Status Issues

1. **Check Individual Agent Health**:
   ```bash
   curl http://localhost:8000/api/v1/coral/health/data_agent
   curl http://localhost:8000/api/v1/coral/health/portfolio_agent
   curl http://localhost:8000/api/v1/coral/health/planner_agent
   curl http://localhost:8000/api/v1/coral/health/explainability_agent
   ```

2. **Review Agent Logs**:
   - Check application logs for agent-specific errors
   - Look for Coral Protocol connection issues

## Advanced Configuration

### Custom Coral Server URL

To use a different Coral Server:

```bash
export CORAL_SERVER_URL=http://your-coral-server:5555
```

### Custom API Base URL

If your API runs on a different port/host:

```bash
export CORAL_API_BASE_URL=http://your-api-server:8000
```

### Agent-Specific Configuration

Agents can be individually configured in `agent/coral_registry.py` by modifying the `_get_agent_configurations()` method.

## Integration Examples

### Basic Agent Orchestration

Once visible in Coral Studio, you can orchestrate your agents for complex financial workflows:

1. **Data Collection**: Use Data Agent to gather market data
2. **Portfolio Analysis**: Use Portfolio Agent to analyze current allocations
3. **Goal Planning**: Use Planner Agent to interpret user goals
4. **Decision Explanation**: Use Explainability Agent to explain recommendations

### Multi-Agent Workflows

Create workflows that span multiple agents:
- Market analysis → Portfolio optimization → Goal alignment → Decision explanation

## Support

For issues with Coral Studio integration:

1. Check the logs in your application
2. Run the test script: `python test_coral_integration.py`
3. Verify all endpoints are accessible
4. Ensure Coral Server is running and reachable

Your Neural Capital agents are now ready for Coral Studio! 🌊✨