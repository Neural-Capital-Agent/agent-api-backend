import sys
import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load real environment variables from .env file
load_dotenv()

# Mock the utilities modules to avoid relative import issues
utils_mock = MagicMock()
sys.modules['utils'] = utils_mock
sys.modules['utils.yahoo'] = MagicMock()
sys.modules['utils.polygon'] = MagicMock()
sys.modules['utils.fred'] = MagicMock()
sys.modules['utils.alpaca'] = MagicMock()
sys.modules['utils.rate_limiter'] = MagicMock()
sys.modules['utils.supabase'] = MagicMock()

# Set up rate limiter mock attributes
rate_limiter_mock = MagicMock()
rate_limiter_mock.llm_rate_limiter = MagicMock()
rate_limiter_mock.setup_user_tier = MagicMock()
rate_limiter_mock.USER_TIER_CONFIGS = {}
sys.modules['utils.rate_limiter'] = rate_limiter_mock

# Mock the coral client
sys.modules['agent.coral_client'] = MagicMock()

# Mock agent modules
agent_mock = MagicMock()
sys.modules['agent'] = agent_mock
sys.modules['agent.agents'] = MagicMock()

# Mock mistral client
mistral_mock = MagicMock()
mistral_mock.MistralLLMClient = MagicMock()
mistral_mock.get_mistral_client = MagicMock()
mistral_mock.ChatMessage = MagicMock()
mistral_mock.ChatCompletionResponse = MagicMock()
sys.modules['agent.mistral_client'] = mistral_mock

# Mock agent config with realistic data structures
class MockDataAgentConfig:
    EQUITY_UNIVERSE = ['SPY', 'QQQ', 'VTI', 'AAPL', 'MSFT']
    FIXED_INCOME_UNIVERSE = ['TLT', 'IEF', 'SHY', 'AGG']
    ALTERNATIVES_UNIVERSE = ['GLD', 'SLV', 'VNQ', 'REIT']
    CRYPTO_UNIVERSE = ['BTC', 'ETH', 'ADA']
    MACRO_INDICATORS = {
        'GDP': 'GDP Growth Rate',
        'INFLATION': 'Consumer Price Index',
        'UNEMPLOYMENT': 'Unemployment Rate'
    }

class MockPortfolioAgentConfig:
    BASE_ALLOCATIONS = {
        1: {'equity': 0.3, 'fixed_income': 0.6, 'alternatives': 0.1},
        2: {'equity': 0.4, 'fixed_income': 0.5, 'alternatives': 0.1},
        3: {'equity': 0.6, 'fixed_income': 0.3, 'alternatives': 0.1},
        4: {'equity': 0.7, 'fixed_income': 0.2, 'alternatives': 0.1},
        5: {'equity': 0.8, 'fixed_income': 0.1, 'alternatives': 0.1}
    }
    RISK_MODELS = ['modern_portfolio_theory', 'black_litterman']
    OPTIMIZATION_CONSTRAINTS = {'max_position': 0.3, 'min_position': 0.01}

class MockPlannerAgentConfig:
    GOAL_STRATEGIES = {
        'retirement': {'horizon': 30, 'risk_tolerance': 'moderate'},
        'house_down_payment': {'horizon': 5, 'risk_tolerance': 'conservative'}
    }
    GOAL_KEYWORDS = {
        'retirement': ['retire', 'retirement', '401k', 'pension'],
        'house': ['house', 'home', 'down payment', 'mortgage']
    }
    GLIDE_PATH_SETTINGS = {'start_equity': 0.9, 'end_equity': 0.4}

class MockExplainabilityAgentConfig:
    JARGON_DICTIONARY = {
        'beta': 'Market risk measure',
        'alpha': 'Excess return measure',
        'sharpe_ratio': 'Risk-adjusted return metric'
    }
    EXPLANATION_TEMPLATES = ['simple', 'detailed', 'technical']

class MockConfig:
    def __init__(self):
        self.data_agent = MockDataAgentConfig()
        self.portfolio_agent = MockPortfolioAgentConfig()
        self.planner_agent = MockPlannerAgentConfig()
        self.explainability_agent = MockExplainabilityAgentConfig()
        self.environment = 'development'
        self.base_config = {
            'database_url': 'test://db',
            'api_keys': {'test': 'key'}
        }

    def should_use_fallbacks(self):
        return True

    def get_fallback(self, *args, **kwargs):
        return {'fallback_data': 'available'}

class MockConfigManager:
    def __init__(self):
        self._config = MockConfig()

    def should_use_fallbacks(self):
        return True

    def get_config(self):
        return self._config

config_instance = MockConfig()
config_mock = MagicMock()
config_mock.config = config_instance
config_mock.ConfigManager = MockConfigManager
sys.modules['agent.config'] = config_mock

# Also set up agent module to have config attribute
agent_module_mock = MagicMock()
agent_module_mock.config = config_instance
sys.modules['agent'].config = config_instance

# Create mock agent classes (after config is defined)
class MockDataAgent:
    def __init__(self, *args, **kwargs):
        self.config = config_instance

class MockPortfolioAgent:
    def __init__(self, *args, **kwargs):
        self.config = config_instance

class MockPlannerAgent:
    def __init__(self, *args, **kwargs):
        self.config = config_instance

class MockExplainabilityAgent:
    def __init__(self, *args, **kwargs):
        self.config = config_instance

agents_mock = MagicMock()
agents_mock.DataAgent = MockDataAgent
agents_mock.PortfolioAgent = MockPortfolioAgent
agents_mock.PlannerAgent = MockPlannerAgent
agents_mock.ExplainabilityAgent = MockExplainabilityAgent
sys.modules['agent.agents'] = agents_mock

# Mock agent shared
shared_mock = MagicMock()
shared_mock.ErrorHandler = MagicMock()
shared_mock.safe_coral_invoke = MagicMock()
sys.modules['agent.shared'] = shared_mock

# Mock Supabase before any imports
supabase_mock = MagicMock()
sys.modules['supabase'] = MagicMock()
sys.modules['supabase'].create_client = MagicMock(return_value=supabase_mock)

# Mock database dependencies
db_mock = MagicMock()
db_mock.supabase = supabase_mock
sys.modules['api.dependencies.db'] = db_mock

# Mock services that depend on supabase
sys.modules['api.services'] = MagicMock()
sys.modules['api.services.user_service'] = MagicMock()

# Create mock models
from unittest.mock import MagicMock
from enum import Enum

class MockRiskLevel(Enum):
    CONSERVATIVE = 1
    BALANCED_CONSERVATIVE = 2
    BALANCED = 3
    GROWTH = 4
    AGGRESSIVE = 5

class MockGoalType(Enum):
    HOUSE_DOWN_PAYMENT = "house_down_payment"
    RETIREMENT = "retirement"
    EMERGENCY_FUND = "emergency_fund"
    CHILD_EDUCATION = "child_education"

# Add to sys.modules
models_mock = MagicMock()
models_mock.RiskLevel = MockRiskLevel
models_mock.GoalType = MockGoalType
models_mock.MarketData = MagicMock
models_mock.MacroData = MagicMock
models_mock.MacroSignal = MagicMock
models_mock.MacroSignals = MagicMock
models_mock.ExplanationResponse = MagicMock

sys.modules['agent.models'] = models_mock
