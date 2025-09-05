from mcp.server.fastmcp import FastMCP
import os
import requests
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("Broker Service")


@mcp.tool()
def get_economy_context() -> dict:
    url="http://localhost:8000/api/v1/economy"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve economy context"}


@mcp.tool()
def get_stocks_context() -> dict:
    url="http://localhost:8000/api/v1/stocks"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve stocks context"}


#tools we need
#checkear el estado de la bolsa y la economia genera
#obtener datos de la api de polygon
#realizar analisis de datos
#generar inversiones en alpaca
