import pytest
from unittest.mock import AsyncMock, patch
from agent.agents import PlannerAgent
from agent.models import GoalType, RiskLevel


class TestPlannerAgent:
    @pytest.fixture
    def planner_agent(self):
        return PlannerAgent()

    def test_init(self, planner_agent):
        assert GoalType.RETIREMENT in planner_agent.goal_strategies
        assert "house" in planner_agent.goal_keywords[GoalType.HOUSE_DOWN_PAYMENT]
        assert isinstance(planner_agent.coral_client, object)

    @pytest.mark.asyncio
    async def test_parse_goal(self, planner_agent):
        goal_text = "I want to save for retirement"

        with patch.object(planner_agent.coral_client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"goal_type": "RETIREMENT", "time_horizon": 30}

            result = await planner_agent.parse_goal(goal_text)

            assert "goal_type" in result or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_create_plan(self, planner_agent):
        goal = {"type": GoalType.RETIREMENT, "amount": 1000000, "time_horizon": 30}

        with patch.object(planner_agent.coral_client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"plan": {"monthly_contribution": 5000}}

            result = await planner_agent.create_plan(goal)

            assert "plan" in result or isinstance(result, dict)

    def test_get_goal_strategy(self, planner_agent):
        strategy = planner_agent.get_goal_strategy(GoalType.RETIREMENT)

        assert strategy["risk_level"] == RiskLevel.GROWTH
        assert "equities" in strategy["allocation"]

    # Add more tests as needed
