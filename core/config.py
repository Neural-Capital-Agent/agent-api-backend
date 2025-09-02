import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Neural API"
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]  # In production, specify actual origins
    
    # Supabase settings
    SUPABASE_URL: str = os.getenv("URL_SUPABASE", "")
    SUPABASE_KEY: str = os.getenv("KEY_SUPABASE", "")
    
    # Alpaca settings
    ALPACA_API_KEY: str = os.getenv("API_KEY_ALPACA", "")
    ALPACA_API_SECRET: str = os.getenv("API_SECRET_ALPACA", "")
    ALPACA_URL: str = os.getenv("URL_ALPACA", "")
    
    # Polygon settings
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")

    # FRED settings
    FRED_KEY: str = os.getenv("FRED_KEY", "")
    FRED_URL: str = os.getenv("URL_FRED", "")

    # Cache settings
    CACHE_EXPIRATION_SECS: int = 300  # 5 minutes

settings = Settings()
