import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from utils.rate_limiter import llm_rate_limiter, rate_limit_decorator
from ..shared.config import config

logger = logging.getLogger(__name__)

class MistralLLMClient:
    """
    Client for interacting with Mistral LLM via aimlapi.com
    Handles natural language processing tasks for financial agents.
    Uses OpenAI-compatible API endpoint.
    """

    def __init__(self, 
                 api_key: Optional[str] = None, 
                 base_url: str = "https://api.aimlapi.com/v1", 
                 max_tokens: int = 2048):
        self.api_key = api_key or os.getenv("AI_ML_API_KEY")  # Match your CrewAI setup
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None
        self.model = "mistralai/Mistral-7B-Instruct-v0.3"  # Match your CrewAI setup
        self.max_tokens = max_tokens
        self.provider = "openai"  # OpenAI-compatible API

        if not self.api_key:
            logger.warning("No API key provided for Mistral LLM client. Set AI_ML_API_KEY environment variable.")

    def _serialize_for_json(self, obj):
        """Helper method to serialize objects containing Enums for JSON"""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                if hasattr(value, 'value'):  # Handle Enum objects
                    result[key] = value.value
                else:
                    result[key] = value
            return result
        elif hasattr(obj, 'value'):  # Handle direct Enum
            return obj.value
        else:
            return obj

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def _ensure_client(self):
        """Ensure httpx client is available"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0
            )

    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Send chat completion request to Mistral

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Response from Mistral API
        """
        try:
            await self._ensure_client()

            if not self.api_key:
                raise ValueError("API key is required for Mistral LLM client")

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or self.max_tokens,  # Use default from config
                "stream": False
            }

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )

            if response.status_code != 200:
                error_text = response.text if hasattr(response, 'text') else str(response.content)
                logger.error(f"Mistral API error {response.status_code}: {error_text}")
                raise Exception(f"Mistral API error: {response.status_code} - {error_text}")

            return response.json()

        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise

    @rate_limit_decorator(llm_rate_limiter, endpoint="llm_parse", cost=1)
    async def parse_financial_goal(self, goal_text: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Parse natural language financial goal into structured data

        Args:
            goal_text: Natural language goal description
            user_id: User identifier for rate limiting

        Returns:
            Structured goal parameters
        """
        try:
            system_prompt = """You are a financial planning assistant. Parse the user's financial goal and extract:
                1. goal_type: one of "retirement", "house_down_payment", "emergency_fund", "child_education", "general_savings"
                2. target_amount: numerical value (if mentioned)
                3. time_horizon: years (if mentioned)
                4. current_age: age (if mentioned)
                5. confidence: your confidence in the parsing (0-1)

                Respond only with valid JSON format. If information is missing, use null for that field.
            """

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parse this financial goal: '{goal_text}'"}
            ]

            response = await self.chat_completion(messages, temperature=0.3, max_tokens=500)

            # Extract the content from response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")

            # Try to parse as JSON
            try:
                parsed_goal = json.loads(content)
                return parsed_goal
            except json.JSONDecodeError:
                # Fallback: extract JSON from content if it's embedded in text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_goal = json.loads(json_match.group())
                    return parsed_goal
                else:
                    raise ValueError("Could not parse JSON from LLM response")

        except Exception as e:
            logger.error(f"Error parsing financial goal: {e}")
            # Return configuration-based fallback response
            fallback = config.get_fallback("mistral_client", "goal_parsing")
            fallback["error"] = str(e)
            return fallback

    @rate_limit_decorator(llm_rate_limiter, endpoint="llm_explain", cost=2)
    async def explain_financial_decision(self, action: Dict[str, Any], context: Dict[str, Any], user_id: str = "anonymous") -> str:
        """
        Generate plain English explanation for a financial decision

        Args:
            action: Dictionary containing action details
            context: Market and portfolio context
            user_id: User identifier for rate limiting

        Returns:
            Plain English explanation
        """
        try:
            system_prompt = """You are a financial advisor who explains investment decisions in simple, clear language.
Avoid jargon and technical terms. Explain decisions in terms of:
1. What action was taken
2. Why it was necessary
3. What market conditions influenced it
4. What this means for the investor

Keep explanations under 200 words and use conversational language."""

            action_type = action.get('type', 'investment decision')
            action_reason = action.get('reason', 'portfolio optimization')
            market_conditions = context.get('market_data', {}).get('market_regime', 'normal conditions')

            user_message = f"""Explain this investment decision:
Action: {action_type}
Reason: {action_reason}
Market conditions: {market_conditions}
Additional context: {json.dumps(context, indent=2)}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            response = await self.chat_completion(messages, temperature=0.5, max_tokens=300)

            explanation = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return explanation.strip()

        except Exception as e:
            logger.error(f"Error explaining financial decision: {e}")
            return f"Investment decision made due to {action.get('reason', 'current market conditions')}. This adjustment helps maintain your portfolio's target risk level and expected returns."

    @rate_limit_decorator(llm_rate_limiter, endpoint="llm_plan", cost=3)
    async def create_investment_plan(self, goal: Dict[str, Any], strategy: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Create detailed investment plan based on goal and strategy

        Args:
            goal: Parsed goal parameters
            strategy: Investment strategy details
            user_id: User identifier for rate limiting

        Returns:
            Detailed investment plan
        """
        try:
            system_prompt = """You are a financial planner creating investment plans. Based on the goal and strategy provided, create a detailed plan with:
1. monthly_contribution: recommended monthly investment amount
2. asset_allocation: percentage breakdown by asset class
3. milestones: key checkpoints and timeline
4. risk_considerations: important risks to consider

Respond in JSON format only."""

            # Safely serialize goal and strategy
            try:
                goal_json = json.dumps(goal, default=self._serialize_for_json, indent=2)
            except:
                goal_json = str(goal)

            try:
                strategy_json = json.dumps(strategy, default=self._serialize_for_json, indent=2)
            except:
                strategy_json = str(strategy)

            user_message = f"""Create an investment plan for:
Goal: {goal_json}
Strategy: {strategy_json}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            response = await self.chat_completion(messages, temperature=0.4, max_tokens=800)

            content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")

            try:
                plan = json.loads(content)
                return plan
            except json.JSONDecodeError:
                # Fallback parsing
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                    return plan
                else:
                    raise ValueError("Could not parse plan JSON")

        except Exception as e:
            logger.error(f"Error creating investment plan: {e}")
            # Return configuration-based fallback plan
            fallback = config.get_fallback("mistral_client", "investment_plan")
            fallback["error"] = str(e)
            return fallback

    @rate_limit_decorator(llm_rate_limiter, endpoint="llm_translate", cost=1)
    async def translate_financial_jargon(self, technical_text: str, user_id: str = "anonymous") -> str:
        """
        Convert financial jargon to plain English

        Args:
            technical_text: Text containing financial jargon
            user_id: User identifier for rate limiting

        Returns:
            Plain English translation
        """
        try:
            system_prompt = """You are a financial translator who converts complex financial terms and concepts into simple, everyday language that anyone can understand.
Replace technical terms with clear explanations while maintaining the original meaning.
Keep the same structure and flow as the original text."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate this financial text to plain English: {technical_text}"}
            ]

            response = await self.chat_completion(messages, temperature=0.3, max_tokens=600)

            translation = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return translation.strip() if translation else technical_text

        except Exception as e:
            logger.error(f"Error translating jargon: {e}")
            return technical_text

    @rate_limit_decorator(llm_rate_limiter, endpoint="llm_validate", cost=2)
    async def validate_market_signals(self, signals: Dict[str, Any], market_data: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
        """
        Use LLM to validate and interpret market signals

        Args:
            signals: Market signals to validate
            market_data: Current market data
            user_id: User identifier for rate limiting

        Returns:
            Validation results with confidence scores
        """
        try:
            system_prompt = """You are a market analyst who validates trading signals against current market conditions.
Analyze the provided signals and market data, then respond with JSON containing:
1. is_valid: boolean indicating if signals are reasonable
2. confidence: number between 0-1 indicating confidence in validation
3. reasoning: brief explanation of the validation
4. risk_level: "low", "medium", or "high" based on current conditions"""

            # Safely serialize signals and market_data
            try:
                signals_json = json.dumps(signals, default=self._serialize_for_json, indent=2)
            except:
                signals_json = str(signals)

            try:
                market_data_json = json.dumps(market_data, default=self._serialize_for_json, indent=2)
            except:
                market_data_json = str(market_data)

            user_message = f"""Validate these market signals:
Signals: {signals_json}
Market Data: {market_data_json}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            response = await self.chat_completion(messages, temperature=0.3, max_tokens=500)

            content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")

            try:
                validation = json.loads(content)
                return validation
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    validation = json.loads(json_match.group())
                    return validation
                else:
                    raise ValueError("Could not parse validation JSON")

        except Exception as e:
            logger.error(f"Error validating market signals: {e}")
            fallback = config.get_fallback("mistral_client", "signal_validation")
            fallback["error"] = str(e)
            return fallback

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the Mistral LLM client is working properly

        Returns:
            Health status information
        """
        try:
            # Simple test query
            test_messages = [
                {"role": "user", "content": "Respond with 'OK' if you can process this message."}
            ]

            response = await self.chat_completion(test_messages, temperature=0, max_tokens=10)

            if response and response.get("choices"):
                return {
                    "status": "healthy",
                    "model": self.model,
                    "api_endpoint": self.base_url,
                    "test_response": response.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "No valid response received",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_key_configured": bool(self.api_key),
                "timestamp": datetime.now().isoformat()
            }

    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None


# Global instance for use across agents
mistral_client = MistralLLMClient()


# Convenience functions for agents to use with rate limiting
async def parse_goal_with_mistral(goal_text: str, user_id: str = "anonymous") -> Dict[str, Any]:
    """Parse financial goal using Mistral LLM"""
    async with mistral_client:
        return await mistral_client.parse_financial_goal(goal_text, user_id)

async def explain_decision_with_mistral(action: Dict[str, Any], context: Dict[str, Any], user_id: str = "anonymous") -> str:
    """Explain financial decision using Mistral LLM"""
    async with mistral_client:
        return await mistral_client.explain_financial_decision(action, context, user_id)

async def create_plan_with_mistral(goal: Dict[str, Any], strategy: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
    """Create investment plan using Mistral LLM"""
    async with mistral_client:
        return await mistral_client.create_investment_plan(goal, strategy, user_id)

async def translate_jargon_with_mistral(text: str, user_id: str = "anonymous") -> str:
    """Translate financial jargon using Mistral LLM"""
    async with mistral_client:
        return await mistral_client.translate_financial_jargon(text, user_id)

async def validate_signals_with_mistral(signals: Dict[str, Any], market_data: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
    """Validate market signals using Mistral LLM"""
    async with mistral_client:
        return await mistral_client.validate_market_signals(signals, market_data, user_id)