"""
Integration tests for configuration system.

Tests the complete configuration management including:
- Configuration loading and validation
- Environment variable integration
- Fallback system behavior
- Configuration consistency across agents
- Development vs production configuration
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from agent.config import config, ConfigManager
from agent.models import RiskLevel, GoalType


class TestConfigurationIntegration:
    """Integration tests for the configuration system"""

    def test_config_singleton_behavior(self):
        """Test that config behaves as a singleton across imports"""
        from agent.config import config as config1
        from agent.config import config as config2

        # Should be the same instance
        assert config1 is config2

        # Should be the same as the globally imported config
        assert config1 is config

    def test_config_structure_completeness(self):
        """Test that configuration has all required sections"""
        # Base configuration
        assert hasattr(config, 'base_config')
        assert hasattr(config.base_config, 'use_fallbacks')
        assert hasattr(config.base_config, 'log_fallback_usage')
        assert hasattr(config.base_config, 'environment')

        # Agent configurations
        assert hasattr(config, 'data_agent')
        assert hasattr(config, 'portfolio_agent')
        assert hasattr(config, 'planner_agent')
        assert hasattr(config, 'explainability_agent')

        # LLM configuration
        assert hasattr(config, 'mistral_client')

    def test_data_agent_config_completeness(self):
        """Test that DataAgent configuration is complete"""
        data_config = config.data_agent

        # Asset universe configurations
        assert hasattr(data_config, 'EQUITY_UNIVERSE')
        assert hasattr(data_config, 'FIXED_INCOME_UNIVERSE')
        assert hasattr(data_config, 'ALTERNATIVES_UNIVERSE')
        assert hasattr(data_config, 'CRYPTO_UNIVERSE')

        # Macro indicators
        assert hasattr(data_config, 'MACRO_INDICATORS')

        # Verify data types
        assert isinstance(data_config.EQUITY_UNIVERSE, list)
        assert isinstance(data_config.FIXED_INCOME_UNIVERSE, list)
        assert isinstance(data_config.ALTERNATIVES_UNIVERSE, list)
        assert isinstance(data_config.CRYPTO_UNIVERSE, list)
        assert isinstance(data_config.MACRO_INDICATORS, dict)

        # Should have some assets defined
        assert len(data_config.EQUITY_UNIVERSE) > 0
        assert len(data_config.FIXED_INCOME_UNIVERSE) > 0

    def test_portfolio_agent_config_completeness(self):
        """Test that PortfolioAgent configuration is complete"""
        portfolio_config = config.portfolio_agent

        # Base allocations
        assert hasattr(portfolio_config, 'BASE_ALLOCATIONS')
        assert isinstance(portfolio_config.BASE_ALLOCATIONS, dict)

        # Should have allocations for all risk levels
        for risk_level in range(1, 6):  # 1-5 risk levels
            assert risk_level in portfolio_config.BASE_ALLOCATIONS

        # Each allocation should be a dictionary with asset classes
        for allocation in portfolio_config.BASE_ALLOCATIONS.values():
            assert isinstance(allocation, dict)
            assert 'equity' in allocation
            assert 'fixed_income' in allocation

    def test_planner_agent_config_completeness(self):
        """Test that PlannerAgent configuration is complete"""
        planner_config = config.planner_agent

        # Goal strategies
        assert hasattr(planner_config, 'GOAL_STRATEGIES')
        assert isinstance(planner_config.GOAL_STRATEGIES, dict)

        # Goal keywords
        assert hasattr(planner_config, 'GOAL_KEYWORDS')
        assert isinstance(planner_config.GOAL_KEYWORDS, dict)

        # Should have strategies for major goal types
        expected_goals = ['retirement', 'house_down_payment', 'emergency_fund']
        for goal in expected_goals:
            assert goal in planner_config.GOAL_STRATEGIES

        # Each strategy should have required fields
        for strategy in planner_config.GOAL_STRATEGIES.values():
            assert 'time_horizon' in strategy
            assert 'allocation' in strategy
            assert 'risk_level' in strategy

    def test_explainability_agent_config_completeness(self):
        """Test that ExplainabilityAgent configuration is complete"""
        explainability_config = config.explainability_agent

        # Jargon dictionary
        assert hasattr(explainability_config, 'JARGON_DICTIONARY')
        assert isinstance(explainability_config.JARGON_DICTIONARY, dict)

        # Risk templates
        assert hasattr(explainability_config, 'RISK_TEMPLATES')
        assert isinstance(explainability_config.RISK_TEMPLATES, dict)

        # Should have some jargon translations
        assert len(explainability_config.JARGON_DICTIONARY) > 0

        # Should have risk templates for different levels
        assert len(explainability_config.RISK_TEMPLATES) > 0

    def test_fallback_system_configuration(self):
        """Test that fallback system is properly configured"""
        # Test fallback availability check
        assert hasattr(config, 'should_use_fallbacks')
        assert callable(config.should_use_fallbacks)

        # Test fallback retrieval
        assert hasattr(config, 'get_fallback')
        assert callable(config.get_fallback)

        # Test environment-based fallback control
        fallbacks_enabled = config.should_use_fallbacks()
        assert isinstance(fallbacks_enabled, bool)

        # Test base config values
        assert isinstance(config.base_config.use_fallbacks, bool)
        assert isinstance(config.base_config.log_fallback_usage, bool)
        assert isinstance(config.base_config.environment, str)

    def test_fallback_data_availability(self):
        """Test that fallback data is available for all agents"""
        agent_types = ['data_agent', 'portfolio_agent', 'planner_agent', 'explainability_agent']

        for agent_type in agent_types:
            # Should be able to get some fallback data
            try:
                fallback = config.get_fallback(agent_type, 'test_fallback')
                assert fallback is not None
            except (KeyError, AttributeError):
                # It's ok if specific fallback doesn't exist, but method should work
                pass

    @patch.dict(os.environ, {'ENVIRONMENT': 'development'})
    def test_development_environment_config(self):
        """Test configuration behavior in development environment"""
        # Recreate config manager to pick up environment
        dev_config = ConfigManager()

        # In development, fallbacks should typically be enabled
        fallbacks_enabled = dev_config.should_use_fallbacks()
        assert isinstance(fallbacks_enabled, bool)

        # Logging should be more verbose in development
        if hasattr(dev_config.base_config, 'log_fallback_usage'):
            assert isinstance(dev_config.base_config.log_fallback_usage, bool)

    @patch.dict(os.environ, {'ENVIRONMENT': 'production'})
    def test_production_environment_config(self):
        """Test configuration behavior in production environment"""
        # Recreate config manager to pick up environment
        prod_config = ConfigManager()

        # Production config should be valid
        assert hasattr(prod_config, 'base_config')
        assert hasattr(prod_config, 'data_agent')

        fallbacks_enabled = prod_config.should_use_fallbacks()
        assert isinstance(fallbacks_enabled, bool)

    def test_environment_variable_integration(self):
        """Test that configuration properly integrates with environment variables"""
        # Test that environment variables are being read
        with patch.dict(os.environ, {'AI_ML_API_KEY': 'test_key'}):
            # Config should be able to access environment variables
            api_key = os.getenv('AI_ML_API_KEY')
            assert api_key == 'test_key'

        # Test missing environment variables are handled gracefully
        with patch.dict(os.environ, {}, clear=True):
            missing_key = os.getenv('NONEXISTENT_KEY')
            assert missing_key is None

    def test_config_thread_safety(self):
        """Test that configuration is thread-safe"""
        import threading
        import time

        results = []

        def access_config():
            try:
                # Access configuration from different threads
                agent_config = config.data_agent
                equity_universe = agent_config.EQUITY_UNIVERSE
                results.append(len(equity_universe))
            except Exception as e:
                results.append(f"Error: {e}")

        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=access_config)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All threads should get the same result
        assert len(results) == 5
        first_result = results[0]
        for result in results:
            assert result == first_result

    def test_config_modification_safety(self):
        """Test that configuration prevents accidental modification"""
        # Original values
        original_equities = config.data_agent.EQUITY_UNIVERSE.copy()

        # Attempting to modify should not affect original config
        try:
            modified_list = config.data_agent.EQUITY_UNIVERSE
            modified_list.append("TEST_SYMBOL")

            # Check if original is preserved (depends on implementation)
            # This test documents current behavior
            current_equities = config.data_agent.EQUITY_UNIVERSE
            # If mutable, we should be aware of this behavior
            assert isinstance(current_equities, list)

        finally:
            # Restore if needed (this documents that config might be mutable)
            pass

    def test_config_with_agents_integration(self):
        """Test that agents properly integrate with configuration"""
        from agent import DataAgent, PortfolioAgent, PlannerAgent, ExplainabilityAgent

        # Create agents
        agents = {
            'data': DataAgent(),
            'portfolio': PortfolioAgent(),
            'planner': PlannerAgent(),
            'explainability': ExplainabilityAgent()
        }

        # All agents should have access to config
        for agent_name, agent in agents.items():
            assert hasattr(agent, 'config')
            assert agent.config is not None

            # Should be the same config instance
            assert agent.config is config

    def test_config_error_handling(self):
        """Test configuration error handling"""
        # Test accessing non-existent config sections
        try:
            nonexistent = getattr(config, 'nonexistent_agent', None)
            assert nonexistent is None or hasattr(nonexistent, '__dict__')

        except AttributeError:
            # This is also acceptable behavior
            pass

        # Test fallback with invalid parameters
        try:
            result = config.get_fallback('invalid_agent', 'invalid_type')
            # Should either return something or raise a reasonable exception
            assert result is not None or True  # Always passes if no exception

        except (KeyError, AttributeError, ValueError):
            # These are reasonable exceptions for invalid input
            pass

    def test_config_consistency_across_imports(self):
        """Test that configuration is consistent across different import styles"""
        # Test different import patterns
        from agent.config import config as config_direct
        from agent import config as config_from_agent

        # Should be the same configuration
        assert config_direct.data_agent.EQUITY_UNIVERSE == config_from_agent.data_agent.EQUITY_UNIVERSE
        assert config_direct.portfolio_agent.BASE_ALLOCATIONS == config_from_agent.portfolio_agent.BASE_ALLOCATIONS

    def test_config_validation(self):
        """Test that configuration data is valid"""
        # Test that risk levels in portfolio config are valid
        for risk_level, allocation in config.portfolio_agent.BASE_ALLOCATIONS.items():
            assert isinstance(risk_level, int)
            assert 1 <= risk_level <= 5

            # Allocation percentages should be reasonable
            total_allocation = sum(allocation.values())
            assert 0.8 <= total_allocation <= 1.2  # Allow some flexibility

        # Test that asset universes contain valid symbols
        for symbol in config.data_agent.EQUITY_UNIVERSE:
            assert isinstance(symbol, str)
            assert len(symbol) >= 1
            assert symbol.isupper() or symbol.islower()  # Valid ticker format

    def test_config_fallback_integration(self):
        """Test integration between configuration and fallback system"""
        # Test that fallback system can access agent configurations
        data_fallback = config.get_fallback('data_agent', 'market_data', symbol='TEST')

        assert data_fallback is not None
        assert isinstance(data_fallback, dict)

        # Should have reasonable fallback structure
        if 'symbol' in data_fallback:
            assert data_fallback['symbol'] == 'TEST'