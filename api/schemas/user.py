from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: str
    street_address: str
    city: str
    state: str
    postal_code: str
    given_name: str
    family_name: str
    date_of_birth: str
    country_of_citizenship: str
    country_of_birth: str
    tax_id: str
    contact_given: str
    contact_family: str
    contact_email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserEmail(BaseModel):
    email: EmailStr
    