#!/usr/bin/env python3
"""
Test imports to check for missing modules
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    
    # Test the main API router import
    from api.api import api_router
    print("✅ api.api imported successfully!")
    
    # Test specific route imports
    from api.routes import tier_management
    print("✅ tier_management imported successfully!")
    
    from api.routes.shared import get_user_id
    print("✅ shared.get_user_id imported successfully!")
    
    print("🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Other Error: {e}")
    sys.exit(1)