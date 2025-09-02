from fastapi import APIRouter, Depends
from core.config import settings
import httpx
from utils.fred import get_multiple_series

router = APIRouter(tags=["economy"])


# Get all available macroeconomic series from FRED
@router.get("/")
async def get_all_macro_series(include_core_cpi: bool = False, include_policy_path: bool = False):
    """
    Return a bundle of key macroeconomic series:
    - DGS10: 10Y Treasury
    - DGS2: 2Y Treasury
    - CPIAUCSL: CPI
    - CPILFESL: Core CPI (optional)
    - FEDFUNDS: Fed Funds Rate
    - DFEDTARU: Fed Target Upper Bound (optional)
    """
    base_series = ["DGS10", "DGS2", "CPIAUCSL", "FEDFUNDS"]
    if include_core_cpi:
        base_series.append("CPILFESL")
    if include_policy_path:
        base_series.append("DFEDTARU")

    return await get_multiple_series(base_series)


