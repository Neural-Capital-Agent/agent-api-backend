#!/usr/bin/env python3
"""
Test script to verify Coral server connectivity
"""

import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_coral_server():
    """Test if Coral server is accessible"""
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            logger.info("Testing Coral server health endpoint...")
            response = await client.get("http://localhost:5555/health", timeout=5.0)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Coral server is healthy: {result}")
                return True
            else:
                logger.error(f"❌ Coral server health check failed: {response.status_code}")
                return False
                
    except httpx.ConnectError as e:
        logger.error(f"❌ Cannot connect to Coral server: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

async def test_registration():
    """Test agent registration"""
    try:
        async with httpx.AsyncClient() as client:
            # Test registration endpoint
            logger.info("Testing agent registration...")
            
            registration_data = {
                "agent_id": "test_agent",
                "agent_type": "test_type", 
                "capabilities": ["test_capability"],
                "endpoint": "http://localhost:8000/api/v1/test"
            }
            
            response = await client.post(
                "http://localhost:5555/register", 
                json=registration_data,
                timeout=5.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Registration successful: {result}")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Registration test failed: {e}")
        return False

async def main():
    logger.info("Starting Coral server connectivity tests...")
    
    # Wait a bit for server to be ready
    await asyncio.sleep(2)
    
    health_ok = await test_coral_server()
    if health_ok:
        registration_ok = await test_registration()
        if registration_ok:
            logger.info("🎉 All tests passed!")
        else:
            logger.error("❌ Registration test failed")
    else:
        logger.error("❌ Health check failed")

if __name__ == "__main__":
    asyncio.run(main())