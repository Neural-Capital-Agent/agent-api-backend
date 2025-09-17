"""
Coral Protocol Server - Mock implementation for local development
This server provides the basic infrastructure for agent registration and discovery.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os

logger = logging.getLogger(__name__)

class AgentRegistration(BaseModel):
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    timestamp: Optional[str] = None

class CoralMessage(BaseModel):
    agent_id: str
    target_agent: str
    method: str
    parameters: Dict[str, Any]
    timestamp: Optional[str] = None

class CoralServer:
    """
    Mock Coral Protocol Server for local development.
    In production, this would be replaced by the actual Coral Protocol infrastructure.
    """

    def __init__(self, host: str = "localhost", port: int = 5555):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="Coral Protocol Server (Mock)",
            description="Mock implementation of Coral Protocol Server for agent registration and discovery",
            version="1.0.0"
        )
        self.registered_agents: Dict[str, AgentRegistration] = {}
        self.setup_routes()

    def setup_routes(self):
        """Setup FastAPI routes for Coral Protocol endpoints"""

        @self.app.get("/")
        async def root():
            """Root endpoint with Coral Protocol server information"""
            return {
                "service": "Coral Protocol Server",
                "version": "1.0.0",
                "status": "running",
                "description": "Coral Protocol Server for Neural Capital Financial Agents - Agent registration, discovery, and orchestration",
                "endpoints": {
                    "health": "/health",
                    "register": "/register",
                    "agents": "/agents",
                    "status": "/status",
                    "studio": "/studio",
                    "documentation": "/docs"
                },
                "network": {
                    "registered_agents": len(self.registered_agents),
                    "total_capabilities": sum(len(agent.capabilities) for agent in self.registered_agents.values()) if self.registered_agents else 0
                },
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "Coral Protocol Server",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "registered_agents": len(self.registered_agents)
            }

        @self.app.post("/register")
        async def register_agent(registration: AgentRegistration):
            """Register an agent with the Coral Protocol network"""
            try:
                registration.timestamp = datetime.now().isoformat()
                self.registered_agents[registration.agent_id] = registration

                logger.info(f"🔌 AGENT REGISTERED: {registration.agent_id} ({registration.agent_type})")
                logger.info(f"   📍 Endpoint: {registration.endpoint}")
                logger.info(f"   🛠️  Capabilities: {', '.join(registration.capabilities)}")
                logger.info(f"   ⏰ Timestamp: {registration.timestamp}")

                return {
                    "success": True,
                    "message": f"Agent {registration.agent_id} registered successfully",
                    "agent_id": registration.agent_id,
                    "timestamp": registration.timestamp
                }
            except Exception as e:
                logger.error(f"❌ Failed to register agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/register/{agent_id}")
        async def unregister_agent(agent_id: str):
            """Unregister an agent from the Coral Protocol network"""
            try:
                if agent_id not in self.registered_agents:
                    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

                del self.registered_agents[agent_id]
                logger.info(f"Unregistered agent {agent_id}")

                return {
                    "success": True,
                    "message": f"Agent {agent_id} unregistered successfully",
                    "timestamp": datetime.now().isoformat()
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to unregister agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/agents")
        async def discover_agents(agent_type: Optional[str] = None):
            """Discover agents in the Coral Protocol network"""
            try:
                agents = list(self.registered_agents.values())

                if agent_type:
                    agents = [agent for agent in agents if agent.agent_type == agent_type]

                return {
                    "agents": agents,
                    "total_count": len(agents),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Failed to discover agents: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/agents/{agent_id}")
        async def get_agent_info(agent_id: str):
            """Get information about a specific agent"""
            try:
                if agent_id not in self.registered_agents:
                    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

                agent = self.registered_agents[agent_id]
                return {
                    "agent": agent,
                    "timestamp": datetime.now().isoformat()
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get agent info: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/invoke")
        async def invoke_agent(message: CoralMessage):
            """Invoke a method on a target agent"""
            try:
                target_agent_id = message.target_agent

                if target_agent_id not in self.registered_agents:
                    raise HTTPException(status_code=404, detail=f"Target agent {target_agent_id} not found")

                logger.info(f"🚀 AGENT INVOCATION: {message.agent_id} → {target_agent_id}")
                logger.info(f"   🎯 Method: {message.method}")
                logger.info(f"   📦 Parameters: {message.parameters}")

                target_agent = self.registered_agents[target_agent_id]

                # Try to invoke the actual agent endpoint
                import httpx
                async with httpx.AsyncClient() as client:
                    try:
                        # Construct the method endpoint URL
                        if message.method == "health_check":
                            endpoint_url = target_agent.endpoint.replace("/api/v1/agents/", "/api/v1/agents/") + "/health"
                        else:
                            # For other methods, construct appropriate endpoint
                            endpoint_url = f"{target_agent.endpoint}/{message.method}"

                        response = await client.post(
                            endpoint_url,
                            json=message.parameters,
                            timeout=10.0
                        )

                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"✅ INVOCATION SUCCESS: {target_agent_id} responded")
                            return {
                                "success": True,
                                "result": result,
                                "timestamp": datetime.now().isoformat(),
                                "invocation_details": {
                                    "method": message.method,
                                    "target": target_agent_id,
                                    "endpoint": endpoint_url
                                }
                            }
                        else:
                            logger.warning(f"⚠️ INVOCATION WARNING: {target_agent_id} returned {response.status_code}")
                            return {
                                "success": False,
                                "error": f"Agent returned status {response.status_code}",
                                "timestamp": datetime.now().isoformat()
                            }

                    except Exception as invoke_error:
                        logger.error(f"❌ INVOCATION FAILED: {target_agent_id} - {invoke_error}")
                        # Fallback to mock response for development
                        return {
                            "success": True,
                            "message": f"Fallback invocation of {message.method} on {target_agent_id}",
                            "result": {
                                "status": "completed",
                                "method": message.method,
                                "target": target_agent_id,
                                "note": "Fallback response - actual agent endpoint not reachable",
                                "error": str(invoke_error)
                            },
                            "timestamp": datetime.now().isoformat()
                        }

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ Failed to invoke agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/status")
        async def get_server_status():
            """Get comprehensive server status"""
            try:
                return {
                    "server": {
                        "status": "running",
                        "host": self.host,
                        "port": self.port,
                        "version": "1.0.0"
                    },
                    "network": {
                        "registered_agents": len(self.registered_agents),
                        "agent_types": list(set(agent.agent_type for agent in self.registered_agents.values())),
                        "total_capabilities": sum(len(agent.capabilities) for agent in self.registered_agents.values())
                    },
                    "agents": {
                        agent_id: {
                            "type": agent.agent_type,
                            "capabilities_count": len(agent.capabilities),
                            "registered_at": agent.timestamp
                        }
                        for agent_id, agent in self.registered_agents.items()
                    },
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Failed to get server status: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/studio", response_class=HTMLResponse)
        async def coral_studio():
            """Serve the Coral Studio interface"""
            try:
                # Get the path to the HTML file
                current_dir = os.path.dirname(os.path.abspath(__file__))
                studio_path = os.path.join(current_dir, "coral_studio.html")

                if os.path.exists(studio_path):
                    with open(studio_path, 'r', encoding='utf-8') as f:
                        return HTMLResponse(content=f.read())
                else:
                    return HTMLResponse(
                        content="<h1>Coral Studio</h1><p>Studio interface not found</p>",
                        status_code=404
                    )
            except Exception as e:
                logger.error(f"Failed to serve Coral Studio: {e}")
                return HTMLResponse(
                    content=f"<h1>Error</h1><p>Failed to load Coral Studio: {str(e)}</p>",
                    status_code=500
                )

    async def start_server(self):
        """Start the Coral Protocol server"""
        try:
            logger.info(f"Starting Coral Protocol Server on {self.host}:{self.port}")
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
        except Exception as e:
            logger.error(f"Failed to start Coral Protocol server: {e}")
            raise

    def run_server(self):
        """Run the server (synchronous)"""
        asyncio.run(self.start_server())


# Global server instance
coral_server = CoralServer()


async def main():
    """Main function to start the Coral Protocol server"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Starting Coral Protocol Server")
    print("=" * 40)
    print(f"Server will be available at: http://localhost:5555")
    print(f"Health check: http://localhost:5555/health")
    print(f"Agent registration: http://localhost:5555/register")
    print(f"Agent discovery: http://localhost:5555/agents")
    print("=" * 40)

    try:
        await coral_server.start_server()
    except KeyboardInterrupt:
        print("\nShutting down Coral Protocol Server...")
    except Exception as e:
        print(f"Server error: {e}")


if __name__ == "__main__":
    asyncio.run(main())