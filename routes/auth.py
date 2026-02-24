from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from models import create_user, find_user_by_email, verify_password

router = APIRouter()

# ======================
# MODELS
# ======================

class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginModel(BaseModel):
    email: EmailStr
    password: str


# ======================
# REGISTER
# ======================

@router.post("/register")
def register(data: RegisterModel):

    if find_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    user_id = create_user(data.name, data.email, data.password)

    return {
        "message": "Registered successfully",
        "userId": user_id
    }


# ======================
# LOGIN
# ======================

@router.post("/login")
def login(data: LoginModel):

    user = find_user_by_email(data.email)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not verify_password(data.password, user):
        raise HTTPException(status_code=400, detail="Invalid password")

    return {
        "message": "Login success",
        "userId": str(user["_id"])
    }