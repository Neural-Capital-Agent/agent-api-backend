"""
Simplified Multi-Agent Orchestration (CrewAI-like functionality)
Works without external dependencies, using your existing Neural Capital agents.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from ..core.data_agent import DataAgent
from ..core.portfolio_agent import PortfolioAgent
from ..core.planner_agent import PlannerAgent
from ..core.explainability_agent import ExplainabilityAgent

logger = logging.getLogger(__name__)

@dataclass
class Task:
    """Simple task definition"""
    description: str
    agent_type: str
    parameters: Dict[str, Any]
    expected_output: str

@dataclass
class WorkflowResult:
    """Result from a workflow execution"""
    success: bool
    results: List[Dict[str, Any]]
    summary: str
    timestamp: str
    error: Optional[str] = None

class SimpleAgentOrchestrator:
    """
    Simplified agent orchestrator that coordinates your Neural Capital agents
    without requiring CrewAI dependencies.
    """

    def __init__(self):
        self.agents = {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainer': ExplainabilityAgent()
        }
        logger.info("Simple Agent Orchestrator initialized with 4 agents")

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task with the appropriate agent"""
        try:
            agent = self.agents.get(task.agent_type)
            if not agent:
                raise ValueError(f"Unknown agent type: {task.agent_type}")

            # Route task to appropriate agent method
            if task.agent_type == 'data':
                if 'symbol' in task.parameters:
                    result = await agent.get_market_data(task.parameters['symbol'])
                elif 'symbols' in task.parameters:
                    result = await agent.get_market_context(task.parameters.get('timestamp'))
                else:
                    result = await agent.get_market_context()

            elif task.agent_type == 'portfolio':
                risk_level = task.parameters.get('risk_level', 3)
                goal = task.parameters.get('goal', 'general')
                result = await agent.build_portfolio(risk_level, goal)

            elif task.agent_type == 'planner':
                goal_text = task.parameters.get('goal_text', '')
                result = await agent.parse_goal(goal_text)

            elif task.agent_type == 'explainer':
                action = task.parameters.get('action', task.parameters)
                result = await agent.explain_decision(action)

            return {
                'task': task.description,
                'agent': task.agent_type,
                'result': result,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                'task': task.description,
                'agent': task.agent_type,
                'error': str(e),
                'status': 'failed',
                'timestamp': datetime.now().isoformat()
            }

    async def run_workflow(self, tasks: List[Task]) -> WorkflowResult:
        """Execute a workflow (sequence of tasks)"""
        results = []
        context = {}  # Shared context between tasks

        for i, task in enumerate(tasks):
            logger.info(f"Executing task {i+1}/{len(tasks)}: {task.description}")

            # Add context from previous tasks
            task.parameters.update(context)

            result = await self.execute_task(task)
            results.append(result)

            # Update context with results for next tasks
            if result['status'] == 'success':
                context[f"{task.agent_type}_result"] = result['result']
            else:
                # If a task fails, continue but note the failure
                logger.warning(f"Task failed: {result.get('error', 'Unknown error')}")

        # Generate workflow summary
        successful_tasks = sum(1 for r in results if r['status'] == 'success')
        total_tasks = len(results)

        summary = f"Workflow completed: {successful_tasks}/{total_tasks} tasks successful"

        if successful_tasks == total_tasks:
            overall_success = True
        else:
            overall_success = False

        return WorkflowResult(
            success=overall_success,
            results=results,
            summary=summary,
            timestamp=datetime.now().isoformat(),
            error=None if overall_success else "Some tasks failed"
        )

    # ================================
    # Pre-defined Workflows
    # ================================

    async def market_analysis_workflow(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Simplified market analysis workflow"""
        if symbols is None:
            symbols = ["SPY", "QQQ", "BND"]

        tasks = [
            Task(
                description=f"Get market data for {', '.join(symbols)}",
                agent_type='data',
                parameters={'symbols': symbols},
                expected_output="Market data and analysis"
            ),
            Task(
                description="Explain market conditions in plain language",
                agent_type='explainer',
                parameters={'action': {'type': 'market_analysis', 'symbols': symbols}},
                expected_output="Market explanation"
            )
        ]

        workflow_result = await self.run_workflow(tasks)

        return {
            'workflow': 'market_analysis',
            'status': 'success' if workflow_result.success else 'partial_success',
            'analysis': workflow_result.summary,
            'details': workflow_result.results,
            'symbols_analyzed': symbols,
            'timestamp': workflow_result.timestamp
        }

    async def portfolio_advisory_workflow(self, goal_text: str, risk_level: int = 3) -> Dict[str, Any]:
        """Complete portfolio advisory workflow"""
        tasks = [
            Task(
                description="Get current market conditions",
                agent_type='data',
                parameters={},
                expected_output="Market context"
            ),
            Task(
                description=f"Parse financial goal: {goal_text}",
                agent_type='planner',
                parameters={'goal_text': goal_text},
                expected_output="Parsed goal parameters"
            ),
            Task(
                description=f"Build portfolio for risk level {risk_level}",
                agent_type='portfolio',
                parameters={'risk_level': risk_level, 'goal': goal_text},
                expected_output="Optimized portfolio"
            ),
            Task(
                description="Explain portfolio recommendations",
                agent_type='explainer',
                parameters={'action': {'type': 'portfolio_recommendation', 'risk_level': risk_level}},
                expected_output="Plain English explanation"
            )
        ]

        workflow_result = await self.run_workflow(tasks)

        return {
            'workflow': 'portfolio_advisory',
            'status': 'success' if workflow_result.success else 'partial_success',
            'recommendations': workflow_result.summary,
            'details': workflow_result.results,
            'goal': goal_text,
            'risk_level': risk_level,
            'timestamp': workflow_result.timestamp
        }

    async def quick_advice_workflow(self, question: str) -> Dict[str, Any]:
        """Quick financial advice workflow"""
        tasks = [
            Task(
                description="Get current market context for advice",
                agent_type='data',
                parameters={},
                expected_output="Market context"
            ),
            Task(
                description=f"Provide advice for: {question}",
                agent_type='explainer',
                parameters={'action': {'type': 'quick_advice', 'question': question}},
                expected_output="Financial advice"
            )
        ]

        workflow_result = await self.run_workflow(tasks)

        return {
            'workflow': 'quick_advice',
            'status': 'success' if workflow_result.success else 'partial_success',
            'advice': workflow_result.summary,
            'details': workflow_result.results,
            'question': question,
            'timestamp': workflow_result.timestamp
        }

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get status of the orchestrator"""
        return {
            'orchestrator': 'SimpleAgentOrchestrator',
            'agents_available': len(self.agents),
            'agent_types': list(self.agents.keys()),
            'workflows_available': [
                'market_analysis_workflow',
                'portfolio_advisory_workflow',
                'quick_advice_workflow'
            ],
            'status': 'ready'
        }

# Global orchestrator instance
simple_orchestrator = SimpleAgentOrchestrator()


# ================================
# Compatibility layer for CrewAI-like interface
# ================================

class SimpleCrewManager:
    """CrewAI-compatible interface using simple orchestrator"""

    def __init__(self):
        self.orchestrator = simple_orchestrator
        logger.info("Simple Crew Manager initialized (CrewAI-compatible)")

    async def market_analysis(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Market analysis using simple orchestrator"""
        return await self.orchestrator.market_analysis_workflow(symbols)

    async def portfolio_advisory(self, goal_text: str, risk_level: int = 3) -> Dict[str, Any]:
        """Portfolio advisory using simple orchestrator"""
        return await self.orchestrator.portfolio_advisory_workflow(goal_text, risk_level)

    async def quick_advice(self, question: str) -> Dict[str, Any]:
        """Quick advice using simple orchestrator"""
        return await self.orchestrator.quick_advice_workflow(question)

    def get_crew_status(self) -> Dict[str, Any]:
        """Get crew status (compatible with CrewAI interface)"""
        status = self.orchestrator.get_orchestrator_status()
        return {
            'crew_size': status['agents_available'],
            'agents': [
                'Market Data Analyst',
                'Portfolio Manager',
                'Financial Planner',
                'Financial Advisor'
            ],
            'process': 'sequential',
            'status': 'ready',
            'implementation': 'SimpleAgentOrchestrator'
        }

# Global crew manager (CrewAI-compatible)
crew_manager = SimpleCrewManager()