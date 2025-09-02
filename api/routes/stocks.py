from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
import asyncio
from api.schemas.stock import StocksResponse, StockResponse
from core.config import settings
from utils.yahoo import yahoo

router = APIRouter(tags=["stocks"])

@router.get("/", response_model=StocksResponse)
@cache(expire=settings.CACHE_EXPIRATION_SECS)
async def read_stocks():
    """
    Retrieve data for all stocks in the watchlist.
    """
    stocks = await asyncio.to_thread(yahoo.fetch_all_stock_data)
    return {"stocks": stocks}

@router.get("/{symbol}", response_model=StockResponse)
@cache(expire=settings.CACHE_EXPIRATION_SECS)
async def read_stock(symbol: str):
    """
    Retrieve data for a specific stock by symbol.
    """
    stock = await asyncio.to_thread(yahoo.fetch_stock_data, symbol)
    return {"stock": stock}
