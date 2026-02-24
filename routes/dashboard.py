from fastapi import APIRouter, HTTPException
from models import get_dashboard

router = APIRouter()

@router.get("/user/{user_id}")
def get_user_dashboard(user_id: str):
    dashboard = get_dashboard(user_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard