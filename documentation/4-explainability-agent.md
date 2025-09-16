# Explainability Agent Documentation

## Overview

The **Explainability Agent** is responsible for **financial jargon translation and decision rationale generation**. It takes complex financial decisions and technical language from other agents and explains them in plain English, providing context, risk assessments, and historical perspectives to make AI-driven financial advice transparent and accessible to everyday users.

## What the Explainability Agent Does

The Explainability Agent provides comprehensive explanation and translation capabilities:

1. **Decision Explanation**: Converts complex financial decisions into clear, understandable explanations
2. **Jargon Translation**: Translates technical financial terms into plain English
3. **Risk Communication**: Explains investment risks in user-friendly language
4. **Historical Context**: Provides relevant market history and precedents
5. **Multi-Agent Context Integration**: Combines insights from multiple agents for comprehensive explanations
6. **Confidence Assessment**: Evaluates and communicates the reliability of recommendations

## Key Inputs

### 1. Financial Action/Decision
```python
{
    "id": "action_123e4567-e89b-12d3-a456-426614174000",
    "type": "rebalancing",
    "agent_source": "portfolio_agent",
    "parameters": {
        "reason": "volatility_spike",
        "current_allocations": {"SPY": 0.70, "BND": 0.30},
        "target_allocations": {"SPY": 0.60, "BND": 0.35, "GLD": 0.05},
        "macro_signals": ["vix_spike", "yield_curve_flattening"]
    },
    "timestamp": "2024-01-15T14:30:00Z",
    "confidence": 0.87
}
```

### 2. Technical Financial Text
```python
{
    "text": "The yield_curve_inversion and elevated volatility suggest implementing a defensive rebalancing strategy with reduced beta exposure and increased duration hedging through TIPS allocation.",
    "context": "portfolio_recommendation",
    "target_audience": "retail_investor",
    "complexity_level": "beginner"
}
```

### 3. Portfolio Information
```python
{
    "portfolio_id": "portfolio_789a1b2c-3d4e-5f6g-7h8i-9j0k1l2m3n4o",
    "risk_level": 3,
    "allocations": {
        "SPY": 0.50,
        "QQQ": 0.20,
        "BTC-USD": 0.10,
        "BND": 0.20
    },
    "expected_return": 0.085,
    "volatility": 0.145,
    "total_value": 250000
}
```

### 4. Risk Level for Explanation
```python
{
    "risk_level": "aggressive",
    "context": "portfolio_allocation",
    "user_experience": "beginner",
    "explanation_depth": "detailed"
}
```

### 5. Market Context (From Other Agents)
```python
{
    "portfolio_rationale": {
        "reason": "Rebalancing due to macro signal triggers",
        "confidence": 0.82,
        "expected_impact": "2% volatility reduction"
    },
    "market_data": {
        "vix": 28.5,
        "market_regime": "elevated_volatility",
        "yield_curve_spread": -0.15
    },
    "economic_context": {
        "inflation_rate": 0.034,
        "unemployment": 0.037,
        "fed_funds_rate": 0.0525
    }
}
```

## Key Outputs

### 1. Comprehensive Explanation Response
```python
{
    "action_id": "action_123e4567-e89b-12d3-a456-426614174000",
    "explanation": "Your portfolio was adjusted because market fear (measured by the VIX) spiked above 25, which historically indicates increased uncertainty. We reduced your stock exposure from 70% to 60% and added 5% to gold as a safety measure. This change is expected to reduce your portfolio's ups and downs by about 2% while maintaining most of your growth potential.",
    "risk_assessment": "Moderate risk adjustment - some ups and downs expected, but historically recovers within 2-3 years. The current elevated market volatility suggests being more defensive is prudent for medium-term stability.",
    "historical_context": "VIX spikes above 25 historically coincide with market corrections, but markets usually recover within 6 months. Similar volatility events in 2018, 2020, and 2022 saw recovery periods of 3-8 months on average.",
    "confidence_score": 0.82,
    "verification_hash": "a1b2c3d4e5f6789abc123def456",
    "plain_language_summary": "Made your investments a bit safer due to market uncertainty",
    "key_terms_explained": {
        "vix_spike": "A jump in the market fear indicator",
        "rebalancing": "Adjusting your investment mix",
        "volatility": "How much prices move up and down"
    },
    "generated_at": "2024-01-15T14:35:00Z"
}
```

### 2. Jargon Translation
```python
{
    "original_text": "The portfolio exhibits elevated duration risk due to the yield_curve_inversion, requiring tactical rebalancing to optimize the sharpe_ratio while maintaining appropriate beta exposure.",
    "translation": "The portfolio is sensitive to interest rate changes because long-term rates are below short-term rates. We need to adjust the investments to get better risk-adjusted returns while keeping the right amount of market exposure.",
    "translated_terms": {
        "duration_risk": "sensitivity to interest rate changes",
        "yield_curve_inversion": "long-term rates below short-term rates",
        "tactical_rebalancing": "adjusting the investments",
        "sharpe_ratio": "risk-adjusted returns",
        "beta_exposure": "market exposure"
    },
    "complexity_reduction": 0.75,  # 75% reduction in complexity
    "confidence": 0.91,
    "fallback_used": false
}
```

### 3. Risk Warning and Assessment
```python
{
    "risk_category": "moderate",
    "warning_text": "Some ups and downs expected, but historically recovers within 2-3 years. Good for medium-term goals. Additional considerations: Cryptocurrency investments are highly volatile and speculative. High concentration in single asset increases risk.",
    "risk_factors": [
        {
            "factor": "crypto_exposure",
            "level": "high",
            "description": "10% in Bitcoin adds significant volatility",
            "mitigation": "Consider reducing to 5% or less"
        },
        {
            "factor": "concentration_risk",
            "level": "medium",
            "description": "50% in single ETF (SPY) creates concentration",
            "mitigation": "Add international diversification"
        }
    ],
    "suitability_assessment": "Suitable for investors with 5+ year time horizon and moderate risk tolerance",
    "worst_case_scenario": "Could lose 25-30% in severe market downturn",
    "recovery_timeline": "Typically recovers within 18-24 months",
    "generated_at": "2024-01-15T14:35:00Z"
}
```

### 4. Historical Context Response
```python
{
    "event_type": "volatility_spike",
    "historical_precedents": [
        {
            "date": "2020-03-20",
            "vix_level": 82.7,
            "market_decline": -34,
            "recovery_time_days": 126,
            "description": "COVID-19 market crash - sharp decline followed by V-shaped recovery"
        },
        {
            "date": "2018-02-05",
            "vix_level": 50.3,
            "market_decline": -12,
            "recovery_time_days": 89,
            "description": "Inflation fears and rising rates - moderate correction"
        }
    ],
    "typical_pattern": "VIX spikes above 25 historically coincide with market corrections averaging -15%, but markets usually recover within 6 months",
    "current_context": "Current VIX at 28.5 suggests elevated but not extreme fear levels",
    "confidence": 0.88,
    "sources": ["Federal Reserve Economic Data", "CBOE VIX Historical Data"],
    "generated_at": "2024-01-15T14:35:00Z"
}
```

### 5. Market Regime Explanation
```python
{
    "current_regime": "elevated_volatility",
    "plain_explanation": "Markets are more volatile than usual, indicating uncertainty. This typically happens when investors are unsure about economic conditions, policy changes, or market direction.",
    "characteristics": [
        "VIX above 20 but below 30",
        "Increased correlation between asset classes",
        "Higher trading volumes",
        "More frequent price swings"
    ],
    "implications": [
        "More defensive positioning may be appropriate",
        "Diversification becomes more important",
        "Consider reducing position sizes",
        "Focus on quality investments"
    ],
    "typical_duration": "2-6 months",
    "historical_frequency": "Occurs about 25% of the time",
    "confidence": 0.84
}
```

## Core Features

### 1. Comprehensive Financial Jargon Dictionary

The Explainability Agent maintains an extensive dictionary of financial terms with plain English explanations:

#### Core Investment Terms
```python
INVESTMENT_JARGON = {
    "yield_curve_inversion": "When long-term interest rates fall below short-term rates",
    "credit_spreads": "The extra interest risky bonds pay compared to safe government bonds",
    "vix_spike": "When the market fear indicator (VIX) rises sharply",
    "p/e_ratio": "How expensive stocks are compared to their earnings",
    "duration_risk": "How sensitive bond prices are to interest rate changes",
    "market_momentum": "Whether stock prices are trending up or down"
}
```

#### Portfolio Management Terms
```python
PORTFOLIO_JARGON = {
    "volatility": "How much prices move up and down",
    "rebalancing": "Adjusting your investment mix back to target percentages",
    "macro_signals": "Economic indicators that suggest market direction",
    "risk_parity": "Balancing risk equally across different investments",
    "correlation": "How similarly different investments move together"
}
```

#### Performance Metrics
```python
PERFORMANCE_JARGON = {
    "alpha": "Investment returns above what the market provides",
    "beta": "How much an investment moves relative to the overall market",
    "sharpe_ratio": "Risk-adjusted returns (higher is better)",
    "drawdown": "The largest peak-to-trough decline in portfolio value",
    "tracking_error": "How much a portfolio differs from its benchmark"
}
```

### 2. Advanced Jargon Translation Engine

#### Multi-Term Translation
```python
async def translate_jargon(self, technical_text: str):
    """Convert technical financial terms to plain English"""

    try:
        # Primary: Use LLM for context-aware translation
        llm_response = await self.coral_client.invoke_agent("llm_agent", "translate_jargon", {
            "text": technical_text,
            "target_audience": "retail_investor",
            "preserve_meaning": True
        })

        if llm_response.get("translation") and not llm_response.get("error"):
            return {"translation": llm_response["translation"], "method": "llm"}

    except Exception as e:
        logger.warning(f"LLM translation failed: {e}")

    # Fallback: Dictionary-based pattern replacement
    translated_text = technical_text
    translated_terms = {}

    for term, explanation in self.jargon_dictionary.items():
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        if pattern.search(translated_text):
            translated_text = pattern.sub(explanation, translated_text)
            translated_terms[term] = explanation

    return {
        "translation": translated_text,
        "translated_terms": translated_terms,
        "method": "dictionary"
    }
```

#### Context-Aware Translation
```python
def _contextual_translation(self, term: str, context: str):
    """Provide context-specific translations"""

    contextual_definitions = {
        "beta": {
            "portfolio_context": "How much your investments move with the overall market",
            "risk_context": "Your portfolio's sensitivity to market swings",
            "performance_context": "Whether your investments are more or less volatile than the market"
        },
        "duration": {
            "bond_context": "How sensitive your bonds are to interest rate changes",
            "risk_context": "Interest rate risk in your portfolio",
            "timing_context": "How long you need to hold bonds to get expected returns"
        }
    }

    if term in contextual_definitions and context in contextual_definitions[term]:
        return contextual_definitions[term][context]

    return self.jargon_dictionary.get(term, f"Definition for {term} is not available")
```

### 3. Risk Communication System

#### Tiered Risk Templates
```python
RISK_TEMPLATES = {
    "low": {
        "description": "Minimal chance of loss, but growth may be limited. Suitable for near-term goals.",
        "characteristics": ["Very stable", "Predictable returns", "Low growth potential"],
        "time_horizon": "0-3 years",
        "typical_assets": ["Cash", "Short-term bonds", "CDs"]
    },
    "moderate": {
        "description": "Some ups and downs expected, but historically recovers within 2-3 years. Good for medium-term goals.",
        "characteristics": ["Balanced approach", "Moderate volatility", "Steady growth"],
        "time_horizon": "3-7 years",
        "typical_assets": ["Balanced funds", "Mixed portfolios", "Target-date funds"]
    },
    "high": {
        "description": "Significant volatility possible, but higher potential returns over long periods. Best for long-term goals only.",
        "characteristics": ["Higher volatility", "Growth focused", "Requires patience"],
        "time_horizon": "7+ years",
        "typical_assets": ["Stock funds", "Growth ETFs", "Emerging markets"]
    },
    "very_high": {
        "description": "Large swings in value are common. Only suitable for long-term goals with high risk tolerance.",
        "characteristics": ["Extreme volatility", "Speculative", "High return potential"],
        "time_horizon": "10+ years",
        "typical_assets": ["Individual stocks", "Sector bets", "Cryptocurrency"]
    }
}
```

#### Dynamic Risk Assessment
```python
def generate_risk_warning(self, portfolio):
    """Generate comprehensive risk warning based on portfolio composition"""

    risk_factors = []
    base_risk_level = self._assess_base_risk(portfolio)

    # Concentration risk
    max_allocation = max(portfolio.allocations.values()) if portfolio.allocations else 0
    if max_allocation > 0.40:
        risk_factors.append({
            "type": "concentration",
            "severity": "medium",
            "description": "High concentration in single asset increases risk",
            "recommendation": "Consider diversifying across more assets"
        })

    # Cryptocurrency exposure
    crypto_assets = ["BTC-USD", "ETH-USD", "ADA-USD"]
    crypto_exposure = sum(portfolio.allocations.get(asset, 0) for asset in crypto_assets)
    if crypto_exposure > 0:
        risk_factors.append({
            "type": "cryptocurrency",
            "severity": "high",
            "description": "Cryptocurrency investments are highly volatile and speculative",
            "recommendation": f"Consider limiting crypto to 5% or less (currently {crypto_exposure:.1%})"
        })

    # Volatility assessment
    if portfolio.volatility > 0.20:
        risk_factors.append({
            "type": "high_volatility",
            "severity": "high",
            "description": f"Portfolio volatility of {portfolio.volatility:.1%} indicates large price swings",
            "recommendation": "Consider reducing position sizes or adding stable assets"
        })

    return self._format_risk_warning(base_risk_level, risk_factors)
```

### 4. Historical Context Engine

#### Market Event Library
```python
HISTORICAL_EVENTS = {
    "volatility_spikes": [
        {
            "date": "2020-03-16",
            "vix_peak": 82.69,
            "trigger": "COVID-19 pandemic",
            "market_decline": -33.9,
            "recovery_days": 126,
            "lessons": "Swift policy response enabled rapid recovery"
        },
        {
            "date": "2008-11-20",
            "vix_peak": 89.53,
            "trigger": "Financial crisis",
            "market_decline": -56.8,
            "recovery_days": 1826,
            "lessons": "Structural issues take longer to resolve"
        }
    ],
    "yield_curve_inversions": [
        {
            "date": "2019-08-14",
            "spread_low": -0.02,
            "recession_lag_months": 7,
            "market_decline": -33.9,
            "recovery_pattern": "V-shaped due to policy intervention"
        },
        {
            "date": "2000-07-17",
            "spread_low": -0.52,
            "recession_lag_months": 8,
            "market_decline": -49.1,
            "recovery_pattern": "Extended bear market lasting 2.5 years"
        }
    ]
}
```

#### Pattern Recognition and Context
```python
def _provide_historical_context(self, action):
    """Provide relevant historical context for financial actions"""

    action_type = getattr(action, 'action_type', None) or action.get('type', 'unknown')
    action_params = getattr(action, 'parameters', None) or action.get('parameters', {})

    context_patterns = {
        "volatility_spike": {
            "pattern": "VIX spikes above 25 historically coincide with market corrections",
            "typical_decline": "10-15% market decline",
            "recovery_time": "Usually recover within 6 months",
            "precedents": self._get_volatility_precedents()
        },
        "yield_curve_inversion": {
            "pattern": "Yield curve inversions historically signal recession within 12-18 months",
            "typical_decline": "Markets typically decline 20-30%",
            "recovery_time": "Recover within 2-3 years",
            "precedents": self._get_inversion_precedents()
        },
        "credit_stress": {
            "pattern": "Credit spread widening indicates economic stress",
            "typical_impact": "Flight to quality, equity underperformance",
            "recovery_time": "Depends on underlying economic health",
            "precedents": self._get_credit_precedents()
        }
    }

    # Match action parameters to historical patterns
    for signal_type in action_params:
        if signal_type in context_patterns:
            return self._format_historical_context(context_patterns[signal_type])

    return "Historical patterns suggest similar market conditions typically resolve within 6-12 months."
```

### 5. Multi-Agent Context Integration

#### Context Gathering
```python
async def gather_multi_agent_context(self, action):
    """Query all relevant agents for comprehensive decision context"""

    context = {}

    try:
        # Portfolio Agent context
        if action.get("agent_source") == "portfolio_agent":
            context["portfolio_rationale"] = await self.coral_client.invoke_agent(
                "portfolio_agent", "get_decision_rationale",
                {"action_id": action.get("id")}
            )

        # Data Agent context
        context["market_data"] = await self.coral_client.invoke_agent(
            "data_agent", "get_market_context",
            {"timestamp": action.get("timestamp", datetime.now().isoformat())}
        )

        # Planner Agent context (if goal-related)
        if action.get("goal_id"):
            context["planning_context"] = await self.coral_client.invoke_agent(
                "planner_agent", "get_goal_context",
                {"goal_id": action.get("goal_id")}
            )

    except Exception as e:
        logger.warning(f"Failed to gather context from agents: {e}")
        context["context_warning"] = "Limited context available due to agent communication issues"

    return context
```

#### Comprehensive Explanation Generation
```python
async def generate_comprehensive_explanation(self, action, context):
    """Generate detailed explanation using multi-agent context"""

    explanation_components = []

    # Core action description
    action_type = action.get('type', 'financial_action')
    explanation_components.append(f"Action taken: {self._humanize_action_type(action_type)}")

    # Portfolio reasoning
    portfolio_rationale = context.get("portfolio_rationale", {})
    if portfolio_rationale and not portfolio_rationale.get("error"):
        reason = portfolio_rationale.get("reason", "Portfolio optimization")
        explanation_components.append(f"Reason: {reason}")

    # Market context
    market_data = context.get("market_data", {})
    if market_data and not market_data.get("error"):
        market_regime = market_data.get("market_regime", "normal_conditions")
        regime_explanation = self._explain_market_regime(market_regime)
        explanation_components.append(f"Market conditions: {regime_explanation}")

    # Planning context
    planning_context = context.get("planning_context", {})
    if planning_context:
        goal_relevance = planning_context.get("goal_impact", "")
        if goal_relevance:
            explanation_components.append(f"Goal impact: {goal_relevance}")

    # Combine and translate
    full_explanation = " ".join(explanation_components)
    translation_result = await self.translate_jargon(full_explanation)

    return translation_result.get("translation", full_explanation)
```

### 6. Confidence Scoring System

```python
def _calculate_confidence_score(self, context):
    """Calculate explanation confidence based on available context quality"""

    confidence_factors = []

    # Portfolio rationale quality
    portfolio_rationale = context.get("portfolio_rationale", {})
    if portfolio_rationale and not portfolio_rationale.get("error"):
        rationale_confidence = portfolio_rationale.get("confidence", 0.5)
        confidence_factors.append(rationale_confidence * 0.4)  # 40% weight
    else:
        confidence_factors.append(0.2)  # Low confidence without portfolio context

    # Market data availability
    market_data = context.get("market_data", {})
    if market_data and not market_data.get("error"):
        confidence_factors.append(0.8 * 0.3)  # 30% weight
    else:
        confidence_factors.append(0.3 * 0.3)  # Reduced confidence

    # Historical context relevance
    historical_matches = len(context.get("historical_precedents", []))
    historical_confidence = min(historical_matches / 3.0, 1.0)  # Up to 3 precedents
    confidence_factors.append(historical_confidence * 0.2)  # 20% weight

    # Context completeness
    context_completeness = len([k for k, v in context.items() if v and not v.get("error")]) / 5.0
    confidence_factors.append(min(context_completeness, 1.0) * 0.1)  # 10% weight

    return sum(confidence_factors)
```

### 7. Verification and Audit Trail

```python
def create_explanation_audit_trail(self, action, explanation_response):
    """Create comprehensive audit trail for explanations"""

    return {
        "explanation_id": str(uuid.uuid4()),
        "action_id": action.get("id"),
        "original_action": action,
        "explanation_method": explanation_response.get("method", "hybrid"),
        "context_sources": list(explanation_response.get("context", {}).keys()),
        "translation_method": explanation_response.get("translation_method"),
        "confidence_breakdown": explanation_response.get("confidence_factors"),
        "historical_precedents_used": explanation_response.get("precedents", []),
        "risk_factors_identified": explanation_response.get("risk_factors", []),
        "jargon_terms_translated": len(explanation_response.get("translated_terms", {})),
        "verification_hash": explanation_response.get("verification_hash"),
        "generated_at": datetime.now().isoformat(),
        "agent_version": "1.0.0"
    }
```

## Integration with Other Agents

### Portfolio Agent Integration
```python
# Portfolio Agent sends decision to Explainability Agent
async def explain_portfolio_decision(portfolio_decision):
    explanation = await explainability_agent.explain_decision(
        action=portfolio_decision,
        context=await explainability_agent.gather_multi_agent_context(portfolio_decision)
    )
    return explanation
```

### Data Agent Integration
```python
# Get market context for explanations
market_context = await data_agent.get_current_market_regime()
economic_indicators = await data_agent.get_economic_indicators()

# Use context in explanations
explanation_context = {
    "market_regime": market_context,
    "economic_data": economic_indicators
}
```

### Planner Agent Integration
```python
# Explain planning recommendations
planning_explanation = await explainability_agent.translate_jargon(
    "Based on your 30-year time horizon and moderate risk tolerance, we recommend a balanced allocation with 70% equities for growth and 30% bonds for stability."
)
```

## Error Handling and Fallbacks

### LLM Unavailability Handling
```python
async def translate_with_fallback(self, text):
    """Handle LLM service unavailability gracefully"""

    try:
        # Primary: LLM translation
        llm_result = await self.llm_translate(text)
        if llm_result.get("success"):
            return llm_result
    except Exception as e:
        logger.warning(f"LLM translation failed: {e}")

    # Fallback: Dictionary-based translation
    try:
        dictionary_result = self.dictionary_translate(text)
        dictionary_result["fallback_used"] = True
        return dictionary_result
    except Exception as e:
        logger.error(f"Dictionary translation failed: {e}")

    # Ultimate fallback: Return original with warning
    return {
        "translation": text,
        "warning": "Translation services temporarily unavailable",
        "fallback_used": True
    }
```

### Context Availability Handling
```python
def generate_explanation_with_limited_context(self, action, available_context):
    """Generate explanation even with limited context"""

    explanation_quality = "basic"

    if len(available_context) >= 3:
        explanation_quality = "comprehensive"
    elif len(available_context) >= 1:
        explanation_quality = "moderate"

    quality_templates = {
        "comprehensive": "Based on current market conditions and portfolio analysis, {action} because {reasoning}. Historical patterns suggest {context}.",
        "moderate": "The {action} was taken because {reasoning}. This is a {frequency} occurrence in similar market conditions.",
        "basic": "A {action} was implemented to {purpose}. This type of adjustment helps maintain appropriate risk levels."
    }

    return quality_templates[explanation_quality].format(
        action=self._humanize_action(action),
        reasoning=self._extract_basic_reasoning(action),
        context=self._provide_general_context(action),
        frequency=self._assess_frequency(action),
        purpose=self._identify_purpose(action)
    )
```

## Performance and Scalability

### Caching Strategy
```python
EXPLANATION_CACHE_CONFIG = {
    "jargon_translations": {
        "ttl": 86400,  # 24 hours
        "max_entries": 10000
    },
    "risk_assessments": {
        "ttl": 3600,   # 1 hour
        "max_entries": 5000
    },
    "historical_contexts": {
        "ttl": 604800, # 7 days
        "max_entries": 1000
    }
}
```

### Batch Processing
```python
async def batch_explain_actions(self, actions, batch_size=10):
    """Process multiple explanations efficiently"""

    explanations = []

    for i in range(0, len(actions), batch_size):
        batch = actions[i:i + batch_size]

        # Process batch in parallel
        batch_tasks = [
            self.explain_decision(action)
            for action in batch
        ]

        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        explanations.extend(batch_results)

    return explanations
```

This Explainability Agent ensures that complex AI-driven financial decisions are transparent, understandable, and trustworthy for users at all levels of financial sophistication.