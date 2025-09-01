# Neural API

A FastAPI-based backend service for stock data, trading, and portfolio management.

## Project Structure

```
api_neural/
│
├── api/                  # API specific components
│   ├── routes/           # API route definitions
│   │   ├── stocks.py     # Stock data endpoints
│   │   └── alpaca.py     # Alpaca trading endpoints
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas for request/response validation
│   │   └── stock.py      # Stock data schemas
│   └── dependencies/     # Dependency injection components
│       └── db.py         # Database connection dependencies
│
├── core/                 # Core application components
│   └── config.py         # Application configuration using environment variables
│
├── utils/                # Utility modules for external services
│   ├── alpaca.py         # Alpaca API integration for trading
│   ├── polygon.py        # Polygon API integration for market data
│   ├── Supabase.py       # Supabase integration for database
│   ├── yahoo.py          # Yahoo Finance integration for stock data
│   └── user.py           # User management utilities
│
├── app.py                # FastAPI application entry point
├── requirements.txt      # Project dependencies
└── .env                  # Environment variables (not in version control)
```

## API Endpoints

The API is organized with the following endpoints:

- `/api/v1/user/*` - User management endpoints
- `/api/v1/stocks/*` - Stock data endpoints
  - `GET /api/v1/stocks/` - Get all stocks in the watchlist
  - `GET /api/v1/stocks/{symbol}` - Get data for a specific stock
- `/api/v1/alpaca/*` - Alpaca trading endpoints
  - `GET /api/v1/alpaca/` - Get Alpaca account information

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your configuration:
   ```
   # Supabase Configuration
   URL_SUPABASE=your_supabase_url
   KEY_SUPABASE=your_supabase_key
   
   # Alpaca Configuration
   API_KEY_ALPACA=your_alpaca_api_key
   API_SECRET_ALPACA=your_alpaca_api_secret
   URL_ALPACA=api.alpaca.markets
   
   # Polygon Configuration
   POLYGON_API_KEY=your_polygon_api_key
   ```

5. Run the application:
   ```
   uvicorn app:app --reload
   ```

## Development

### Key Dependencies

This project uses several key libraries:
- `fastapi` - Modern, fast web framework
- `fastapi-cache2` - Caching for FastAPI endpoints
- `httpx` - HTTP client for async requests
- `pydantic` - Data validation and settings management
- `uvicorn` - ASGI server
- `yfinance` - Yahoo Finance API wrapper

To add a new dependency:
```
pip install new-package
pip freeze > requirements.txt
```

## API Documentation

Once the application is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/api/v1/openapi.json

## Project Structure Benefits

This project follows a modular architecture with several advantages:

1. **Separation of Concerns**: Each component has a clear responsibility
   - Routes handle HTTP requests and responses
   - Schemas validate input/output data
   - Utils manage external service integrations

2. **Maintainability**: Easy to add new features or modify existing ones
   - Add new routes by creating files in `/api/routes/`
   - Add new schemas in `/api/schemas/`
   - Register new routes in `api/api.py`

3. **Scalability**: The structure supports growth as the application expands
   - Easily add new external service integrations
   - Add more complex database models as needed

4. **Configuration Management**: Centralized settings in `core/config.py`
   - Environment variables loaded from `.env` file
   - Settings validated with Pydantic
