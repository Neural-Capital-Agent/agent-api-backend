# LLM Rate Limiting Implementation

This document explains the comprehensive rate limiting system implemented for LLM usage in the Neural Capital API.

## Overview

The rate limiting system provides:
- **Multi-tier user limits** (basic, premium, enterprise)
- **Multiple time windows** (daily, hourly, per-minute)
- **Credit-based system** for LLM operations
- **Automatic request cost calculation**
- **Real-time usage tracking**
- **Admin management endpoints**

## Architecture

### Core Components

1. **`utils/rate_limiter.py`** - Core rate limiting logic
2. **`api/middleware/rate_limiting.py`** - FastAPI middleware
3. **`api/routes/llm.py`** - LLM endpoints with rate limiting
4. **`api/schemas/user.py`** - Data models for rate limiting
5. **`agent/mistral_client.py`** - Updated with rate limiting decorators

### Rate Limiting Strategy

The system uses a **multi-window approach** with:
- **Sliding window** for minute-based limits
- **Fixed window** for hourly/daily limits
- **Credit system** for LLM operations
- **Per-user state tracking** with automatic reset

## User Tiers

### Basic Tier (Default)
```python
daily_limit = 50      # requests per day
hourly_limit = 10     # requests per hour
minute_limit = 3      # requests per minute
llm_credits = 100     # LLM operation credits
```

### Premium Tier
```python
daily_limit = 200
hourly_limit = 50
minute_limit = 10
llm_credits = 500
```

### Enterprise Tier
```python
daily_limit = 1000
hourly_limit = 200
minute_limit = 50
llm_credits = 2000
```

## LLM Operation Costs

Different LLM operations have different credit costs:

- **Goal Parsing** (`/llm/parse-goal`): 1 credit
- **Jargon Translation** (`/llm/translate-jargon`): 1 credit
- **Decision Explanation** (`/llm/explain-decision`): 2 credits
- **Signal Validation** (`/llm/validate-signals`): 2 credits
- **Investment Planning** (`/llm/create-plan`): 3 credits

## API Endpoints

### LLM Operations

#### Parse Financial Goal
```http
POST /api/v1/llm/parse-goal
Authorization: Bearer <token>
Content-Type: application/json

{
  "goal_text": "I want to save $100k for a house down payment in 5 years"
}
```

**Rate Limit**: 1 credit per request

#### Explain Financial Decision
```http
POST /api/v1/llm/explain-decision
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": {"type": "rebalance", "reason": "market volatility"},
  "context": {"market_data": {...}}
}
```

**Rate Limit**: 2 credits per request

#### Create Investment Plan
```http
POST /api/v1/llm/create-plan
Authorization: Bearer <token>
Content-Type: application/json

{
  "goal": {...},
  "strategy": {...}
}
```

**Rate Limit**: 3 credits per request

### Management Endpoints

#### Get User Usage
```http
GET /api/v1/llm/usage/{user_id}
```

Response:
```json
{
  "user_id": "user123",
  "current_usage": {
    "daily": 25,
    "hourly": 5,
    "minute": 1,
    "credits": 75
  },
  "limits": {
    "daily": 50,
    "hourly": 10,
    "minute": 3
  },
  "utilization": {
    "daily_percent": 50.0,
    "hourly_percent": 50.0,
    "minute_percent": 33.3
  },
  "tier": "basic",
  "credits_remaining": 75
}
```

#### Update User Tier (Admin)
```http
POST /api/v1/llm/set-tier
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "user_id": "user123",
  "new_tier": "premium",
  "additional_credits": 100
}
```

#### Add Credits (Admin)
```http
POST /api/v1/llm/add-credits
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "user_id": "user123",
  "credits": 50,
  "reason": "customer_support_credit"
}
```

## Rate Limit Headers

All responses include rate limiting headers:

```http
X-RateLimit-Limit: 3
X-RateLimit-Remaining: 2
X-RateLimit-Reset: 1672531200
X-LLM-Credits: 75
X-User-Tier: basic
```

## Rate Limit Exceeded Response

When rate limits are exceeded, the API returns:

```http
HTTP 429 Too Many Requests
Retry-After: 60

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
  },
  "user_id": "user123",
  "endpoint": "llm_chat"
}
```

## User Identification

The system identifies users through multiple methods (in priority order):

1. **JWT Token** - `Authorization: Bearer <token>` header
2. **Query Parameter** - `?user_id=user123`
3. **IP Address** - Fallback for anonymous users (`ip_192.168.1.1`)

## Middleware Configuration

The rate limiting middleware is configured in `app.py`:

```python
app.add_middleware(LLMUsageMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    llm_endpoints=["/api/v1/llm/", "/api/v1/agents/", "/api/v1/chat/"],
    default_user_tier="basic"
)
```

## Health Checks

### System Health
```http
GET /rate-limit/health
```

### LLM Service Health
```http
GET /api/v1/llm/health
```

## Implementation Details

### Rate Limiter Class

The `LLMRateLimiter` class manages:
- Per-user state tracking
- Multi-window rate limiting
- Credit management
- Automatic counter resets
- Thread-safe operations (async locks)

### Decorators

Rate limiting is applied via decorators:

```python
@rate_limit_decorator(llm_rate_limiter, endpoint="llm_parse", cost=1)
async def parse_financial_goal(self, goal_text: str, user_id: str = "anonymous"):
    # LLM operation
```

### Middleware Flow

1. **Request arrives** → Extract user ID
2. **Check endpoints** → Determine if rate limiting applies
3. **Calculate cost** → Based on endpoint and method
4. **Check limits** → All time windows + credits
5. **Allow/Deny** → Process or return 429
6. **Add headers** → Include rate limit info in response

## Configuration

### Environment Variables

```bash
# Optional - for enhanced features
AI_ML_API_KEY=your_mistral_api_key
FRED_KEY=your_fred_api_key
```

### Default Settings

- **Anonymous users**: Basic tier with IP-based tracking
- **Authenticated users**: Configurable tiers
- **Rate limit storage**: In-memory (can be extended to Redis)
- **Auto-reset**: Daily/hourly/minute counters reset automatically

## Monitoring and Analytics

The system tracks:
- Request counts per time window
- Credit usage
- Endpoint-specific usage
- Success/failure rates
- Average response times

Future enhancements can include:
- Database persistence
- Historical analytics
- Usage patterns analysis
- Predictive scaling

## Error Handling

The system gracefully handles:
- Middleware errors (continues with request)
- Rate limiter failures (allows request)
- User identification failures (uses anonymous)
- Invalid configurations (falls back to defaults)

## Security Considerations

- Rate limits prevent API abuse
- Credit system prevents unlimited LLM usage
- User identification prevents spoofing (when using JWT)
- Admin endpoints should be properly secured
- Sensitive operations are logged

## Future Enhancements

1. **Redis Backend** - For distributed deployments
2. **Database Persistence** - Historical data and analytics
3. **Dynamic Pricing** - Variable costs based on model/complexity
4. **Burst Allowances** - Temporary limit increases
5. **Custom Rate Limits** - Per-user custom configurations
6. **Webhooks** - Rate limit notifications
7. **Dashboard** - Admin UI for monitoring and management

## Testing

Example usage for testing:

```python
# Test rate limiting
import asyncio
from utils.rate_limiter import llm_rate_limiter, setup_user_tier

async def test_rate_limiting():
    # Setup user
    await setup_user_tier("test_user", "basic")

    # Test requests
    for i in range(5):
        result = await llm_rate_limiter.check_rate_limit("test_user", "llm_parse", 1)
        print(f"Request {i+1}: {'✓' if result['allowed'] else '✗'}")

# Run test
asyncio.run(test_rate_limiting())
```

This comprehensive rate limiting system ensures fair usage of LLM resources while providing flexibility for different user tiers and use cases.