# Neural Capital Agents - Coral Protocol Marketplace Deployment Guide

## Overview

This guide walks you through deploying your Neural Capital AI agents to the Coral Protocol marketplace. The process involves wallet setup, agent configuration, Docker deployment, and marketplace submission.

## Prerequisites

- Docker and Docker Compose installed
- Git repository access
- Crossmint API key (provided)
- Beta program registration

## Step-by-Step Deployment Process

### 1. Initial Setup & Wallet Configuration

First, set up your Coral Protocol wallet using the interactive keygen:

```bash
# Download and build Coral Protocol server
git clone https://github.com/Coral-Protocol/coral-server.git
cd coral-server

# Run interactive wallet setup
./gradlew run --args="--interactive-keygen-crossmint"
```

When prompted, enter your Crossmint API key:
```
c2tfcHJvZHVjdGlvbl81ajJNS3IzWDk5U3lwSHJoWEtuU21meFBUMXlBc3E5R0JQaGh5aHlLdUNMYmZiSEdEVmV2clJSakc4VWFrdnhiQ1lCajVxNWpjbW9NSjIzNVQ1Z2drWng5a2tiQTlLczM0bURxMkhxbzFYWGZQNEFHbmZVYW9BR29hUnFwam0yTHRmenFkVHF3SmFVR3pZbzZtWUxYZnVFbkFNOWJwcEZEQk5mQUdpamhCNDFidzlFMTRydGE3RUdIYkFNdXQ5YXlTNHRORE56ZnI0UTRQcjRuejFFYlBaTVAK
```

Complete the authentication process:
1. Visit the provided authentication URL
2. Enter your wallet public address
3. Enter your Crossmint affiliated email

### 2. Build Agent Docker Images

Build Docker images for each Neural Capital agent:

```bash
# Navigate to your agent backend directory
cd /path/to/agent-api-backend

# Build all agent images
docker build -f Dockerfile.data-agent -t neural-capital/data-agent:latest .
docker build -f Dockerfile.portfolio-agent -t neural-capital/portfolio-agent:latest .
docker build -f Dockerfile.explainability-agent -t neural-capital/explainability-agent:latest .
docker build -f Dockerfile.planner-agent -t neural-capital/planner-agent:latest .

# Build the coral server
docker build -f Dockerfile -t neural-capital/coral-server:latest .
```

### 3. Configure Environment Variables

Create a `.env` file with your API keys:

```bash
# Neural Capital Coral Protocol Environment Configuration
# Copy this to .env and fill in your actual API keys

# Data Sources
POLYGON_API_KEY=your_polygon_api_key_here
FRED_API_KEY=your_fred_api_key_here

# AI Services
OPENROUTER_API_KEY=your_openrouter_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here

# Coral Protocol
CORAL_PROTOCOL_ENABLED=true
CORAL_MARKETPLACE_API_URL=https://api.coralprotocol.org
CORAL_SERVER_URL=http://localhost:5555

# Crossmint Integration
CROSSMINT_API_KEY=c2tfcHJvZHVjdGlvbl81ajJNS3IzWDk5U3lwSHJoWEtuU21meFBUMXlBc3E5R0JQaGh5aHlLdUNMYmZiSEdEVmV2clJSakc4VWFrdnhiQ1lCajVxNWpjbW9NSjIzNVQ1Z2drWng5a2tiQTlLczM0bURxMkhxbzFYWGZQNEFHbmZVYW9BR29hUnFwam0yTHRmenFkVHF3SmFVR3pZbzZtWUxYZnVFbkFNOWJwcEZEQk5mQUdpamhCNDFidzlFMTRydGE3RUdIYkFNdXQ5YXlTNHRORE56ZnI0UTRQcjRuejFFYlBaTVAK
```

### 4. Deploy Agents Locally

Test your agents locally using Docker Compose:

```bash
# Start all agents and coral server
docker-compose -f docker-compose.coral.yml up -d

# Check agent status
docker-compose -f docker-compose.coral.yml ps

# View logs
docker-compose -f docker-compose.coral.yml logs -f
```

### 5. Test Agent Registration

Verify that your agents are properly registered:

```bash
# Test data agent
curl http://localhost:8000/health

# Test portfolio agent
curl http://localhost:8001/health

# Test explainability agent
curl http://localhost:8002/health

# Test planner agent
curl http://localhost:8003/health

# Check coral server
curl http://localhost:5555/agents
```

### 6. Push Images to Registry

Push your Docker images to a container registry (Docker Hub, Amazon ECR, etc.):

```bash
# Tag images for registry
docker tag neural-capital/data-agent:latest your-registry/neural-capital/data-agent:latest
docker tag neural-capital/portfolio-agent:latest your-registry/neural-capital/portfolio-agent:latest
docker tag neural-capital/explainability-agent:latest your-registry/neural-capital/explainability-agent:latest
docker tag neural-capital/planner-agent:latest your-registry/neural-capital/planner-agent:latest

# Push to registry
docker push your-registry/neural-capital/data-agent:latest
docker push your-registry/neural-capital/portfolio-agent:latest
docker push your-registry/neural-capital/explainability-agent:latest
docker push your-registry/neural-capital/planner-agent:latest
```

### 7. Marketplace Submission

Submit your agents to the Coral Protocol marketplace by emailing the following information to **hello@coralprotocol.org**:

#### Required Information:

**Agent Details:**
- Agent configuration files (coral-agent-*.toml)
- Docker image URLs and tags
- Registry configuration (coral-registry.toml)
- Documentation and usage examples

**Wallet Information:**
- Wallet address from setup process
- Crossmint affiliated email
- Request for wallet funding for testing

**Publisher Information:**
- Company: Neural Capital
- Email: hello@neural-capital.com
- Website: https://neural-capital.com
- Support: support@neural-capital.com

**Technical Specifications:**
- Agent capabilities and APIs
- Pricing tiers and service levels
- Resource requirements
- Security and compliance information

#### Email Template:

```
Subject: Neural Capital Agents - Coral Protocol Marketplace Submission

Dear Coral Protocol Team,

I am submitting Neural Capital's AI financial agents for inclusion in the Coral Protocol marketplace.

Company Information:
- Publisher: Neural Capital
- Contact: hello@neural-capital.com
- Website: https://neural-capital.com
- Support: support@neural-capital.com

Agents for Submission:
1. Neural Capital Data Agent - Real-time financial data and market analysis
2. Neural Capital Portfolio Agent - Portfolio optimization and risk management
3. Neural Capital Explainability Agent - AI decision transparency and explanations  
4. Neural Capital Planner Agent - Comprehensive financial planning

Wallet Details:
- Wallet Address: [Your wallet address from setup]
- Crossmint Email: [Your crossmint email]
- Beta Registration: Completed via form

Docker Images:
- neural-capital/data-agent:latest
- neural-capital/portfolio-agent:latest
- neural-capital/explainability-agent:latest
- neural-capital/planner-agent:latest

Please find attached:
- Agent configuration files (coral-agent-*.toml)
- Registry configuration (coral-registry.toml)
- Docker deployment configurations
- Technical documentation

I have completed the beta registration form and request wallet funding for testing purposes.

Best regards,
[Your Name]
Neural Capital
```

### 8. Beta Program Registration

Ensure you're registered for the beta program:
https://docs.google.com/forms/d/e/1FAIpQLScrdR4Yf7C-LcAV1CGkCd1AMNIjj7CRlnAICUII4iYFkflN7w/viewform

### 9. Post-Submission Checklist

After submitting to the marketplace:

- [ ] Received confirmation email from Coral Protocol team
- [ ] Wallet has been funded for testing
- [ ] Agents appear in marketplace listings
- [ ] Test purchasing and usage flows
- [ ] Monitor agent performance and earnings
- [ ] Respond to any feedback or requirements

### 10. Monitoring and Management

Once deployed, monitor your agents:

```bash
# Check agent earnings
curl -X GET "https://api.coralprotocol.org/api/v1/agents/neural-capital-data-agent/earnings"

# Update pricing if needed
curl -X PUT "https://api.coralprotocol.org/api/v1/agents/neural-capital-data-agent/pricing" \
  -H "Content-Type: application/json" \
  -d '{"min_price": {"type": "usd", "amount": 3.00}}'

# View marketplace listings
curl "https://api.coralprotocol.org/api/v1/agents?category=Financial%20Services"
```

## Troubleshooting

### Common Issues:

1. **Docker Build Failures:**
   - Ensure all dependencies are in requirements.txt
   - Check Dockerfile syntax and base image availability

2. **Wallet Setup Issues:**
   - Verify Crossmint API key is correct
   - Ensure stable internet connection during setup
   - Check that beta registration is complete

3. **Agent Registration Failures:**
   - Verify coral-agent.toml files are valid TOML
   - Check that Docker images are accessible
   - Ensure all required options are defined

4. **Marketplace Submission Delays:**
   - Follow up if no response within 3-5 business days
   - Ensure all required information was provided
   - Check spam folder for responses

## Support

For technical issues:
- Neural Capital Support: support@neural-capital.com
- Coral Protocol Documentation: https://docs.coralprotocol.org
- Coral Protocol Community: [Discord/Telegram links]

## Next Steps

After successful marketplace deployment:
1. Monitor agent usage and performance
2. Gather user feedback and iterate
3. Consider additional agent capabilities
4. Explore integration with other Coral Protocol features
5. Plan for scaling and enterprise features