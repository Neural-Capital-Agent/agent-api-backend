from fastapi import APIRouter
from api.services import user_service, user_portafolio_service
from api.schemas.user import UserCreate,UserLogin
from api.schemas.user_portafolio import UserInput

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

@router.post("/{user_id}/setup")
async def create_user_goals(user_id: str, user_input: UserInput):
    try:
        return user_portafolio_service.process_onboarding_form(user_input, user_id)
    except Exception as e:
        return {"error": str(e)}

@router.get("/{user_id}/setup")
async def get_user_goals(user_id: str):
    try: 
        if user_portafolio_service.get_user_goals(user_id):
            return True
        else:
            return False
    except Exception as e:
        return {"error": str(e)}

@router.get("/{user_id}")
async def get_user(user_id: str):
    try:
        return user_service.get_user_by_id(user_id)
    except Exception as e:
        return {"error": str(e)}