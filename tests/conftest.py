import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the utilities modules to avoid relative import issues
sys.modules['utils'] = MagicMock()
sys.modules['utils.yahoo'] = MagicMock()
sys.modules['utils.polygon'] = MagicMock()
sys.modules['utils.fred'] = MagicMock()
sys.modules['utils.alpaca'] = MagicMock()

# Mock the coral client
sys.modules['agent.coral_client'] = MagicMock()

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
