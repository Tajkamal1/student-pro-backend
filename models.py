from bson import ObjectId
from database import users, dashboards
import hashlib, secrets


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def create_user(name, email, password):
    salt = secrets.token_hex(16)
    hashed = hash_password(password, salt)

    result = users.insert_one({
        "name": name,
        "email": email,
        "salt": salt,
        "password": hashed
    })

    user_id = result.inserted_id

    dashboards.insert_one({
        "userId": user_id,
        "name": name,
        "email": email,
        "studyHours": 0,
        "tasksCompleted": 0,
        "attendance": 0,
        "streak": 0,
        "goal": 2,
        "weeklyActivity": [0, 0, 0, 0, 0, 0, 0],
        "recentActivity": []
    })

    return str(user_id)


def find_user_by_email(email):
    return users.find_one({"email": email})


def verify_password(password, user):
    return hash_password(password, user["salt"]) == user["password"]


def get_dashboard(user_id):
    dashboard = dashboards.find_one({"userId": ObjectId(user_id)})

    if dashboard:
        dashboard["_id"] = str(dashboard["_id"])
        dashboard["userId"] = str(dashboard["userId"])

    return dashboard