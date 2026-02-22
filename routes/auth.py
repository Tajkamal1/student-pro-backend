from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from models import create_user, find_user_by_email, verify_password

router = APIRouter()

# --- Pydantic models ---
class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirmPassword: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

# --- Register route ---
@router.post("/register")
def register(user: RegisterModel):
    if user.password != user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if find_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    create_user(user.name, user.email, user.password)
    return {"message": "User registered successfully"}

# --- Login route ---
@router.post("/login")
def login(data: LoginModel):
    user = find_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not verify_password(data.password, user):
        raise HTTPException(status_code=400, detail="Invalid password")

    return {"message": "Login successful", "userId": str(user["_id"])}