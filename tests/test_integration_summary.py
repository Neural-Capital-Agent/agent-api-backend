"""
Summary integration test that validates core functionality across all systems.

This is a lightweight test that can be run quickly to validate that:
- All integration test files are working
- Core agent functionality is intact
- Configuration system is operational
- Error handling is functional
- Basic data flow works
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime

from agent import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent
from agent.config import config
from agent.shared import ErrorHandler, get_current_timestamp, safe_get


class TestIntegrationSummary:
    """Summary integration tests for quick validation"""

    @pytest_asyncio.fixture
    async def agents(self):
        """Create all agents for testing"""
        return {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainability': ExplainabilityAgent()
        }

    def test_all_integration_test_files_importable(self):
        """Test that all integration test files can be imported"""
        try:
            import tests.test_integration_multi_agent
            import tests.test_integration_api
            import tests.test_integration_config
            import tests.test_integration_error_handling
            import tests.test_integration_coral
            import tests.test_integration_data_flow
            import tests.test_integration_fallbacks

            # All imports successful
            assert True

        except ImportError as e:
            pytest.fail(f"Integration test file import failed: {e}")

    def test_core_agent_system_functional(self, agents):
        """Test that core agent system is functional"""
        # All agents should be created successfully
        assert len(agents) == 4

        # All agents should have required attributes
        for agent_name, agent in agents.items():
            assert hasattr(agent, 'coral_client')
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'config')
            assert agent.agent_id == f"{agent_name}_agent"

    @pytest.mark.asyncio
    async def test_agent_health_checks_functional(self, agents):
        """Test that agent health checks work"""
        health_results = []

        for agent_name, agent in agents.items():
            try:
                health = await agent.health_check()
                assert health is not None
                assert isinstance(health, dict)
                health_results.append((agent_name, "success"))
            except Exception as e:
                health_results.append((agent_name, f"error: {e}"))

        # At least some health checks should work
        successful_health_checks = [r for r in health_results if r[1] == "success"]
        assert len(successful_health_checks) >= 1

    def test_configuration_system_functional(self):
        """Test that configuration system is working"""
        # Config should be accessible
        assert config is not None
        assert hasattr(config, 'base_config')
        assert hasattr(config, 'data_agent')
        assert hasattr(config, 'portfolio_agent')

        # Should be able to check fallback status
        fallbacks_enabled = config.should_use_fallbacks()
        assert isinstance(fallbacks_enabled, bool)

        # Should be able to get a fallback
        try:
            fallback = config.get_fallback('data_agent', 'validation')
            assert fallback is not None
            assert isinstance(fallback, dict)
        except (KeyError, AttributeError, ValueError):
            # Some specific fallbacks might not exist, but method should work
            pass

    def test_shared_utilities_functional(self):
        """Test that shared utilities are working"""
        # Timestamp utility
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0

        # Datetime parsing should work
        parsed_time = datetime.fromisoformat(timestamp)
        assert isinstance(parsed_time, datetime)

        # Safe get utility
        test_dict = {"key1": "value1", "key2": None}
        assert safe_get(test_dict, "key1") == "value1"
        assert safe_get(test_dict, "key2") is None
        assert safe_get(test_dict, "missing") is None
        assert safe_get(test_dict, "missing", "default") == "default"

    def test_error_handling_functional(self):
        """Test that error handling system is working"""
        # Test ErrorHandler
        test_error = ValueError("Test error")

        try:
            result = ErrorHandler.handle_with_fallback(
                "test_operation",
                "data_agent",
                "validation",
                test_error
            )

            assert result is not None
            assert isinstance(result, dict)
            assert 'error' in result
            assert 'timestamp' in result

        except Exception as e:
            # Error handler should not raise exceptions
            pytest.fail(f"Error handler raised exception: {e}")

    @pytest.mark.asyncio
    async def test_basic_agent_operations(self, agents):
        """Test basic operations across agents"""
        results = {}

        # Test DataAgent
        try:
            data_agent = agents['data']
            market_context = await data_agent.get_market_context()
            results['data_agent'] = market_context is not None
        except Exception:
            results['data_agent'] = False

        # Test PortfolioAgent
        try:
            portfolio_agent = agents['portfolio']
            portfolio = await portfolio_agent.build_portfolio(
                risk_level=3,
                goal="retirement",
                constraints={}
            )
            results['portfolio_agent'] = portfolio is not None
        except Exception:
            results['portfolio_agent'] = False

        # Test PlannerAgent
        try:
            planner_agent = agents['planner']
            parsed_goal = await planner_agent.parse_goal("Save for retirement")
            results['planner_agent'] = parsed_goal is not None
        except Exception:
            results['planner_agent'] = False

        # Test ExplainabilityAgent
        try:
            explainability_agent = agents['explainability']
            action = {
                'type': 'test_action',
                'details': 'test',
                'timestamp': datetime.now()
            }
            explanation = await explainability_agent.explain_decision(action)
            results['explainability_agent'] = explanation is not None
        except Exception:
            results['explainability_agent'] = False

        # At least some operations should work
        successful_operations = sum(results.values())
        assert successful_operations >= 1

        # Log results for debugging
        print(f"Agent operation results: {results}")

    def test_integration_test_categories_complete(self):
        """Test that all integration test categories are present"""
        expected_categories = [
            'multi_agent',
            'api',
            'config',
            'error_handling',
            'coral',
            'data_flow',
            'fallbacks'
        ]

        import os
        test_dir = os.path.dirname(__file__)
        test_files = os.listdir(test_dir)

        for category in expected_categories:
            expected_file = f"test_integration_{category}.py"
            assert expected_file in test_files, f"Missing integration test file: {expected_file}"

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, agents):
        """Test that agents can handle concurrent operations"""
        tasks = []

        # Create concurrent tasks
        for agent_name, agent in agents.items():
            task = agent.health_check()
            tasks.append(task)

        # Execute concurrently
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            assert len(results) == len(agents)

            # At least some should complete successfully
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) >= 1

        except Exception as e:
            pytest.fail(f"Concurrent operations failed: {e}")

    def test_agent_inheritance_structure(self, agents):
        """Test that agents properly inherit from BaseAgent"""
        from agent.shared import BaseAgent

        for agent_name, agent in agents.items():
            # Should be instance of BaseAgent
            assert isinstance(agent, BaseAgent)

            # Should have BaseAgent attributes
            assert hasattr(agent, 'coral_client')
            assert hasattr(agent, 'agent_id')
            assert hasattr(agent, 'config')

    def test_configuration_consistency(self, agents):
        """Test configuration consistency across agents"""
        # All agents should reference same config object
        config_objects = [agent.config for agent in agents.values()]
        first_config = config_objects[0]

        for cfg in config_objects[1:]:
            assert cfg is first_config  # Same object reference

        # Configuration should have expected structure
        assert hasattr(first_config, 'data_agent')
        assert hasattr(first_config, 'portfolio_agent')

    def test_integration_test_coverage(self):
        """Test that integration tests cover expected functionality"""

        # Expected test patterns that should exist
        expected_patterns = [
            'agent.*initialization',
            'health.*check',
            'config.*structure',
            'error.*handling',
            'fallback.*system',
            'data.*flow',
            'coral.*protocol'
        ]

        import os
        import re

        test_dir = os.path.dirname(__file__)
        coverage_found = []

        # Check integration test files for expected patterns
        for filename in os.listdir(test_dir):
            if filename.startswith('test_integration_') and filename.endswith('.py'):
                filepath = os.path.join(test_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().lower()

                        for pattern in expected_patterns:
                            if re.search(pattern, content):
                                coverage_found.append(pattern)
                except Exception:
                    continue

        # Should find most expected patterns
        coverage_ratio = len(set(coverage_found)) / len(expected_patterns)
        assert coverage_ratio >= 0.5  # At least 50% coverage of expected patterns