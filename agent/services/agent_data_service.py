"""
Agent Data Service - Comprehensive data persistence for all agents in Supabase
Handles saving and retrieving data for Portfolio, Planner, and Explainability agents
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging
import uuid
import json

from api.dependencies.db import supabase
from ..shared.models import MarketData, MacroData

logger = logging.getLogger(__name__)


class AgentDataService:
    """Comprehensive service for saving and retrieving agent analysis data from Supabase"""

    # Table names for agent data
    ANALYSIS_SESSIONS_TABLE = "analysis_sessions"
    PORTFOLIO_ANALYSIS_TABLE = "portfolio_analysis"
    PLANNER_ANALYSIS_TABLE = "planner_analysis"
    EXPLAINABILITY_ANALYSIS_TABLE = "explainability_analysis"
    STRESS_TESTS_TABLE = "stress_tests"
    MONTE_CARLO_RESULTS_TABLE = "monte_carlo_results"
    REBALANCING_TRIGGERS_TABLE = "rebalancing_triggers"

    @staticmethod
    async def create_analysis_session(user_id: str, goal_text: str, session_type: str = "complete_analysis") -> str:
        """
        Create a new analysis session to group all agent results.

        Args:
            user_id: User identifier
            goal_text: Original goal text from user
            session_type: Type of analysis session

        Returns:
            str: Session ID
        """
        try:
            session_id = str(uuid.uuid4())

            session_data = {
                "id": session_id,
                "user_id": user_id,
                "goal_text": goal_text,
                "session_type": session_type,
                "status": "in_progress",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            result = supabase.table(AgentDataService.ANALYSIS_SESSIONS_TABLE).insert(session_data).execute()

            if result.data:
                logger.info(f"Created analysis session {session_id} for user {user_id}")
                return session_id
            else:
                raise Exception(f"Failed to create session: {result}")

        except Exception as e:
            logger.error(f"Error creating analysis session: {e}")
            raise

    @staticmethod
    async def save_portfolio_analysis(session_id: str, user_id: str, portfolio_data: Dict[str, Any]) -> bool:
        """
        Save Portfolio Agent analysis results.

        Args:
            session_id: Analysis session ID
            user_id: User identifier
            portfolio_data: Complete portfolio analysis data

        Returns:
            bool: True if successful
        """
        try:
            # Save main portfolio analysis
            portfolio_record = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_id": user_id,
                "risk_level": portfolio_data.get("risk_level"),
                "allocations": json.dumps(portfolio_data.get("allocations", {})),
                "expected_return": portfolio_data.get("expected_return"),
                "expected_risk": portfolio_data.get("expected_risk"),
                "sharpe_ratio": portfolio_data.get("sharpe_ratio"),
                "portfolio_value": portfolio_data.get("portfolio_value"),
                "created_at": datetime.now().isoformat()
            }

            result = supabase.table(AgentDataService.PORTFOLIO_ANALYSIS_TABLE).insert(portfolio_record).execute()

            if not result.data:
                raise Exception("Failed to save portfolio analysis")

            portfolio_id = result.data[0]["id"]

            # Save stress test results if available
            stress_tests = portfolio_data.get("stress_tests", [])
            if stress_tests:
                await AgentDataService._save_stress_tests(portfolio_id, stress_tests)

            # Save rebalancing triggers if available
            rebalancing_triggers = portfolio_data.get("rebalancing_triggers", [])
            if rebalancing_triggers:
                await AgentDataService._save_rebalancing_triggers(portfolio_id, rebalancing_triggers)

            logger.info(f"Saved portfolio analysis for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving portfolio analysis: {e}")
            return False

    @staticmethod
    async def save_planner_analysis(session_id: str, user_id: str, planner_data: Dict[str, Any]) -> bool:
        """
        Save Planner Agent analysis results.

        Args:
            session_id: Analysis session ID
            user_id: User identifier
            planner_data: Complete planner analysis data

        Returns:
            bool: True if successful
        """
        try:
            # Save main planner analysis
            planner_record = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_id": user_id,
                "goal_type": planner_data.get("goal_type"),
                "target_amount": planner_data.get("target_amount"),
                "time_horizon_years": planner_data.get("time_horizon_years"),
                "current_age": planner_data.get("current_age"),
                "risk_tolerance": planner_data.get("risk_tolerance"),
                "monthly_investment": planner_data.get("monthly_investment"),
                "success_probability": planner_data.get("success_probability"),
                "expected_final_value": planner_data.get("expected_final_value"),
                "goal_summary": planner_data.get("goal_summary"),
                "asset_allocation": json.dumps(planner_data.get("asset_allocation", {})),
                "risk_considerations": json.dumps(planner_data.get("risk_considerations", [])),
                "milestones": json.dumps(planner_data.get("milestones", [])),
                "alternative_scenarios": json.dumps(planner_data.get("alternative_scenarios", [])),
                "stress_test_summary": planner_data.get("stress_test_summary"),
                "created_at": datetime.now().isoformat()
            }

            result = supabase.table(AgentDataService.PLANNER_ANALYSIS_TABLE).insert(planner_record).execute()

            if not result.data:
                raise Exception("Failed to save planner analysis")

            planner_id = result.data[0]["id"]

            # Save Monte Carlo results if available
            monte_carlo_results = planner_data.get("monte_carlo_results", [])
            if monte_carlo_results:
                await AgentDataService._save_monte_carlo_results(planner_id, monte_carlo_results)

            logger.info(f"Saved planner analysis for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving planner analysis: {e}")
            return False

    @staticmethod
    async def save_explainability_analysis(session_id: str, user_id: str, explanation_data: Dict[str, Any]) -> bool:
        """
        Save Explainability Agent analysis results.

        Args:
            session_id: Analysis session ID
            user_id: User identifier
            explanation_data: Complete explanation analysis data

        Returns:
            bool: True if successful
        """
        try:
            explanation_record = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "user_id": user_id,
                "main_explanation": explanation_data.get("main_explanation"),
                "risk_framework": explanation_data.get("risk_framework"),
                "return_expectations": explanation_data.get("return_expectations"),
                "monitoring_approach": explanation_data.get("monitoring_approach"),
                "word_count": explanation_data.get("word_count"),
                "confidence_score": explanation_data.get("confidence_score"),
                "theoretical_framework": explanation_data.get("theoretical_framework"),
                "explanation_metadata": json.dumps(explanation_data.get("metadata", {})),
                "created_at": datetime.now().isoformat()
            }

            result = supabase.table(AgentDataService.EXPLAINABILITY_ANALYSIS_TABLE).insert(explanation_record).execute()

            if result.data:
                logger.info(f"Saved explainability analysis for session {session_id}")
                return True
            else:
                raise Exception("Failed to save explainability analysis")

        except Exception as e:
            logger.error(f"Error saving explainability analysis: {e}")
            return False

    @staticmethod
    async def _save_stress_tests(portfolio_id: str, stress_tests: List[Dict[str, Any]]) -> bool:
        """Save stress test results to database."""
        try:
            stress_test_records = []
            for test in stress_tests:
                record = {
                    "id": str(uuid.uuid4()),
                    "portfolio_id": portfolio_id,
                    "scenario": test.get("scenario"),
                    "portfolio_loss": test.get("portfolio_loss"),
                    "worst_asset_loss": test.get("worst_asset_loss"),
                    "recovery_time_estimate": test.get("recovery_time_estimate"),
                    "risk_adjusted_return": test.get("risk_adjusted_return"),
                    "max_drawdown": test.get("max_drawdown"),
                    "var_95": test.get("var_95"),
                    "expected_shortfall": test.get("expected_shortfall"),
                    "stress_ratio": test.get("stress_ratio"),
                    "created_at": datetime.now().isoformat()
                }
                stress_test_records.append(record)

            if stress_test_records:
                result = supabase.table(AgentDataService.STRESS_TESTS_TABLE).insert(stress_test_records).execute()
                return bool(result.data)

            return True

        except Exception as e:
            logger.error(f"Error saving stress tests: {e}")
            return False

    @staticmethod
    async def _save_rebalancing_triggers(portfolio_id: str, triggers: List[Dict[str, Any]]) -> bool:
        """Save rebalancing triggers to database."""
        try:
            trigger_records = []
            for trigger in triggers:
                record = {
                    "id": str(uuid.uuid4()),
                    "portfolio_id": portfolio_id,
                    "trigger_name": trigger.get("name"),
                    "condition_met": trigger.get("condition_met"),
                    "trigger_value": trigger.get("trigger_value"),
                    "threshold": trigger.get("threshold"),
                    "confidence": trigger.get("confidence"),
                    "urgency": trigger.get("urgency"),
                    "recommended_action": trigger.get("recommended_action"),
                    "expected_impact": trigger.get("expected_impact"),
                    "created_at": datetime.now().isoformat()
                }
                trigger_records.append(record)

            if trigger_records:
                result = supabase.table(AgentDataService.REBALANCING_TRIGGERS_TABLE).insert(trigger_records).execute()
                return bool(result.data)

            return True

        except Exception as e:
            logger.error(f"Error saving rebalancing triggers: {e}")
            return False

    @staticmethod
    async def _save_monte_carlo_results(planner_id: str, monte_carlo_results: List[Dict[str, Any]]) -> bool:
        """Save Monte Carlo simulation results to database."""
        try:
            mc_records = []
            for result in monte_carlo_results:
                record = {
                    "id": str(uuid.uuid4()),
                    "planner_id": planner_id,
                    "scenario": result.get("scenario"),
                    "success_probability": result.get("success_probability"),
                    "expected_final_value": result.get("expected_final_value"),
                    "percentile_10": result.get("percentile_10"),
                    "percentile_50": result.get("percentile_50"),
                    "percentile_90": result.get("percentile_90"),
                    "shortfall_risk": result.get("shortfall_risk"),
                    "excess_probability": result.get("excess_probability"),
                    "required_monthly_savings": result.get("required_monthly_savings"),
                    "confidence_interval_lower": result.get("confidence_interval", [0, 0])[0],
                    "confidence_interval_upper": result.get("confidence_interval", [0, 0])[1],
                    "created_at": datetime.now().isoformat()
                }
                mc_records.append(record)

            if mc_records:
                result = supabase.table(AgentDataService.MONTE_CARLO_RESULTS_TABLE).insert(mc_records).execute()
                return bool(result.data)

            return True

        except Exception as e:
            logger.error(f"Error saving Monte Carlo results: {e}")
            return False

    @staticmethod
    async def complete_analysis_session(session_id: str) -> bool:
        """Mark analysis session as completed."""
        try:
            update_data = {
                "status": "completed",
                "updated_at": datetime.now().isoformat()
            }

            result = supabase.table(AgentDataService.ANALYSIS_SESSIONS_TABLE).update(update_data).eq("id", session_id).execute()

            if result.data:
                logger.info(f"Completed analysis session {session_id}")
                return True
            else:
                raise Exception("Failed to update session status")

        except Exception as e:
            logger.error(f"Error completing analysis session: {e}")
            return False

    @staticmethod
    async def get_complete_analysis(session_id: str) -> Dict[str, Any]:
        """
        Retrieve complete analysis data for a session.

        Args:
            session_id: Analysis session ID

        Returns:
            Dict containing all analysis data
        """
        try:
            # Get session info
            session_result = supabase.table(AgentDataService.ANALYSIS_SESSIONS_TABLE).select("*").eq("id", session_id).execute()

            if not session_result.data:
                raise Exception(f"Session {session_id} not found")

            session_data = session_result.data[0]

            # Get portfolio analysis
            portfolio_result = supabase.table(AgentDataService.PORTFOLIO_ANALYSIS_TABLE).select("*").eq("session_id", session_id).execute()
            portfolio_data = portfolio_result.data[0] if portfolio_result.data else None

            # Get planner analysis
            planner_result = supabase.table(AgentDataService.PLANNER_ANALYSIS_TABLE).select("*").eq("session_id", session_id).execute()
            planner_data = planner_result.data[0] if planner_result.data else None

            # Get explainability analysis
            explanation_result = supabase.table(AgentDataService.EXPLAINABILITY_ANALYSIS_TABLE).select("*").eq("session_id", session_id).execute()
            explanation_data = explanation_result.data[0] if explanation_result.data else None

            # Get detailed data if portfolio analysis exists
            stress_tests = []
            rebalancing_triggers = []
            if portfolio_data:
                # Get stress tests
                stress_result = supabase.table(AgentDataService.STRESS_TESTS_TABLE).select("*").eq("portfolio_id", portfolio_data["id"]).execute()
                stress_tests = stress_result.data if stress_result.data else []

                # Get rebalancing triggers
                triggers_result = supabase.table(AgentDataService.REBALANCING_TRIGGERS_TABLE).select("*").eq("portfolio_id", portfolio_data["id"]).execute()
                rebalancing_triggers = triggers_result.data if triggers_result.data else []

            # Get Monte Carlo results if planner analysis exists
            monte_carlo_results = []
            if planner_data:
                mc_result = supabase.table(AgentDataService.MONTE_CARLO_RESULTS_TABLE).select("*").eq("planner_id", planner_data["id"]).execute()
                monte_carlo_results = mc_result.data if mc_result.data else []

            # Compile complete analysis
            complete_analysis = {
                "session": session_data,
                "portfolio_analysis": {
                    **(portfolio_data or {}),
                    "stress_tests": stress_tests,
                    "rebalancing_triggers": rebalancing_triggers
                },
                "planner_analysis": {
                    **(planner_data or {}),
                    "monte_carlo_results": monte_carlo_results
                },
                "explainability_analysis": explanation_data or {},
                "metadata": {
                    "retrieved_at": datetime.now().isoformat(),
                    "data_completeness": {
                        "portfolio": bool(portfolio_data),
                        "planner": bool(planner_data),
                        "explainability": bool(explanation_data),
                        "stress_tests": len(stress_tests),
                        "monte_carlo": len(monte_carlo_results),
                        "triggers": len(rebalancing_triggers)
                    }
                }
            }

            logger.info(f"Retrieved complete analysis for session {session_id}")
            return complete_analysis

        except Exception as e:
            logger.error(f"Error retrieving complete analysis: {e}")
            raise

    @staticmethod
    async def get_user_analysis_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get user's analysis history.

        Args:
            user_id: User identifier
            limit: Number of sessions to retrieve

        Returns:
            List of analysis sessions
        """
        try:
            result = supabase.table(AgentDataService.ANALYSIS_SESSIONS_TABLE)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error retrieving user analysis history: {e}")
            return []

    @staticmethod
    async def delete_analysis_session(session_id: str) -> bool:
        """
        Delete an analysis session and all related data.

        Args:
            session_id: Session ID to delete

        Returns:
            bool: True if successful
        """
        try:
            # Get portfolio and planner IDs for cascading deletes
            portfolio_result = supabase.table(AgentDataService.PORTFOLIO_ANALYSIS_TABLE).select("id").eq("session_id", session_id).execute()
            planner_result = supabase.table(AgentDataService.PLANNER_ANALYSIS_TABLE).select("id").eq("session_id", session_id).execute()

            # Delete related data
            if portfolio_result.data:
                portfolio_id = portfolio_result.data[0]["id"]
                supabase.table(AgentDataService.STRESS_TESTS_TABLE).delete().eq("portfolio_id", portfolio_id).execute()
                supabase.table(AgentDataService.REBALANCING_TRIGGERS_TABLE).delete().eq("portfolio_id", portfolio_id).execute()

            if planner_result.data:
                planner_id = planner_result.data[0]["id"]
                supabase.table(AgentDataService.MONTE_CARLO_RESULTS_TABLE).delete().eq("planner_id", planner_id).execute()

            # Delete main analysis records
            supabase.table(AgentDataService.PORTFOLIO_ANALYSIS_TABLE).delete().eq("session_id", session_id).execute()
            supabase.table(AgentDataService.PLANNER_ANALYSIS_TABLE).delete().eq("session_id", session_id).execute()
            supabase.table(AgentDataService.EXPLAINABILITY_ANALYSIS_TABLE).delete().eq("session_id", session_id).execute()

            # Delete session
            result = supabase.table(AgentDataService.ANALYSIS_SESSIONS_TABLE).delete().eq("id", session_id).execute()

            logger.info(f"Deleted analysis session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting analysis session: {e}")
            return False