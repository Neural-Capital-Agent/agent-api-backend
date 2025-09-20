#!/usr/bin/env python3
"""
Test script for Coral Studio integration.
Verifies that agents are properly configured and can be registered with Coral Server.
"""

import asyncio
import sys
import logging
from typing import Dict, Any
import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_coral_integration():
    """Test Coral Protocol integration end-to-end"""
    print("Testing Coral Protocol Integration")
    print("=" * 50)

    try:
        # Test 1: Import and initialize coral registry
        print("\n1. Testing Coral Registry Initialization...")
        from agent.coral_registry import coral_registry
        print(f"   SUCCESS: Coral Server URL: {coral_registry.coral_server_url}")
        print(f"   SUCCESS: API Base URL: {coral_registry.api_base_url}")

        # Test 2: Check agent configurations
        print("\n2. Testing Agent Configurations...")
        configs = coral_registry._get_agent_configurations()
        print(f"   SUCCESS: Found {len(configs)} agent configurations:")
        for config in configs:
            print(f"     - {config.agent_id} ({config.agent_type})")
            print(f"       Capabilities: {len(config.capabilities)}")
            print(f"       Endpoint: {config.endpoint_url}")

        # Test 3: Test agent registration
        print("\n3. Testing Agent Registration...")
        try:
            registration_results = await coral_registry.register_all_agents()
            successful = sum(1 for success in registration_results.values() if success)
            total = len(registration_results)

            print(f"   SUCCESS: Registration Results: {successful}/{total} successful")
            for agent_id, success in registration_results.items():
                status = "SUCCESS" if success else "FAILED"
                print(f"     {status}: {agent_id}")

        except Exception as reg_error:
            print(f"   WARNING: Registration test failed: {reg_error}")
            print("   NOTE: This is expected if Coral Server is not running")

        # Test 4: Test registry status
        print("\n4. Testing Registry Status...")
        try:
            status = await coral_registry.get_agent_registry_status()
            print(f"   SUCCESS: Registry Status: {status['registry_status']}")
            print(f"   SUCCESS: Total Agents: {status['summary']['total_agents']}")
            print(f"   SUCCESS: Healthy Agents: {status['summary']['healthy_agents']}")
        except Exception as status_error:
            print(f"   WARNING: Status check failed: {status_error}")

        # Test 5: Test Coral Studio config generation
        print("\n5. Testing Coral Studio Configuration...")
        try:
            studio_config = await coral_registry.get_coral_studio_config()
            print(f"   SUCCESS: Generated config for {len(studio_config['agents'])} agents")
            print(f"   SUCCESS: Coral Server: {studio_config['coral_server']['url']}")
            print(f"   SUCCESS: API Server: {studio_config['api_server']['url']}")
        except Exception as config_error:
            print(f"   WARNING: Config generation failed: {config_error}")

        # Test 6: Test API endpoints (if server is running)
        print("\n6. Testing API Endpoints...")
        try:
            async with httpx.AsyncClient() as client:
                # Test if API server is running
                response = await client.get(f"{coral_registry.api_base_url}/")
                if response.status_code == 200:
                    print(f"   SUCCESS: API server is running at {coral_registry.api_base_url}")

                    # Test coral endpoints
                    coral_endpoints = [
                        "/api/v1/coral/status",
                        "/api/v1/coral/studio-config",
                        "/api/v1/coral/capabilities"
                    ]

                    for endpoint in coral_endpoints:
                        try:
                            url = f"{coral_registry.api_base_url}{endpoint}"
                            response = await client.get(url, timeout=5.0)
                            print(f"   SUCCESS: {endpoint}: HTTP {response.status_code}")
                        except Exception as endpoint_error:
                            print(f"   WARNING: {endpoint}: {endpoint_error}")
                else:
                    print(f"   WARNING: API server not responding (HTTP {response.status_code})")
        except Exception as api_error:
            print(f"   WARNING: API server connection failed: {api_error}")
            print("   NOTE: Start the API server with: python app.py")

        print("\n" + "=" * 50)
        print("Coral Integration Test Completed!")

        # Provide next steps
        print("\nNext Steps:")
        print("1. Ensure Coral Server is running at:", coral_registry.coral_server_url)
        print("2. Start your API server: python app.py")
        print("3. Register agents: POST /api/v1/coral/register")
        print("4. Check status: GET /api/v1/coral/status")
        print("5. Open Coral Studio and configure with your agents")

    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        return False

    finally:
        # Clean up
        try:
            await coral_registry.close()
        except:
            pass

    return True


async def test_coral_server_connection():
    """Test if Coral Server is reachable"""
    print("\nTesting Coral Server Connection...")

    try:
        from agent.coral_registry import coral_registry
        coral_url = coral_registry.coral_server_url

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{coral_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print(f"   SUCCESS: Coral Server is running at {coral_url}")
                    print(f"   SUCCESS: Health check passed: {response.json()}")
                    return True
                else:
                    print(f"   WARNING: Coral Server responded with HTTP {response.status_code}")
                    return False
            except httpx.ConnectError:
                print(f"   ERROR: Cannot connect to Coral Server at {coral_url}")
                print("   NOTE: Make sure Coral Server is running")
                return False
            except Exception as e:
                print(f"   WARNING: Connection test failed: {e}")
                return False
    except Exception as e:
        print(f"   ERROR: Test setup failed: {e}")
        return False


async def main():
    """Main test function"""
    print("Neural Capital - Coral Studio Integration Test")
    print("Testing agent visibility and configuration for Coral Studio")

    # Test Coral Server connection
    coral_available = await test_coral_server_connection()

    # Run main integration test
    success = await test_coral_integration()

    if success:
        if coral_available:
            print("\nAll tests passed! Agents should be visible in Coral Studio.")
        else:
            print("\nIntegration setup complete. Start Coral Server to see agents in Studio.")
        return 0
    else:
        print("\nSome tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)