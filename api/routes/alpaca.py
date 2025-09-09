from fastapi import APIRouter, Depends
<<<<<<< HEAD
from utils.alpaca import alpaca
from api.services import user_service
from api.schemas.user import UserEmail

router = APIRouter(tags=["alpaca"])

@router.post("/")
async def create_alpaca_account(user_email: UserEmail):
    user = user_service.get_user_by_email(user_email.email)
    if(user.get('id_alpaca')):
        return {"mensaje": "Alpaca account already exists"}
    try:
        response = alpaca.create_user(user)
        if(response):
            user_service.add_alpaca_id(user_email.email, response.id)

    except Exception as e:
        return {"error": str(e),"user": user}
    return {"data": "Account created successfully", "response": response}

@router.get("/{email}")
async def get_alpaca_account(email: str):
    user = user_service.get_user_by_email(email)
    if not user:
        return {"mensaje": "User not found"}
    alpaca_account = user.get("id_alpaca")
    if not alpaca_account:
        return {"mensaje": "Alpaca account not found"}
    alpaca_data=alpaca.get_account(alpaca_account)
    return {"data": "Alpaca account retrieved successfully", "alpaca_account": alpaca_dat}
=======
from utils.alpaca import Alpaca

router = APIRouter(tags=["alpaca"])

@router.get("/")
async def get_alpaca_data():
    """
    Retrieve account data from Alpaca.
    """
    return {"data": Alpaca.requestAlpaca("GET", "/v2/account")}

# Add more alpaca-related endpoints as needed
>>>>>>> 4318aabd8f49beaada6d00c27cd8e4790426dc72
