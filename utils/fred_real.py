"""
Real FRED API integration - requires FRED API key
"""
import os
import httpx
from typing import List, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

FRED_API_KEY = os.getenv('FRED_KEY')
FRED_BASE_URL = "https://api.stlouisfed.org/fred"


class FredAPIClient:
    """Real FRED API client for economic data"""

    def __init__(self):
        self.api_key = FRED_API_KEY
        if not self.api_key:
            raise ValueError("FRED_KEY environment variable required for real FRED API access")

    async def get_series_data(self, series_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get real FRED series data"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{FRED_BASE_URL}/series/observations"
                params = {
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "limit": limit,
                    "sort_order": "desc"
                }

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                observations = data.get("observations", [])

                # Convert to our format
                result = []
                for obs in observations:
                    try:
                        value = float(obs["value"])
                        date = datetime.strptime(obs["date"], "%Y-%m-%d")
                        result.append({
                            "date": date.isoformat(),
                            "value": value
                        })
                    except (ValueError, TypeError):
                        # Skip invalid data points
                        continue

                return result

        except Exception as e:
            raise Exception(f"FRED API error for {series_id}: {str(e)}")


# Global FRED client
fred_client = None

def get_fred_client():
    """Get FRED client instance"""
    global fred_client
    if fred_client is None:
        fred_client = FredAPIClient()
    return fred_client

class fred:
    """FRED API integration for economic data"""

    @staticmethod
    async def get_fred_data(series_id: str):
        """Get FRED data for a series - real API only, no fallback data"""
        # Check if we have API key
        if not FRED_API_KEY:
            raise Exception(f"FRED API key required. Set FRED_KEY environment variable to access real data for {series_id}")

        try:
            client = get_fred_client()
            # client.get_series_data is async
            data = await client.get_series_data(series_id)
            if not data:
                raise Exception(f"No data returned from FRED API for {series_id}")
            return data
        except Exception as e:
            # Don't return fake data - let the calling code handle the error
            raise Exception(f"Failed to fetch real FRED data for {series_id}: {str(e)}")