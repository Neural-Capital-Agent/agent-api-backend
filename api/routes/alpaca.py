from fastapi import APIRouter, Depends
from utils.alpaca import Alpaca

router = APIRouter(tags=["alpaca"])

@router.get("/")
async def get_alpaca_data():
    """
    Retrieve account data from Alpaca.
    """
    return {"data": Alpaca.requestAlpaca("GET", "/v2/account")}

# Add more alpaca-related endpoints as needed
