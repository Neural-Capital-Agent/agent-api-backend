"""
CrewAI Integration for Neural Capital Agents
Wraps existing agents as CrewAI agents for orchestrated workflows.
Falls back to simple orchestrator if CrewAI is not available.
"""

import logging
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure AI/ML API key for CrewAI (maps to OpenAI)
ai_ml_api_key = os.getenv('AI_ML_API_KEY')
if ai_ml_api_key:
    ##os.environ['OPENAI_API_KEY'] = ai_ml_api_key
    os.environ['AIML_API_KEY'] = ai_ml_api_key
    logger.info("AI-ML-API-Key loaded and configured for CrewAI")
else:
    logger.warning("AI-ML-API-Key not found in environment variables")

# Try to import CrewAI, fallback to simple orchestrator if not available
try:
    from crewai import Agent, Task, Crew, Process ,litellm
    from crewai.tools import BaseTool
    from pydantic import BaseModel, Field
    CREWAI_AVAILABLE = True
    logger.info("CrewAI is available - using full CrewAI functionality")
except ImportError:
    CREWAI_AVAILABLE = False
    logger.info("CrewAI not available - using simple orchestrator fallback")

from ..core.data_agent import DataAgent
from ..core.portfolio_agent import PortfolioAgent
from ..core.planner_agent import PlannerAgent
from ..core.explainability_agent import ExplainabilityAgent

logger = logging.getLogger(__name__)

# ================================
# Custom Tools for Neural Capital (CrewAI-specific)
# ================================

if CREWAI_AVAILABLE:
    class MarketDataTool(BaseTool):
        name: str = "market_data_tool"
        description: str = "Get real-time market data and macro indicators"

        def _run(self, symbol: str = "SPY") -> str:
            """Get market data for a symbol"""
            try:
                data_agent = DataAgent()
                data = data_agent.get_market_data(symbol)
                return f"Market data for {symbol}: Price ${data.get('price', 'N/A')}, Change {data.get('change_percent', 'N/A')}%"
            except Exception as e:
                return f"Error getting market data: {str(e)}"

    class PortfolioOptimizationTool(BaseTool):
        name: str = "portfolio_optimization_tool"
        description: str = "Optimize portfolio allocation based on risk level"

        def _run(self, risk_level: int = 3, goal: str = "retirement") -> str:
            """Build optimized portfolio"""
            try:
                portfolio_agent = PortfolioAgent()
                portfolio = portfolio_agent.build_portfolio(risk_level, goal)
                if 'allocations' in portfolio:
                    allocations = portfolio['allocations']
                    summary = f"Portfolio for risk level {risk_level}: "
                    summary += ", ".join([f"{ticker}: {alloc:.1%}" for ticker, alloc in allocations.items() if alloc > 0])
                    return summary
                return "Portfolio optimization completed"
            except Exception as e:
                return f"Error optimizing portfolio: {str(e)}"

    class GoalPlanningTool(BaseTool):
        name: str = "goal_planning_tool"
        description: str = "Parse financial goals and create investment strategies"

        def _run(self, goal_text: str) -> str:
            """Parse and plan for financial goal"""
            try:
                planner_agent = PlannerAgent()
                parsed_goal = planner_agent.parse_goal(goal_text)
                if 'goal_type' in parsed_goal:
                    return f"Goal identified: {parsed_goal['goal_type']}, Target: ${parsed_goal.get('target_amount', 'TBD')}, Timeline: {parsed_goal.get('time_horizon', 'TBD')} years"
                return "Goal parsing completed"
            except Exception as e:
                return f"Error parsing goal: {str(e)}"

    class ExplanationTool(BaseTool):
        name: str = "explanation_tool"
        description: str = "Explain financial decisions in plain language"

        def _run(self, decision: str) -> str:
            """Explain a financial decision"""
            try:
                explainer_agent = ExplainabilityAgent()
                explanation = explainer_agent.explain_decision({"description": decision})
                if 'explanation' in explanation:
                    return explanation['explanation']
                return f"Explanation: {decision} was recommended based on current market conditions and your financial profile."
            except Exception as e:
                return f"Error generating explanation: {str(e)}"

# ================================
# CrewAI Agent Definitions
# ================================

if CREWAI_AVAILABLE:
    def create_financial_crew() -> Crew:
        """Create a simplified financial advisory crew"""

        # Initialize tools
        market_tool = MarketDataTool()
        portfolio_tool = PortfolioOptimizationTool()
        planning_tool = GoalPlanningTool()
        explanation_tool = ExplanationTool()

        # Data Analyst Agent
        data_analyst = Agent(
            role='Market Data Analyst',
            goal='Analyze market conditions and provide data insights',
            backstory="""You are an experienced financial data analyst with expertise in
            market trends, economic indicators, and risk assessment. You provide accurate,
            timely market data and analysis to support investment decisions.""",
            tools=[market_tool],
            verbose=True,
            allow_delegation=False,
        )

        # Portfolio Manager Agent
        portfolio_manager = Agent(
            role='Portfolio Manager',
            goal='Create optimized investment portfolios',
            backstory="""You are a skilled portfolio manager with deep knowledge of asset
            allocation, risk management, and investment strategies. You create balanced
            portfolios tailored to individual risk tolerance and goals.""",
            tools=[portfolio_tool],
            verbose=True,
            allow_delegation=False
        )

        # Financial Planner Agent
        financial_planner = Agent(
            role='Financial Planner',
            goal='Understand client goals and create financial strategies',
            backstory="""You are a certified financial planner who specializes in translating
            client dreams into actionable financial plans. You excel at goal interpretation
            and strategic planning.""",
            tools=[planning_tool],
            verbose=True,
            allow_delegation=False
        )

        # Financial Advisor Agent
        financial_advisor = Agent(
            role='Financial Advisor',
            goal='Communicate recommendations clearly to clients',
            backstory="""You are a client-focused financial advisor who excels at explaining
            complex financial concepts in simple terms. You ensure clients understand
            their investments and feel confident in their decisions.""",
            tools=[explanation_tool],
            verbose=True,
            allow_delegation=False
        )

        return Crew(
            agents=[data_analyst, portfolio_manager, financial_planner, financial_advisor],
            verbose=True,
            process=Process.sequential
        )

    # ================================
    # Simplified Workflow Functions
    # ================================

    async def run_market_analysis(symbols: List[str] = None) -> Dict[str, Any]:
        """Simple market analysis workflow"""
        if symbols is None:
            symbols = ["SPY", "QQQ", "BND"]

        # Initialize tools
        market_tool = MarketDataTool()

        # Create data analyst agent
        data_analyst = Agent(
            role='Market Data Analyst',
            goal='Analyze market conditions and provide data insights',
            backstory="""You are an experienced financial data analyst with expertise in
            market trends, economic indicators, and risk assessment. You provide accurate,
            timely market data and analysis to support investment decisions.""",
            tools=[market_tool],
            verbose=True,
            allow_delegation=False
        )

        # Create market analysis task
        task = Task(
            description=f"Analyze current market conditions for {', '.join(symbols)}. Provide key insights on market trends, volatility, and investment outlook.",
            agent=data_analyst,
            expected_output="Market analysis with key trends and insights"
        )

        # Create crew with tasks
        crew = Crew(
            agents=[data_analyst],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )

        try:
            result = crew.kickoff()
            return {
                "status": "success",
                "analysis": str(result),
                "symbols_analyzed": symbols
            }
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analysis": "Market analysis could not be completed"
            }

    async def run_portfolio_advisory(goal_text: str, risk_level: int = 3) -> Dict[str, Any]:
        """Complete portfolio advisory workflow"""
        crew = create_financial_crew()

        # Define workflow tasks
        tasks = [
            Task(
                description="Analyze current market conditions and identify key trends affecting investment decisions",
                agent=crew.agents[0],  # Data analyst
                expected_output="Market analysis with current conditions"
            ),
            Task(
                description=f"Parse this financial goal: '{goal_text}' and determine appropriate investment strategy",
                agent=crew.agents[2],  # Financial planner
                expected_output="Parsed financial goal with recommended strategy"
            ),
            Task(
                description=f"Create an optimized portfolio for risk level {risk_level} based on the market analysis and financial goal",
                agent=crew.agents[1],  # Portfolio manager
                expected_output="Optimized portfolio allocation"
            ),
            Task(
                description="Explain the investment recommendations in clear, client-friendly language",
                agent=crew.agents[3],  # Financial advisor
                expected_output="Plain English explanation of recommendations"
            )
        ]

        try:
            result = crew.kickoff(tasks)
            return {
                "status": "success",
                "recommendations": str(result),
                "goal": goal_text,
                "risk_level": risk_level
            }
        except Exception as e:
            logger.error(f"Portfolio advisory failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "recommendations": "Advisory workflow could not be completed"
            }

    async def run_quick_advisory(question: str) -> Dict[str, Any]:
        """Quick financial advisory for simple questions"""
        # Initialize tools
        explanation_tool = ExplanationTool()

        # Create financial advisor agent
        financial_advisor = Agent(
            role='Financial Advisor',
            goal='Provide clear, actionable financial advice',
            backstory="""You are a trusted financial advisor with years of experience
            helping individuals make informed financial decisions. You excel at explaining
            complex concepts in simple terms and providing practical guidance.""",
            tools=[explanation_tool],
            verbose=True,
            allow_delegation=False
        )

        # Single task for quick questions
        task = Task(
            description=f"Provide financial advice for this question: '{question}'. Give practical, actionable guidance.",
            agent=financial_advisor,
            expected_output="Clear financial advice and guidance"
        )

        # Create crew with tasks
        crew = Crew(
            agents=[financial_advisor],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )

        try:
            result = crew.kickoff()
            return {
                "status": "success",
                "advice": str(result),
                "question": question
            }
        except Exception as e:
            logger.error(f"Quick advisory failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "advice": "Could not provide advice at this time"
            }

    # ================================
    # Simplified Agent Manager
    # ================================

    class SimpleCrewManager:
        """Simplified manager for CrewAI workflows"""

        def __init__(self):
            self.crew = create_financial_crew()
            logger.info("CrewAI Financial Advisory Team initialized")

        async def market_analysis(self, symbols: List[str] = None) -> Dict[str, Any]:
            """Run market analysis"""
            return await run_market_analysis(symbols)

        async def portfolio_advisory(self, goal_text: str, risk_level: int = 3) -> Dict[str, Any]:
            """Run complete portfolio advisory"""
            return await run_portfolio_advisory(goal_text, risk_level)

        async def quick_advice(self, question: str) -> Dict[str, Any]:
            """Get quick financial advice"""
            return await run_quick_advisory(question)

        def get_crew_status(self) -> Dict[str, Any]:
            """Get status of the crew"""
            return {
                "crew_size": len(self.crew.agents),
                "agents": [agent.role for agent in self.crew.agents],
                "process": str(self.crew.process),
                "status": "ready"
            }

# ================================
# Fallback Logic
# ================================

if CREWAI_AVAILABLE:
    # Use full CrewAI functionality
    crew_manager = SimpleCrewManager()
    logger.info("Using CrewAI-powered SimpleCrewManager")
else:
    # Fallback to simple orchestrator
    logger.info("Falling back to simple orchestrator")
    from .simple_crew import crew_manager