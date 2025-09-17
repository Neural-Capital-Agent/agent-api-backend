#!/bin/bash

# Neural Capital API Deployment Script
# This script helps deploy the FastAPI application using Docker

set -e

echo "🚀 Neural Capital API Deployment Script"
echo "======================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Supabase Configuration
URL_SUPABASE=your_supabase_url
KEY_SUPABASE=your_supabase_key

# Alpaca Configuration
API_KEY_ALPACA=your_alpaca_api_key
API_SECRET_ALPACA=your_alpaca_api_secret
URL_ALPACA=api.alpaca.markets

# Polygon Configuration
POLYGON_API_KEY=your_polygon_api_key

# App Configuration
PROJECT_NAME=Neural Capital API
DEBUG=False
SECRET_KEY=your-secret-key-here

# CORS Origins (comma-separated)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
EOF
    echo "✅ Created .env template. Please edit it with your actual values."
    echo "   Then run this script again."
    exit 1
fi

echo "✅ Environment file found"

# Create logs directory
mkdir -p logs

echo "🏗️  Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if the service is running
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Your API is running at: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "🔄 ReDoc Documentation: http://localhost:8000/redoc"
    echo ""
    echo "📊 To view logs: docker-compose logs -f neural-api"
    echo "🛑 To stop: docker-compose down"
    echo "🔄 To restart: docker-compose restart"
else
    echo "❌ Health check failed. Checking logs..."
    docker-compose logs neural-api
    echo ""
    echo "💡 Troubleshooting:"
    echo "   - Check your .env file has correct values"
    echo "   - Ensure required ports are available"
    echo "   - Run: docker-compose logs -f neural-api"
fi