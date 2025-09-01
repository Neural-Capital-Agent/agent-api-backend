from pydantic import BaseModel
from typing import Optional, List

class StockBase(BaseModel):
    symbol: str
    
class StockData(StockBase):
    current_price: Optional[float] = None
    price: Optional[float] = None
    name: Optional[str] = None
    
class StocksResponse(BaseModel):
    stocks: List[StockData]
    
class StockResponse(BaseModel):
    stock: StockData
