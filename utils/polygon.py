import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

class polygon:
    """Polygon API integration for financial data"""

    @staticmethod
    def get_stock_data(symbol: str):
        """Get real stock data from Polygon API"""
        if not POLYGON_API_KEY:
            raise Exception(f"POLYGON_API_KEY required. Set POLYGON_API_KEY environment variable to access real data for {symbol}")

        try:
            # Get current market status first
            url = f"https://api.polygon.io/v1/marketstatus/now?apikey={POLYGON_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()

            # Get previous close data
            prev_close_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apikey={POLYGON_API_KEY}"
            prev_response = requests.get(prev_close_url)
            prev_response.raise_for_status()
            prev_data = prev_response.json()

            if prev_data.get("status") != "OK" or not prev_data.get("results"):
                raise Exception(f"No previous close data available for {symbol}")

            result = prev_data["results"][0]

            return {
                "symbol": symbol,
                "current_price": result.get("c"),  # Close price
                "price": result.get("o"),  # Open price as previous
                "high": result.get("h"),
                "low": result.get("l"),
                "volume": result.get("v"),
                "change": result.get("c", 0) - result.get("o", 0),
                "changePercent": ((result.get("c", 0) - result.get("o", 0)) / result.get("o", 1)) * 100 if result.get("o") else 0
            }

        except Exception as e:
            # Don't return dummy data - let the calling code handle the error
            raise Exception(f"Failed to fetch real Polygon data for {symbol}: {str(e)}")