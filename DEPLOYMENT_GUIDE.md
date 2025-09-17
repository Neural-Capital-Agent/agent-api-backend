# FastAPI Deployment Guide

## 🚀 Deployment Options for Your Neural Capital API

### Current Setup
Your FastAPI application is currently configured to run locally with:
- **Main App**: `app.py`
- **ASGI Server**: Uvicorn
- **Dependencies**: Managed with `uv` and `pyproject.toml`
- **Environment**: Virtual environment with `.env` file

---

## 1. 🐳 Docker Deployment (Recommended for Production)

### Create Dockerfile
```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  neural-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - URL_SUPABASE=${URL_SUPABASE}
      - KEY_SUPABASE=${KEY_SUPABASE}
      - API_KEY_ALPACA=${API_KEY_ALPACA}
      - API_SECRET_ALPACA=${API_SECRET_ALPACA}
      - POLYGON_API_KEY=${POLYGON_API_KEY}
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Add PostgreSQL if not using Supabase
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: neural_api
  #     POSTGRES_USER: neural_user
  #     POSTGRES_PASSWORD: your_password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
```

### Docker Commands
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f neural-api

# Stop
docker-compose down
```

---

## 2. ☁️ Cloud Platform Deployment

### Option A: Railway (Easiest)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables
railway variables set URL_SUPABASE=your_value
railway variables set API_KEY_ALPACA=your_value
# ... set other variables
```

### Option B: Render
1. Connect your GitHub repository
2. Choose "Web Service"
3. Set build command: `pip install uv && uv pip install --system -r pyproject.toml`
4. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in Render dashboard

### Option C: Heroku
```bash
# Create requirements.txt from pyproject.toml
uv pip compile pyproject.toml -o requirements.txt

# Create Procfile
echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.12.0" > runtime.txt

# Deploy
heroku create your-app-name
heroku config:set URL_SUPABASE=your_value
git push heroku main
```

### Option D: DigitalOcean App Platform
1. Connect repository
2. Set runtime to Python
3. Configure environment variables
4. Set run command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

---

## 3. 🖥️ VPS/Cloud Server Deployment

### Using systemd (Linux)
```bash
# Create systemd service file
sudo nano /etc/systemd/system/neural-api.service
```

```ini
[Unit]
Description=Neural Capital API
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable neural-api
sudo systemctl start neural-api
sudo systemctl status neural-api
```

### Using PM2 (Process Manager)
```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
nano ecosystem.config.js
```

```javascript
module.exports = {
  apps: [{
    name: 'neural-api',
    script: 'uvicorn',
    args: 'app:app --host 0.0.0.0 --port 8000 --workers 4',
    instances: 2,
    exec_mode: 'cluster',
    env: {
      URL_SUPABASE: process.env.URL_SUPABASE,
      API_KEY_ALPACA: process.env.API_KEY_ALPACA,
      // ... other env vars
    }
  }]
}
```

```bash
# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 4. 🔧 Production Configuration

### Environment Variables
Create a production `.env` file:
```env
# Database
URL_SUPABASE=your_production_supabase_url
KEY_SUPABASE=your_production_supabase_key

# API Keys
API_KEY_ALPACA=your_production_alpaca_key
API_SECRET_ALPACA=your_production_alpaca_secret
POLYGON_API_KEY=your_production_polygon_key

# App Settings
PROJECT_NAME=Neural Capital API
DEBUG=False
SECRET_KEY=your-secret-key-here

# CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

### Production ASGI Server
For production, use a production ASGI server:

```bash
# Install production server
pip install gunicorn uvicorn[standard]

# Run with gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### SSL/TLS Setup
```bash
# Using certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 5. 📊 Monitoring & Logging

### Health Check Endpoint
Add to your FastAPI app:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)
```

---

## 6. 🔒 Security Best Practices

### API Security
- Use HTTPS in production
- Implement proper authentication/authorization
- Rate limiting is already configured
- Validate all inputs
- Use environment variables for secrets

### Database Security
- Use connection pooling
- Implement proper database migrations
- Regular backups
- Monitor database performance

---

## 7. 🚀 Quick Deployment Commands

### For Railway (Simplest)
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### For Docker
```bash
docker build -t neural-api .
docker run -p 8000:8000 --env-file .env neural-api
```

### For Local Production
```bash
pip install gunicorn uvicorn[standard]
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 📝 Next Steps

1. Choose your deployment platform
2. Set up environment variables
3. Configure domain and SSL
4. Set up monitoring
5. Test all endpoints
6. Configure backups

Would you like me to help you set up any specific deployment option?