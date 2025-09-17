# Neural Capital Financial Agents API

A comprehensive FastAPI-based backend service for financial data, AI-powered portfolio management, and multi-agent financial advisory through Coral Protocol integration.

## 🌊 Coral Protocol Integration

This project implements a full **Coral Protocol** ecosystem for multi-agent financial services, enabling:

- **Agent Registration & Discovery** - Automatic agent registration with Coral Server
- **Multi-Agent Orchestration** - Coordinate multiple financial agents seamlessly
- **Real-time Agent Communication** - Inter-agent messaging and collaboration
- **Coral Studio Integration** - Visual interface for agent management and testing
- **Blockchain Verification** - Agent action verification and audit trails

## 🤖 Financial Agents

### Available Agents

1. **Data Agent** (`data_agent`)
   - Real-time market data aggregation
   - Macro-economic indicator collection
   - Market context analysis and signal validation
   - Asset universe data management

2. **Portfolio Agent** (`portfolio_agent`)
   - Algorithmic portfolio optimization
   - Risk-based asset allocation
   - Dynamic rebalancing strategies
   - Performance analytics and backtesting

3. **Planner Agent** (`planner_agent`)
   - Natural language goal interpretation
   - Investment strategy generation
   - Lifecycle-based financial planning
   - Goal parsing and validation

4. **Explainability Agent** (`explainability_agent`)
   - Financial jargon translation
   - Decision rationale generation
   - Risk communication in plain English
   - Investment recommendation explanations

### Agent Capabilities

Each agent provides specialized financial services through standardized Coral Protocol interfaces:

- **Health Monitoring** - Real-time agent status and performance metrics
- **Method Invocation** - Standardized API for agent interactions
- **Capability Discovery** - Dynamic service discovery and composition
- **Error Handling** - Robust error recovery and fallback mechanisms

## 🏗️ Architecture Overview

### Enhanced Neural Capital System Architecture

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                             MANAGEMENT LAYER                                ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────────┐   ║
║   │  Coral Studio   │   │  CrewAI         │   │  MCP Tools &            │   ║
║   │  Monitoring     │   │  Dashboard      │   │  Context Sharing        │   ║
║   │  Interface      │   │  Workflows      │   │  Standards              │   ║
║   └─────────────────┘   └─────────────────┘   └─────────────────────────┘   ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                       │
                                       ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                            ORCHESTRATION LAYER                              ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────────┐ ║
║  │  Coral Protocol    │  │  CrewAI            │  │  MCP Framework         │ ║
║  │                    │  │                    │  │                        │ ║
║  │  • Verification    │  │  • Workflows       │  │  • Tool Management     │ ║
║  │  • Payments        │  │  • Coordination    │  │  • Context Sharing     │ ║
║  │  • Discovery       │  │  • Task Mgmt       │  │  • Standards           │ ║
║  └────────────────────┘  └────────────────────┘  └────────────────────────┘ ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                       │
                                       ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                          NEURAL CAPITAL AGENTS                              ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ ║
║ │  Data Agent     │ │  Portfolio      │ │  Planner        │ │ Explain     │ ║
║ │                 │ │  Agent          │ │  Agent          │ │ Agent       │ ║
║ │  • Market Data  │ │  • Optimization │ │  • Goal Parse   │ │ • Explain   │ ║
║ │  • Macro Econ   │ │  • Rebalancing  │ │  • Planning     │ │ • Translate │ ║
║ │  • Validation   │ │  • Analytics    │ │  • Strategies   │ │ • Rationale │ ║
║ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────┘ ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                       │
                                       ▼
╔═════════════════════════════════════════════════════════════════════════════╗
║                               DATA SOURCES                                  ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ ║
║ │  Yahoo Finance  │ │  FRED Economic  │ │  Polygon        │ │  Mistral AI │ ║
║ │  Market Data    │ │  Indicators     │ │  Market Data    │ │  Language   │ ║
║ │  (via MCP)      │ │  (via MCP)      │ │  (via MCP)      │ │  (via MCP)  │ ║
║ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────┘ ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

### System Components

#### **Management Layer**
- **Coral Studio**: Visual monitoring and agent management interface
- **CrewAI Dashboard**: Workflow orchestration and task management
- **MCP Tools**: Context sharing and tool standardization

#### **Orchestration Layer**
- **Coral Protocol**: Agent verification, payments, and discovery
- **CrewAI**: Multi-agent workflows and coordination
- **MCP (Model Context Protocol)**: Tool management and context standards

#### **Agent Layer**
- **Data Agent**: Market data aggregation and macro-economic analysis
- **Portfolio Agent**: Optimization algorithms and rebalancing strategies
- **Planner Agent**: Goal parsing and investment planning
- **Explainability Agent**: Decision rationale and jargon translation

#### **Data Layer**
- **Financial Data Sources**: Real-time and historical market data
- **AI Services**: Natural language processing and machine learning
- **External APIs**: Third-party integrations via MCP standards

## 📁 Project Structure

```
agent-api-backend/
├── app.py                          # Main FastAPI application with Coral integration
├── requirements.txt                # Python dependencies
├── docker-compose.yml             # Local development setup
├── Dockerfile                     # Production container setup
├── DEPLOYMENT_GUIDE.md            # Comprehensive deployment instructions
├──
├── agent/                          # Financial Agents & Coral Protocol
│   ├── coral_server.py            # Coral Protocol Server implementation
│   ├── coral_client.py            # Coral Protocol client for agent communication
│   ├── coral_registry.py          # Agent registration and discovery service
│   ├── coral_studio.html          # Custom Coral Studio web interface
│   ├── data_agent.py              # Market data and economic indicators
│   ├── portfolio_agent.py         # Portfolio optimization and rebalancing
│   ├── planner_agent.py           # Financial planning and goal interpretation
│   ├── explainability_agent.py    # Decision explanations and jargon translation
│   ├── crew_agents.py             # CrewAI orchestrated workflows
│   ├── models.py                  # Coral Protocol data models
│   ├── shared.py                  # Shared agent functionality
│   └── mistral_client.py          # LLM integration for natural language processing
│
├── api/                           # REST API Layer
│   ├── api.py                     # API router configuration
│   ├── routes/                    # API endpoint definitions
│   │   ├── agents.py              # Individual agent endpoints
│   │   ├── crew.py                # CrewAI workflow endpoints
│   │   ├── coral.py               # Coral Protocol management endpoints
│   │   ├── stocks.py              # Stock data endpoints
│   │   ├── economy.py             # Economic data endpoints
│   │   └── llm.py                 # LLM interaction endpoints
│   ├── schemas/                   # Pydantic models for request/response
│   └── middleware/                # Rate limiting and authentication
│
├── core/                          # Core application configuration
│   └── config.py                  # Application settings with Coral Protocol config
│
├── utils/                         # External service integrations
│   ├── fred_real.py               # Federal Reserve Economic Data
│   ├── polygon.py                 # Polygon.io market data
│   ├── yahoo.py                   # Yahoo Finance integration
│   ├── supabase.py                # Database and authentication
│   └── rate_limiter.py            # API rate limiting
│
└── tests/                         # Test suites
    └── test_e2e_demo.py           # End-to-end testing framework
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- Node.js (for official Coral Studio)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Neural-Capital-Agent/api_neural.git
   cd agent-api-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Start the application**
   ```bash
   uvicorn app:app --reload
   ```

The application will start with:
- **Main API**: http://localhost:8000
- **Coral Protocol Server**: http://localhost:5555
- **API Documentation**: http://localhost:8000/docs
- **Coral Studio (Custom)**: http://localhost:5555/studio

### Using Official Coral Studio

For the full Coral Studio experience:

```bash
# In a separate terminal
npx @coral-protocol/coral-studio
```

Then configure it to connect to: `http://localhost:5555`

## 🌊 Coral Protocol Features

### Agent Management

- **Automatic Registration** - All agents register with Coral Server on startup
- **Health Monitoring** - Real-time agent status and performance tracking
- **Service Discovery** - Dynamic discovery of available agents and capabilities
- **Load Balancing** - Distribute requests across healthy agent instances

### Multi-Agent Workflows

- **CrewAI Integration** - Orchestrated multi-agent workflows
- **Sequential Processing** - Step-by-step agent collaboration
- **Parallel Execution** - Concurrent agent operations for performance
- **Error Recovery** - Robust error handling and fallback strategies

### Studio Interface

- **Visual Agent Management** - See all agents, their status, and capabilities
- **Interactive Testing** - Send test requests to agents and view responses
- **Real-time Logs** - Monitor agent interactions and system events
- **Session Management** - Create and manage testing sessions

## 🎯 API Endpoints

### Core Financial Services

- `GET /` - API overview and status
- `GET /health` - Comprehensive system health check
- `GET /api/v1/agents/` - List all available financial agents

### Individual Agent Endpoints

- `/api/v1/agents/data/` - Data Agent endpoints
- `/api/v1/agents/portfolio/` - Portfolio Agent endpoints
- `/api/v1/agents/planner/` - Planner Agent endpoints
- `/api/v1/agents/explainer/` - Explainability Agent endpoints

### CrewAI Workflows

- `/api/v1/crew/market-analysis` - Multi-agent market analysis
- `/api/v1/crew/portfolio-advisory` - Complete portfolio advisory workflow
- `/api/v1/crew/quick-advice` - Instant financial guidance

### Coral Protocol Management

- `/api/v1/coral/status` - Coral registry status and agent health
- `/api/v1/coral/register` - Manual agent registration
- `/api/v1/coral/discover` - Discover available agents in network

### LLM & AI Services

- `/api/v1/llm/` - Direct LLM interactions
- `/api/v1/llm/health` - LLM service status

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Neural Capital API

# Coral Protocol Configuration
CORAL_SERVER_URL=http://localhost:5555
CORAL_API_BASE_URL=http://localhost:8000

# Financial Data Sources
POLYGON_API_KEY=your_polygon_api_key
FRED_KEY=your_fred_api_key

# Database Configuration (Optional)
URL_SUPABASE=your_supabase_url
KEY_SUPABASE=your_supabase_key

# AI/LLM Configuration
MISTRAL_API_KEY=your_mistral_api_key

# Alpaca Trading (Optional)
API_KEY_ALPACA=your_alpaca_api_key
API_SECRET_ALPACA=your_alpaca_api_secret
```

### Rate Limiting Configuration

The API includes comprehensive rate limiting with multiple tiers:

- **Basic Tier**: 50 requests/day, 10/hour, 3/minute, 100 LLM credits
- **Premium Tier**: 200 requests/day, 50/hour, 10/minute, 500 LLM credits
- **Enterprise Tier**: 1000 requests/day, 200/hour, 50/minute, 2000 LLM credits

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build the image
docker build -t neural-capital-api .

# Run the container
docker run -p 8000:8000 -p 5555:5555 --env-file .env neural-capital-api
```

## ☁️ Cloud Deployment

### Render.com (One-Click)

1. Fork this repository
2. Connect to [Render.com](https://render.com)
3. Create new Blueprint from your repository
4. Configure environment variables in Render dashboard
5. Deploy automatically using `render.yaml`

### Manual Cloud Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions on:

- AWS ECS deployment
- Google Cloud Run
- Azure Container Instances
- Railway deployment
- Heroku deployment

## 🧪 Testing

### End-to-End Testing

```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_e2e_demo.py -v

# Test Coral Protocol integration
curl http://localhost:5555/agents
curl http://localhost:8000/api/v1/coral/status
```

### Manual Testing with Coral Studio

1. Start the application
2. Open Coral Studio at http://localhost:5555/studio
3. Test agent interactions:
   - Select an agent (e.g., data_agent)
   - Choose a method (e.g., health_check)
   - Send test parameters
   - View real-time responses

## 🔍 Monitoring & Observability

### Health Checks

- **System Health**: `/health` - Overall system status
- **Agent Health**: `/api/v1/agents/health` - Individual agent status
- **Coral Health**: `/api/v1/coral/status` - Coral Protocol status
- **LLM Health**: `/api/v1/llm/health` - AI service status

### Logging

The application provides structured logging with multiple levels:

- **INFO**: Agent registrations, successful operations
- **WARNING**: Partial failures, degraded performance
- **ERROR**: Operation failures, connection issues
- **DEBUG**: Detailed execution traces

### Metrics

Monitor key metrics through health endpoints:

- Request rates and response times
- Agent availability and performance
- LLM usage and credit consumption
- Coral Protocol network health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow conventional commit format
- Add tests for new features
- Update documentation for API changes
- Ensure all agents register properly with Coral Protocol

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- **Issues**: [GitHub Issues](https://github.com/Neural-Capital-Agent/api_neural/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Coral Protocol**: [Official Documentation](https://docs.coralprotocol.org)

## 🛠️ Tech Stack

### Backend & API
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server for production deployment
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation and settings management
- **[httpx](https://www.python-httpx.org/)** - Async HTTP client for external API calls

### AI & Machine Learning
- **[Coral Protocol](https://docs.coralprotocol.org/)** - Multi-agent orchestration and communication
- **[CrewAI](https://github.com/joaomdmoura/crewAI)** - Multi-agent workflow automation
- **[Mistral AI](https://mistral.ai/)** - Large Language Model for natural language processing
- **Scikit-learn** - Machine learning algorithms for portfolio optimization

### Financial Data Sources
- **[Yahoo Finance](https://pypi.org/project/yfinance/)** - Stock quotes and financial data
- **[Polygon.io](https://polygon.io/)** - Real-time and historical market data
- **[FRED API](https://fred.stlouisfed.org/)** - Federal Reserve Economic Data
- **[Alpaca](https://alpaca.markets/)** - Commission-free trading platform

### Database & Storage
- **[Supabase](https://supabase.com/)** - Open source Firebase alternative
- **PostgreSQL** - Relational database for structured data
- **Redis** - In-memory cache for session management and rate limiting

### Development & Deployment
- **[Docker](https://www.docker.com/)** - Containerization for consistent deployments
- **[Docker Compose](https://docs.docker.com/compose/)** - Multi-container application orchestration
- **[pytest](https://pytest.org/)** - Testing framework for comprehensive test coverage
- **[Black](https://black.readthedocs.io/)** - Code formatting for consistent style

### Monitoring & Observability
- **[FastAPI-Cache](https://github.com/comeuplater/fastapi_cache)** - Caching layer for improved performance
- **Python Logging** - Structured logging with multiple output formats
- **Health Check Endpoints** - Comprehensive system monitoring

### Security & Rate Limiting
- **Custom Rate Limiter** - Multi-tier API rate limiting system
- **CORS Middleware** - Cross-origin resource sharing configuration
- **Environment Variables** - Secure configuration management

### Frontend Integration
- **[Coral Studio](https://docs.coralprotocol.org/concepts/coral-studio)** - Official visual interface for agent management
- **Custom HTML/CSS/JS** - Built-in studio interface for development
- **OpenAPI/Swagger** - Automatic API documentation generation

### Cloud Platforms (Supported)
- **[Render.com](https://render.com/)** - Recommended cloud deployment platform
- **[Railway](https://railway.app/)** - Alternative cloud deployment
- **[Heroku](https://heroku.com/)** - Platform-as-a-Service deployment
- **AWS ECS** - Enterprise container orchestration
- **Google Cloud Run** - Serverless container deployment
- **Azure Container Instances** - Microsoft cloud containers

### Package Management
- **pip** - Python package installer
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager (optional)
- **requirements.txt** - Dependency specification

## 🔮 Roadmap

- [ ] Advanced portfolio optimization algorithms
- [ ] Real-time market data streaming
- [ ] Multi-exchange trading support
- [ ] Enhanced AI model integration
- [ ] Mobile app integration
- [ ] Advanced risk management tools
- [ ] Institutional trading features

---

**Built with ❤️ using FastAPI, Coral Protocol, and AI-powered financial intelligence.**