# Neural Capital API Guide

Quick reference for all API endpoints in your Financial Agents system.

## Getting Started

**Base URL**: `http://localhost:8000`
**Documentation**: Visit `/docs` for interactive API explorer

## Basic System Endpoints

### Check if everything is working
```http
GET /health          # Is the system running?
GET /info           # What can the API do?
```

## Core Data Endpoints

### Users
```http
GET  /api/v1/user/           # List all users
POST /api/v1/user/           # Create new user
POST /api/v1/user/login      # Login user
```

### Stock Market Data
```http
GET /api/v1/stocks/          # Get watchlist stocks
GET /api/v1/stocks/{symbol}  # Get specific stock (e.g., AAPL)
```

### Economic Data
```http
GET /api/v1/economy/         # Get economic indicators (GDP, inflation, etc.)
```

## AI Financial Agents

These are your smart financial assistants that analyze data and make recommendations.

### 📊 Data Agent - Gets Market Information

```http
GET /api/v1/agents/data/market/{ticker}    # Get price for one stock (e.g., AAPL)
GET /api/v1/agents/data/market            # Get data for all tracked stocks
GET /api/v1/agents/data/macro/{indicator} # Get economic data (CPI, unemployment, etc.)
GET /api/v1/agents/data/volatility        # Get market fear index (VIX)
```

**What you get back:**
```json
{
  "success": true,
  "ticker": "AAPL",
  "price": 175.23,
  "change": 0.73,
  "change_percent": 0.42
}
```

### 💼 Portfolio Agent - Builds Investment Portfolios

```http
POST /api/v1/agents/portfolio/build      # Create a new portfolio
POST /api/v1/agents/portfolio/rebalance  # Adjust existing portfolio
```

**Create a portfolio:** Send your risk level (1-5) and goals
```json
{
  "risk_level": 3,
  "goal": "retirement planning"
}
```

**Get back:** Recommended investments with percentages
```json
{
  "allocations": {
    "SPY": 0.40,    // 40% S&P 500
    "BND": 0.30,    // 30% Bonds
    "QQQ": 0.20,    // 20% Tech stocks
    "GLD": 0.10     // 10% Gold
  },
  "expected_return": 0.08,
  "risk": 0.12
}
```

### 🎯 Planner Agent - Understands Your Financial Goals

```http
POST /api/v1/agents/planner/parse-goal      # Turn your goal into a plan
POST /api/v1/agents/planner/create-strategy # Create investment strategy
POST /api/v1/agents/planner/create-plan     # Complete financial plan
```

**Tell it your goal:** In plain English
```json
{
  "goal_text": "I want to save $500k for retirement in 25 years. I'm 40 years old."
}
```

**Get back:** Structured plan
```json
{
  "goal_type": "RETIREMENT",
  "time_horizon": 25,
  "target_amount": 500000,
  "current_age": 40
}
```

### 💬 Explainer Agent - Translates Finance Jargon

```http
POST /api/v1/agents/explainer/explain-decision            # Why did we make this choice?
POST /api/v1/agents/explainer/translate-jargon            # Turn jargon into plain English
GET  /api/v1/agents/explainer/jargon-definition/{term}    # What does this term mean?
```

**Example:** Turn complex finance speak into simple language
```json
{
  "technical_text": "Duration risk increased due to yield curve inversion"
}
```
↓ Becomes ↓
```
"Bond prices may fall more than usual because interest rates are acting strangely"
```

## Complete Workflows

### 🔄 All-in-One Financial Analysis
```http
POST /api/v1/agents/workflow/complete-analysis
```

**Send:** Your goal and profile
```json
{
  "goal_text": "Save $100k for house in 5 years",
  "user_profile": {
    "age": 28,
    "income": 75000,
    "risk_tolerance": 2
  }
}
```

**Get:** Complete financial plan using all 4 agents working together

## Team Workflows (CrewAI)

Multiple agents working as a team for complex analysis.

### 🚀 Quick Commands
```http
POST /api/v1/crew/market-analysis      # Analyze market trends
POST /api/v1/crew/portfolio-advisory   # Complete investment advice
POST /api/v1/crew/quick-advice         # Quick financial questions
```

### 📋 Management
```http
GET /api/v1/crew/status                # Is the team working?
GET /api/v1/crew/health                # Team health check
```

**Example - Get Market Analysis:**
```json
{
  "symbols": ["SPY", "QQQ", "BND"]
}
```

**Get back:** Professional market report from the team

## Advanced Features

### 🌊 Coral Protocol - Agent Network
```http
GET  /api/v1/coral/status               # Connection status
POST /api/v1/coral/register             # Join the network
GET  /api/v1/coral/agents               # See other agents
GET  /api/v1/coral/studio               # Visual interface
```

### 🧠 Direct LLM Access
```http
POST /api/v1/llm/parse-goal             # Parse goals directly
POST /api/v1/llm/explain-decision       # Get explanations
POST /api/v1/llm/create-plan            # Generate plans
```

## Rate Limits & Authentication

### 🔐 How to Connect
Add this header to your requests:
```http
Authorization: Bearer your-jwt-token
```

### 🚦 Usage Limits
| Plan | Daily Requests | AI Credits |
|------|---------------|------------|
| Basic | 50 | 100 |
| Premium | 200 | 500 |
| Enterprise | 1000 | 2000 |

### ✅ Success Response
```json
{
  "success": true,
  "data": { your_results_here }
}
```

### ❌ Error Response
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Try again in 60 seconds."
}
```

## Quick Example

**Goal:** Get Apple stock price and build a retirement portfolio

```bash
# 1. Get Apple stock data
curl "http://localhost:8000/api/v1/agents/data/market/AAPL"

# 2. Build retirement portfolio
curl -X POST "http://localhost:8000/api/v1/agents/portfolio/build" \
  -H "Content-Type: application/json" \
  -d '{"risk_level": 3, "goal": "retirement"}'
```

## Need Help?

- **Interactive Docs**: Visit `/docs` for a playground
- **System Status**: Check `/health`
- **Full API Info**: Visit `/info`

That's it! Your Neural Capital AI agents are ready to help with financial decisions. 🚀