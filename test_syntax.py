#!/usr/bin/env python3
"""
Quick syntax check for portfolio_agent.py
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agent.core.portfolio_agent import PortfolioAgent
    print("✅ portfolio_agent.py imported successfully!")
    print("✅ PortfolioAgent class is available")
except SyntaxError as e:
    print(f"❌ Syntax Error: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"⚠️  Import Error: {e}")
    print("This might be due to missing dependencies, but syntax is OK")
except Exception as e:
    print(f"❌ Other Error: {e}")
    sys.exit(1)