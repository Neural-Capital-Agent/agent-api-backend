from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from api.api import api_router
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup():
    """Initialize the API cache on startup."""
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@app.get("/")
def read_root():
    """Root endpoint for health check."""
    return {"status": "online", "service": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
async def read_alpaca():
    return {"message": "Alpaca API endpoint"}

@app.post("/create_user")
async def create_user(data: dict):
    supabase_object = Supabase(URL, KEY)
    supabase_data = await supabase_object.insert_data("users", data)
    return {"message": "User created successfully", "data": data, "supabase_info": supabase_data}