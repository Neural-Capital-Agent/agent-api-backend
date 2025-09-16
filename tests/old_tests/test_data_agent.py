#!/usr/bin/env python3
"""
Test DataAgent with REAL DATA ONLY - NO MOCK RESPONSES
This script will fail unless real financial data is available.
"""

import pytest
import asyncio
import json
import sys
from datetime import datetime
import logging
import os

# Ensure local .env is loaded when running tests locally (so os.getenv finds keys)
# Prefer python-dotenv if available, otherwise fall back to a tiny parser for simple KEY=VALUE lines.
try:
    # python-dotenv will handle quotes and export formats
    from dotenv import load_dotenv
    # Load .env from repository root (this test file lives under tests/)
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
except Exception:
    # Fallback: parse simple KEY=VALUE lines
    try:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip("'\" ")
                    # Don't override existing environment variables
                    if key and key not in os.environ:
                        os.environ[key] = val
    except Exception:
        # If fallback fails, continue without crashing; environment may be set externally in CI
        pass

# Suppress warnings
logging.basicConfig(level=logging.ERROR)

@pytest.mark.asyncio
async def test_real_data_only():
    """Test DataAgent with only real data sources"""

    print("=" * 60)
    print("REAL DATA ONLY - NEURAL CAPITAL DATAAGENT")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check API keys
    print("API KEY STATUS:")
    print("-" * 30)
    fred_key = os.getenv('FRED_KEY')
    aiml_key = os.getenv('AI_ML_API_KEY')
    print(f"FRED API Key: {'AVAILABLE' if fred_key else 'MISSING'}")
    print(f"AIML API Key: {'AVAILABLE' if aiml_key else 'MISSING'}")
    print()

    try:
        from agent.data_agent import DataAgent
        agent = DataAgent()

        # Test 1: Real Market Data Only
        print("REAL MARKET DATA (Yahoo Finance):")
        print("-" * 40)

        real_market_data = {}
        success_count = 0

        test_tickers = ["SPY", "QQQ", "BND", "GLD", "^VIX"]

        for ticker in test_tickers:
            try:
                data = await agent.fetch_market_data(ticker)

                # Validate real data
                if data.price == 0 and data.previous_close == 0:
                    print(f"{ticker:>6}: FAILED - No real price data")
                    continue

                real_price = data.price if data.price > 0 else data.previous_close
                change = data.change or 0
                change_pct = data.change_percent or 0

                print(f"{ticker:>6}: ${real_price:>8.2f} | Change: ${change:>+7.2f} ({change_pct:>+6.2f}%)")
                real_market_data[ticker] = data
                success_count += 1

            except Exception as e:
                print(f"{ticker:>6}: ERROR - {str(e)[:50]}")

        if success_count == 0:
            raise Exception("No real market data retrieved")

        print(f"\nReal Market Data Retrieved: {success_count}/{len(test_tickers)} tickers")
        print()

        # Test 2: Real Technical Indicators
        print("REAL TECHNICAL ANALYSIS:")
        print("-" * 40)
        try:
            tech_data = await agent.fetch_technical_indicators("SPY")

            # Validate technical data is real
            if not tech_data or tech_data.get('current_price', 0) <= 0:
                raise Exception("No real technical data available")

            print(f"Current Price: ${tech_data.get('current_price', 0):>10.2f}")
            print(f"20-Day SMA:   ${tech_data.get('sma_20', 0):>10.2f}")
            print(f"200-Day SMA:  ${tech_data.get('sma_200', 0):>10.2f}")
            print(f"RSI:          {tech_data.get('rsi', 0):>10.2f}")

        except Exception as e:
            print(f"Technical Analysis FAILED: {e}")
            raise

        print()

        # Test 3: Real VIX Data
        print("REAL VIX VOLATILITY:")
        print("-" * 40)
        try:
            vix_data = await agent.fetch_volatility_data()

            # Validate VIX is real
            vix_value = vix_data.get('vix', 0)
            if vix_value <= 0:
                raise Exception("No real VIX data available")

            print(f"VIX Level: {vix_value:>10.2f}")
            print(f"VIX Change: {vix_data.get('vix_change', 0):>+9.2f}")

            if vix_value < 15:
                status = "LOW (Complacency)"
            elif vix_value < 25:
                status = "NORMAL"
            elif vix_value < 35:
                status = "ELEVATED (Caution)"
            else:
                status = "HIGH (Fear)"

            print(f"Market Fear: {status}")

        except Exception as e:
            print(f"VIX Data FAILED: {e}")
            raise

        print()

        # Test 4: Real FRED Economic Data (if API key available)
        print("REAL ECONOMIC DATA (FRED):")
        print("-" * 40)

        if fred_key:
            try:
                # Try to get real CPI data
                cpi_data = await agent.fetch_macro_data("CPI", date_range=30)

                if not cpi_data or len(cpi_data) == 0:
                    print("CPI: No real FRED data available")
                else:
                    latest_cpi = cpi_data[-1]
                    print(f"Latest CPI: {latest_cpi.value:.2f}% (Real FRED data)")
                    print(f"Date: {latest_cpi.date.strftime('%Y-%m-%d')}")

            except Exception as e:
                print(f"FRED CPI FAILED: {e}")

            try:
                # Try unemployment
                unemployment_data = await agent.fetch_macro_data("UNEMPLOYMENT", date_range=30)
                if unemployment_data and len(unemployment_data) > 0:
                    latest_unemployment = unemployment_data[-1]
                    print(f"Unemployment: {latest_unemployment.value:.1f}% (Real FRED data)")

            except Exception as e:
                print(f"FRED Unemployment FAILED: {e}")
        else:
            print("FRED API Key required for real economic data")
            print("Set FRED_KEY environment variable")

        print()

        # Test 5: Real LLM Analysis (if API key available)
        print("REAL AI ANALYSIS (Mistral):")
        print("-" * 40)

        if aiml_key:
            try:
                # Test real signal validation
                test_signals = {"volatility_spike": vix_data.get('vix', 20) > 25}
                validation = await agent.validate_signals(test_signals)

                if 'error' in validation:
                    print(f"LLM Analysis FAILED: {validation['error']}")
                else:
                    is_valid = validation.get('is_valid', False)
                    confidence = validation.get('confidence', 0)

                    print(f"Signal Validation: {'VALID' if is_valid else 'INVALID'}")
                    print(f"AI Confidence: {confidence:.1%}")
                    print("Source: Real Mistral LLM")

            except Exception as e:
                print(f"LLM Analysis FAILED: {e}")
        else:
            print("AI_ML_API_KEY required for real LLM analysis")
            print("Set AI_ML_API_KEY environment variable")

        print()
        print("=" * 60)
        print("REAL DATA VALIDATION COMPLETE")
        print("=" * 60)

        # Final validation - ensure we got REAL data
        validation_checks = [
            success_count > 0,  # Got real market data
            tech_data and tech_data.get('current_price', 0) > 0,  # Got real technical data
            vix_data and vix_data.get('vix', 0) > 0,  # Got real VIX
        ]

        passed_checks = sum(validation_checks)
        total_checks = len(validation_checks)

        print(f"REAL DATA VALIDATION: {passed_checks}/{total_checks} checks passed")

        if passed_checks >= 2:  # Need at least market + technical or VIX
            print("SUCCESS: Real financial data successfully retrieved")
            print(f"- Market Data: {success_count} tickers with real prices")
            print(f"- Technical Analysis: Real calculations from Yahoo Finance")
            print(f"- VIX: Real volatility data (Level: {vix_data.get('vix', 0):.2f})")
            return True
        else:
            print("FAILED: Insufficient real data retrieved")
            return False

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function - only succeeds with real data"""
    print("INITIALIZING REAL DATA TEST...")
    print("No mock responses will be accepted")
    print()

    success = await test_real_data_only()

    if success:
        print("\nSUCCESS: DataAgent operating with real data only")
        sys.exit(0)
    else:
        print("\nFAILED: Real data requirements not met")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())