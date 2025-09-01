from fastapi import APIRouter
from api.services import user_service

router = APIRouter(prefix="/user", tags=["Users"])

@router.get("/")
async def list_users():
    return await user_service.get_users()

@router.post("/")
async def create_user(user: dict):
    return await user_service.add_user(user)