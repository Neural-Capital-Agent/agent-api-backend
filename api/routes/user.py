from fastapi import APIRouter
from api.services import user_service
from api.schemas.user import UserCreate,UserLogin

router = APIRouter(tags=["user"])

@router.get("/")
async def list_users():
    return await user_service.get_users()

@router.post("/")
async def create_user(user: UserCreate):
    try:
        return user_service.add_user(user)
    except Exception as e:
        return {"error": str(e)}

@router.post("/login")
async def login_user(user: UserLogin):
    try:
        return user_service.login_user(user)
    except Exception as e:
        return {"error": str(e)}