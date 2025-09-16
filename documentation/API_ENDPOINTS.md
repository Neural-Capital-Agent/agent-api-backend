# Neural Capital Financial Agents API - Complete Endpoint Reference

This document provides a comprehensive reference for all API endpoints in the enhanced Financial Agents API.

## 🚀 API Overview

**Base URL**: `http://localhost:8000`
**API Version**: `v2.0.0`
**Documentation**: `/docs` (Swagger UI) | `/redoc` (ReDoc)

## 📊 System Endpoints

### Root Information
```http
GET /
```
Returns comprehensive API information including available agents, features, and endpoint links.

### Health Checks
```http
GET /health                    # System-wide health check
GET /rate-limit/health        # Rate limiting health
GET /api/v1/agents/health     # All agents health
GET /api/v1/llm/health        # LLM services health
```

### API Information
```http
GET /info                     # Detailed API capabilities and statistics
```

## 🏛️ Core API Endpoints

### User Management (`/api/v1/user/`)
```http
GET    /api/v1/user/          # List users
POST   /api/v1/user/          # Create user
POST   /api/v1/user/login     # User login
```

### Stock Data (`/api/v1/stocks/`)
```http
GET    /api/v1/stocks/        # Get all watchlist stocks
GET    /api/v1/stocks/{symbol} # Get specific stock data
```

### Economic Data (`/api/v1/economy/`)
```http
GET    /api/v1/economy/       # Get macro economic indicators
```

### Trading (`/api/v1/alpaca/`)
```http
# Alpaca trading endpoints (existing functionality)
```

## 🤖 Financial Agents Endpoints (`/api/v1/agents/`)

### Data Agent - Market Data & Analysis

#### Market Data
```http
GET    /api/v1/agents/data/market/{ticker}    # Single ticker data
GET    /api/v1/agents/data/market            # All universe data
```

**Example Response**:
```json
{
  "success": true,
  "agent": "data_agent",
  "ticker": "AAPL",
  "data": {
    "symbol": "AAPL",
    "price": 175.23,
    "previous_close": 174.50,
    "change": 0.73,
    "change_percent": 0.42,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Macro Economic Data
```http
GET    /api/v1/agents/data/macro/{indicator}  # FRED economic data
```

**Available Indicators**: `CPI`, `2Y_TREASURY`, `10Y_TREASURY`, `FED_FUNDS_RATE`, `UNEMPLOYMENT`, `VIX`, `PMI`, `DXY`

#### Volatility & Technical Analysis
```http
GET    /api/v1/agents/data/volatility         # VIX and volatility indicators
GET    /api/v1/agents/data/technical/{ticker} # Technical indicators (SMA, RSI, MACD)
```

#### Health Check
```http
GET    /api/v1/agents/data/health            # Data sources health
```

### Portfolio Agent - Optimization & Rebalancing

#### Portfolio Building
```http
POST   /api/v1/agents/portfolio/build
Content-Type: application/json

{
  "risk_level": 3,
  "goal": "retirement planning",
  "constraints": {
    "max_single_position": 0.4,
    "exclude_crypto": false
  }
}
```

**Response**:
```json
{
  "success": true,
  "agent": "portfolio_agent",
  "portfolio": {
    "id": "portfolio-uuid",
    "risk_level": 3,
    "allocations": {
      "SPY": 0.40,
      "BND": 0.30,
      "QQQ": 0.20,
      "GLD": 0.10
    },
    "expected_return": 0.08,
    "volatility": 0.12
  }
}
```

#### Portfolio Rebalancing
```http
POST   /api/v1/agents/portfolio/rebalance
Content-Type: application/json

{
  "current_portfolio": {
    "allocations": {"SPY": 0.6, "BND": 0.4}
  },
  "signals": {
    "yield_curve_inversion": true,
    "volatility_spike": false
  }
}
```

### Planner Agent - Goal Parsing & Strategy

#### Goal Parsing
```http
POST   /api/v1/agents/planner/parse-goal
Content-Type: application/json

{
  "goal_text": "I want to save $500k for retirement in 25 years. I'm 40 years old and have moderate risk tolerance."
}
```

**Response**:
```json
{
  "success": true,
  "agent": "planner_agent",
  "parsed_goal": {
    "goal_type": "RETIREMENT",
    "time_horizon": 25,
    "amount": 500000,
    "current_age": 40
  }
}
```

#### Strategy Generation
```http
POST   /api/v1/agents/planner/create-strategy
POST   /api/v1/agents/planner/glide-path
POST   /api/v1/agents/planner/create-plan
```

### Explainability Agent - Plain English Explanations

#### Decision Explanations
```http
POST   /api/v1/agents/explainer/explain-decision
Content-Type: application/json

{
  "action": {
    "type": "rebalancing",
    "reason": "yield curve inversion detected"
  },
  "context": {
    "market_regime": "elevated_volatility"
  }
}
```

#### Jargon Translation
```http
POST   /api/v1/agents/explainer/translate-jargon
Content-Type: application/json

{
  "technical_text": "The portfolio's duration risk increased due to yield curve inversion and credit spread widening."
}
```

#### Financial Term Definitions
```http
GET    /api/v1/agents/explainer/jargon-definition/{term}
GET    /api/v1/agents/explainer/jargon-definition/duration_risk
```

#### Risk Level Explanations
```http
POST   /api/v1/agents/explainer/risk-explanation
Content-Type: application/json

{
  "risk_level": "aggressive"
}
```

### Multi-Agent Workflows

#### Complete Financial Analysis
```http
POST   /api/v1/agents/workflow/complete-analysis
Content-Type: application/json

{
  "goal_text": "Save for house down payment of $100k in 5 years",
  "user_profile": {
    "age": 28,
    "income": 75000,
    "risk_tolerance": 2,
    "investment_experience": "beginner"
  },
  "current_portfolio": null
}
```

**This workflow runs**:
1. Goal parsing (Planner Agent)
2. Strategy generation (Planner Agent)
3. Portfolio building (Portfolio Agent)
4. Market context analysis (Data Agent)
5. Plain English explanation (Explainability Agent)

## 🧠 LLM Operations (`/api/v1/llm/`)

### Natural Language Processing
```http
POST   /api/v1/llm/parse-goal           # Parse financial goals (1 credit)
POST   /api/v1/llm/explain-decision     # Explain decisions (2 credits)
POST   /api/v1/llm/create-plan          # Investment planning (3 credits)
POST   /api/v1/llm/translate-jargon     # Jargon translation (1 credit)
POST   /api/v1/llm/validate-signals     # Market signal validation (2 credits)
```

### Rate Limit Management
```http
GET    /api/v1/llm/usage/{user_id}      # User usage statistics
POST   /api/v1/llm/set-tier             # Update user tier (admin)
POST   /api/v1/llm/add-credits          # Add credits (admin)
POST   /api/v1/llm/reset-limits/{user_id} # Reset limits (admin)
GET    /api/v1/llm/tiers               # Available tiers
GET    /api/v1/llm/analytics/{user_id}  # Usage analytics
```

## 📋 Request/Response Patterns

### Standard Success Response
```json
{
  "success": true,
  "agent": "agent_name",
  "data": { ... },
  "user_id": "user123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": {
    "code": 500,
    "message": "Detailed error message",
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/api/v1/agents/data/market/INVALID",
    "method": "GET"
  }
}
```

### Rate Limit Response (429)
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after_seconds": 60,
  "current_usage": {
    "daily": 50,
    "hourly": 10,
    "minute": 3,
    "credits": 0
  },
  "limits": {
    "daily": 50,
    "hourly": 10,
    "minute": 3,
    "tier": "basic"
  }
}
```

## 🔒 Authentication & Rate Limiting

### Authentication
```http
Authorization: Bearer <jwt_token>
```

### Rate Limiting Headers
```http
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 1672531200
X-LLM-Credits: 75
X-User-Tier: basic
```

### User Tiers

| Tier | Daily | Hourly | Per Minute | LLM Credits |
|------|-------|--------|------------|-------------|
| Basic | 50 | 10 | 3 | 100 |
| Premium | 200 | 50 | 10 | 500 |
| Enterprise | 1000 | 200 | 50 | 2000 |

## 📈 Usage Examples

### Complete Workflow Example

1. **Parse Goal**:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/planner/parse-goal" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"goal_text": "Save $100k for house in 5 years"}'
```

2. **Build Portfolio**:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/portfolio/build" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"risk_level": 3, "goal": "house_down_payment"}'
```

3. **Get Market Context**:
```bash
curl "http://localhost:8000/api/v1/agents/data/market" \
  -H "Authorization: Bearer <token>"
```

4. **Explain Decision**:
```bash
curl -X POST "http://localhost:8000/api/v1/agents/explainer/explain-decision" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action": {"type": "portfolio_creation"}, "context": {}}'
```

## 🔍 Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid token |
| 403 | Forbidden - Insufficient permissions |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - System error |
| 503 | Service Unavailable - External service down |

## 📞 Support

- **Documentation**: `/docs` or `/redoc`
- **Health Checks**: `/health`, `/rate-limit/health`
- **Support Email**: api-support@neural-capital.com
- **API Info**: `/info` endpoint

The API provides comprehensive financial agent capabilities with proper rate limiting, error handling, and extensive documentation through auto-generated OpenAPI specifications.