from api.dependencies.db import supabase
from api.schemas.user import UserCreate, UserLogin

def get_user_by_email(email: str):
    response = supabase.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None

def add_user(user: UserCreate):
    user_response= supabase.auth.sign_up({"email": user.email, "password": user.password})
    user_dict = user.dict()
    user_dict["id_user"] = user_response.user.id
    user_dict.pop("password", None)
    response = supabase.table("users").insert(user_dict).execute()
    return f'{user} dfs {response.data[0]}' if response.data else None

<<<<<<< HEAD
def add_alpaca_id(email: str, alpaca_id: str):
    response = supabase.table("users").update({"alpaca_id": alpaca_id}).eq("email", email).execute()
    return response.data[0] if response.data else None

=======
>>>>>>> 4318aabd8f49beaada6d00c27cd8e4790426dc72
def login_user(user: UserLogin):
    user_response = supabase.auth.sign_in_with_password({"email": user.email, "password": user.password})
    if user_response.user:
        return {"access_token": user_response.session.access_token}
    return {"error": "Invalid email or password"}