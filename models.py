from pymongo import MongoClient, errors
from bson import ObjectId
from bson.errors import InvalidId
import os, hashlib, secrets
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✅ MongoDB connected successfully!")
except errors.ServerSelectionTimeoutError as err:
    print("❌ Failed to connect to MongoDB:", err)

db = client["Student-Pro-DB"]
users_collection = db["users"]
dashboards_collection = db["dashboardsdata"]

# Password hashing
def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Create user
def create_user(name: str, email: str, password: str) -> dict:
    salt = secrets.token_hex(16)
    hashed_password = hash_password(password, salt)
    
    user = {"name": name, "email": email, "salt": salt, "password": hashed_password}
    result = users_collection.insert_one(user)
    user["_id"] = str(result.inserted_id)

    # Create initial dashboard
    dashboard = {
        "userId": result.inserted_id,
        "name": name,
        "email": email,
        "studyHours": 0,
        "tasksCompleted": 0,
        "attendance": 0,
        "streak": 0,
        "goal": 2,
        "weeklyActivity": [0,0,0,0,0,0,0],
        "recentActivity": [{"icon":"👋","text":"Welcome to your dashboard!","time":"just now"}]
    }
    dashboards_collection.insert_one(dashboard)
    return user

def find_user_by_email(email: str):
    user = users_collection.find_one({"email": email})
    if user: user["_id"] = str(user["_id"])
    return user

def find_user_by_id(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        return None
    user = users_collection.find_one({"_id": obj_id})
    if user: user["_id"] = str(user["_id"])
    return user

def verify_password(plain_password: str, user: dict) -> bool:
    return hash_password(plain_password, user["salt"]) == user["password"]

def get_dashboard_by_userid(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        return None
    dashboard = dashboards_collection.find_one({"userId": obj_id})
    if dashboard:
        dashboard["_id"] = str(dashboard["_id"])
        dashboard["userId"] = str(dashboard["userId"])
    return dashboard