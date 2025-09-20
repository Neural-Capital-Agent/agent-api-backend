from api.dependencies.db import supabase
from api.schemas.user import UserCreate, UserLogin

def get_user_by_email(email: str):
    response = supabase.table("users").select("*, user_tier").eq("email", email).execute()
    return response.data[0] if response.data else None
def get_user_by_id(user_id: str):
    response = supabase.table("users").select("*, user_tier").eq("id_user", user_id).execute()
    return response.data[0] if response.data else None

def add_user(user: UserCreate):
    user_response= supabase.auth.sign_up({"email": user.email, "password": user.password})
    user_dict = user.dict()
    user_dict["id_user"] = user_response.user.id
    user_dict["user_tier"] = "basic"  # Set default tier for new users
    user_dict.pop("password", None)
    response = supabase.table("users").insert(user_dict).execute()
    return f'{user} dfs {response.data[0]}' if response.data else None

def add_alpaca_id(email: str, alpaca_id: str):
    response = supabase.table("users").update({"alpaca_id": alpaca_id}).eq("email", email).execute()
    return response.data[0] if response.data else None

def update_user_tier(user_id: str, new_tier: str):
    """Update user tier in database"""
    valid_tiers = ["basic", "premium", "enterprise"]
    if new_tier not in valid_tiers:
        raise ValueError(f"Invalid tier: {new_tier}. Must be one of {valid_tiers}")

    response = supabase.table("users").update({"user_tier": new_tier}).eq("id_user", user_id).execute()
    return response.data[0] if response.data else None

def login_user(user: UserLogin):
    user_response = supabase.auth.sign_in_with_password({"email": user.email, "password": user.password})
    if user_response.user:
        # Get user details including tier from database
        user_data = get_user_by_id(user_response.user.id)
        user_tier = user_data.get("user_tier", "basic") if user_data else "basic"

        return {
            "access_token": user_response.session.access_token,
            "user_id": user_response.user.id,
            "user_tier": user_tier
        }
    return {"error": "Invalid email or password"}