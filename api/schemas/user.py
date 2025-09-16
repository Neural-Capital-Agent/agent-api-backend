from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: str
    street_address: str
    city: str
    state: str
    postal_code: str
    given_name: str
    family_name: str
    date_of_birth: str
    country_of_citizenship: str
    country_of_birth: str
    tax_id: str
    contact_given: str
    contact_family: str
    contact_email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserEmail(BaseModel):
    email: EmailStr


class LLMUsageStats(BaseModel):
    """LLM usage statistics for a user"""
    daily_requests: int = 0
    hourly_requests: int = 0
    minute_requests: int = 0
    total_requests: int = 0
    llm_credits: int = 100
    credits_used: int = 0
    tier: str = "basic"
    last_request: Optional[datetime] = None
    daily_reset: Optional[datetime] = None
    hourly_reset: Optional[datetime] = None


class UserRateLimit(BaseModel):
    """Rate limit configuration for a user"""
    user_id: str
    tier: str = "basic"
    daily_limit: int = 50
    hourly_limit: int = 10
    minute_limit: int = 3
    llm_credits: int = 100
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserUsageResponse(BaseModel):
    """Response model for user usage information"""
    user_id: str
    current_usage: Dict[str, int]
    limits: Dict[str, int]
    utilization: Dict[str, float]
    tier: str
    credits_remaining: int
    next_reset: Optional[Dict[str, datetime]] = None


class UpdateUserTier(BaseModel):
    """Request to update user tier"""
    user_id: str
    new_tier: str
    additional_credits: Optional[int] = 0


class AddCreditsRequest(BaseModel):
    """Request to add credits to user"""
    user_id: str
    credits: int
    reason: Optional[str] = "manual_addition"


class RateLimitStatus(BaseModel):
    """Rate limit status response"""
    allowed: bool
    user_id: str
    endpoint: str
    cost: int
    retry_after: Optional[float] = None
    current_usage: Dict[str, int]
    limits: Dict[str, int]
    message: Optional[str] = None


class LLMEndpointUsage(BaseModel):
    """Usage statistics for a specific LLM endpoint"""
    endpoint: str
    count: int
    total_time: float
    average_time: float
    last_used: Optional[datetime] = None


class UserLLMAnalytics(BaseModel):
    """Comprehensive LLM usage analytics for a user"""
    user_id: str
    tier: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_credits_used: int
    credits_remaining: int
    endpoints_usage: Dict[str, LLMEndpointUsage]
    peak_usage_hour: Optional[int] = None
    average_requests_per_day: float = 0.0
    last_active: Optional[datetime] = None

