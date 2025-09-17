@echo off
REM Neural Capital API Deployment Script for Windows
REM This script helps deploy the FastAPI application using Docker

echo 🚀 Neural Capital API Deployment Script
echo =======================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose is not installed. Please install docker-compose first.
    echo    Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating template...
    (
        echo # Supabase Configuration
        echo URL_SUPABASE=your_supabase_url
        echo KEY_SUPABASE=your_supabase_key
        echo.
        echo # Alpaca Configuration
        echo API_KEY_ALPACA=your_alpaca_api_key
        echo API_SECRET_ALPACA=your_alpaca_api_secret
        echo URL_ALPACA=api.alpaca.markets
        echo.
        echo # Polygon Configuration
        echo POLYGON_API_KEY=your_polygon_api_key
        echo.
        echo # App Configuration
        echo PROJECT_NAME=Neural Capital API
        echo DEBUG=False
        echo SECRET_KEY=your-secret-key-here
        echo.
        echo # CORS Origins (comma-separated)
        echo BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
    ) > .env
    echo ✅ Created .env template. Please edit it with your actual values.
    echo    Then run this script again.
    pause
    exit /b 1
)

echo ✅ Environment file found

REM Create logs directory
if not exist "logs" mkdir logs

echo 🏗️  Building Docker image...
docker-compose build

echo 🚀 Starting services...
docker-compose up -d

echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check if the service is running
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Deployment successful!
    echo.
    echo 🌐 Your API is running at: http://localhost:8000
    echo 📚 API Documentation: http://localhost:8000/docs
    echo 🔄 ReDoc Documentation: http://localhost:8000/redoc
    echo.
    echo 📊 To view logs: docker-compose logs -f neural-api
    echo 🛑 To stop: docker-compose down
    echo 🔄 To restart: docker-compose restart
) else (
    echo ❌ Health check failed. Checking logs...
    docker-compose logs neural-api
    echo.
    echo 💡 Troubleshooting:
    echo    - Check your .env file has correct values
    echo    - Ensure required ports are available
    echo    - Run: docker-compose logs -f neural-api
)

pause