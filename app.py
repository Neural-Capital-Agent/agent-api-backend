from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import yahoo, alpaca
from utils.Supabase import Supabase # Correct import path for the yahoo class
import asyncio
import os
from dotenv import load_dotenv
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

load_dotenv()

URL = os.getenv("URL_SUPABASE")
KEY = os.getenv("KEY_SUPABASE")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/stocks")
@cache(expire=300)  
async def read_stocks():
    return {"stocks": await asyncio.to_thread(yahoo.fetch_all_stock_data)}


@app.get("/stocks/{symbol}")
@cache(expire=300)
async def read_stock(symbol: str):
    return {"stock": await asyncio.to_thread(yahoo.fetch_stock_data, symbol)}

@app.get("/alpaca")
async def read_alpaca():
    return {"message": "Alpaca API endpoint"}

@app.post("/create_user")
async def create_user(data: dict):
    # Fix: Pass the data dictionary directly without trying to access a 'data' key
    # alpaca_instance = alpaca.Alpaca()
    # alpaca_data=alpaca_instance.create_user(data)
    
    supabase_object = Supabase(URL, KEY)
    supabase_data = await supabase_object.insert_data("users", data)
    return {"message": "User created successfully", "data": data, "supabase_info": supabase_data}