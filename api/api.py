from fastapi import APIRouter
from api.routes import stocks, alpaca

api_router = APIRouter()

api_router.include_router(stocks.router, prefix="/user")
api_router.include_router(stocks.router, prefix="/stocks")
api_router.include_router(alpaca.router, prefix="/alpaca")


