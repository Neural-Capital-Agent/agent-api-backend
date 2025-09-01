from api.Dependencies.db import supabase
from app.schemas.user import UserCreate

def get_user_by_email(email: str):
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

def create_user(user: UserCreate):
    response = supabase.table("users").insert(user.dict()).execute()
    return response.data[0] if response.data else None