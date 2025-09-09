<<<<<<< HEAD
=======

>>>>>>> 4318aabd8f49beaada6d00c27cd8e4790426dc72
# Neural API

A FastAPI-based backend service for stock data, trading, and portfolio management.

---

## 📁 Project Structure

```
api_neural/
├── app.py                    # Main FastAPI application entry point
├── pyproject.toml           # Project dependencies and configuration
├── requirements.txt         # Python dependencies
├── uv.lock                  # UV lock file for dependency management
├── README.md               # Project documentation
├── api/                    # API layer
│   ├── __init__.py
│   ├── api.py              # API router configuration
│   ├── routes/             # API endpoint definitions
│   │   ├── __init__.py
│   │   ├── alpaca.py       # Alpaca trading endpoints
│   │   ├── economy.py      # Economic data endpoints
│   │   ├── stocks.py       # Stock data endpoints
│   │   └── user.py         # User management endpoints
│   ├── schemas/            # Pydantic models for request/response
│   │   ├── __init__.py
│   │   ├── stock.py        # Stock data schemas
│   │   └── user.py         # User schemas
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   └── user.py         # User model
│   ├── services/           # Business logic layer
│   │   └── user_service.py # User-related business logic
│   └── dependencies/       # Dependency injection
│       ├── __init__.py
│       └── db.py           # Database dependencies
├── agent/                  # AI agent functionality
│   ├── agents.py           # Agent implementations
│   ├── mcp.py              # Model Context Protocol
│   ├── tasks.py            # Task definitions
│   ├── tools.py            # Agent tools
│   └── utils.py            # Agent utilities
├── core/                   # Core application configuration
│   ├── __init__.py
│   └── config.py           # Application settings and configuration
└── utils/                  # External service integrations
    ├── alpaca.py           # Alpaca API integration
    ├── fred.py             # FRED API integration
    ├── polygon.py          # Polygon API integration
    └── yahoo.py            # Yahoo Finance integration
```

---

## 🚀 API Endpoints

**User Management**
- `/api/v1/user/*` — User management endpoints

**Stock Data**
- `/api/v1/stocks/*` — Stock data endpoints
  - `GET /api/v1/stocks/` — Get all stocks in the watchlist
  - `GET /api/v1/stocks/{symbol}` — Get data for a specific stock

**Alpaca Trading**
- `/api/v1/alpaca/*` — Alpaca trading endpoints
  - `GET /api/v1/alpaca/` — Get Alpaca account information

**Economy Data**
- `/api/v1/economy/*` — Economic data endpoints

### 🤖 AI Agent Features

The Neural API includes AI agent functionality for automated trading and analysis:

- **Model Context Protocol (MCP)** — Standardized AI model integration
- **Automated Trading Agents** — AI-powered trading strategies
- **Task Management** — Scheduled and event-driven tasks
- **Tool Integration** — External tool and service connectivity

---

## ⚡️ Setup & Installation

1. **Clone the repository**
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** (see below for example)
5. **Run the application**
   ```bash
   uvicorn app:app --reload
   ```

### Example `.env` file
```env
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

---

## 🛠 Development

### Key Dependencies

- **fastapi** — Modern, fast web framework
- **fastapi-cache2** — Caching for FastAPI endpoints
- **httpx** — HTTP client for async requests
- **pydantic** — Data validation and settings management
- **uvicorn** — ASGI server
- **yfinance** — Yahoo Finance API wrapper

### External Service Integrations

The project integrates with several external financial data providers:

- **Alpaca** — Trading platform for stock trading operations
- **Polygon** — Real-time and historical market data
- **Yahoo Finance** — Stock quotes and financial data
- **FRED** — Federal Reserve Economic Data
- **Supabase** — Database and authentication services

---

## ⚡️ Setting Up with [uv](https://github.com/astral-sh/uv)

If you have a `pyproject.toml` file, you can use `uv` for fast dependency management:

1. **Install uv**
   ```bash
   pip install uv
   # Or with pipx:
   pipx install uv
   ```
2. **Create a virtual environment and install dependencies**
   ```bash
   uv venv
   uv pip install -r requirements.txt      # If you have requirements.txt
   uv pip install -e .                    # For editable installs (if needed)
   uv pip install --all-extras            # To install all optional dependencies
   # Or, to install directly from pyproject.toml:
   uv pip install -r pyproject.toml
   ```
3. **Activate the virtual environment**
   ```bash
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

For more details, see the [uv documentation](https://github.com/astral-sh/uv)

---

## ➕ Adding a New Dependency

```bash
pip install new-package
pip freeze > requirements.txt
```

<<<<<<< HEAD
## API Documentation

Once the application is running, you can access:
- Interactive API documentation: http://localhost:8000/docs
- Alternative API documentation: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/api/v1/openapi.json

## Project Structure Benefits
=======
---

## 📚 API Documentation

Once the application is running, you can access:

- [Swagger UI](http://localhost:8000/docs) — Interactive API documentation
- [ReDoc](http://localhost:8000/redoc) — Alternative API documentation
- [OpenAPI Schema](http://localhost:8000/api/v1/openapi.json)

---

## 🏗 Project Structure Benefits
>>>>>>> 4318aabd8f49beaada6d00c27cd8e4790426dc72

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

<<<<<<< HEAD
4. **Configuration Management**: Centralized settings in `core/config.py`
=======
4. **Configuration Management**
   - Centralized settings in `core/config.py`
>>>>>>> 4318aabd8f49beaada6d00c27cd8e4790426dc72
   - Environment variables loaded from `.env` file
   - Settings validated with Pydantic
