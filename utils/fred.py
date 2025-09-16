from core.config import settings
import httpx

async def get_series_observations(series_id: str):
    url = f"{settings.FRED_URL}/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": settings.FRED_KEY,
        "file_type": "json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def get_multiple_series(series_ids: list[str]):
    results = {}
    for sid in series_ids:
        try:
            data = await get_series_observations(sid)
            results[sid] = data.get("observations", [])
        except Exception as e:
            results[sid] = {"error": str(e)}
    return results

class fred:
    """FRED API integration for economic data"""

    @staticmethod
    def get_fred_data(series_id: str):
        """Get FRED data for a series - REQUIRES FRED API KEY"""
        # No mock data - must use real FRED API
        raise NotImplementedError(f"FRED API integration required for series {series_id}. Set FRED_KEY environment variable and implement real API calls.")