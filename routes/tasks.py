from fastapi import APIRouter
from database import tasks, users
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# Get all tasks for a user
@router.get("/{user_id}")
def get_tasks(user_id: str):
    data = list(tasks.find({"userId": ObjectId(user_id)}))
    for t in data:
        t["_id"] = str(t["_id"])
        t["userId"] = str(t["userId"])
    return data

# Create a new task
@router.post("/{user_id}")
def create_task(user_id: str, task: dict):
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return {"error": "User not found"}

    task["userId"] = ObjectId(user_id)
    task["email"] = user.get("email")
    task["name"] = user.get("name")
    task["createdAt"] = task.get("createdAt") or datetime.now().isoformat()
    task["dueDateTime"] = task.get("dueDateTime")
    task["completed"] = task.get("completed", False)
    task["notified"] = False  # Important for one-time email

    result = tasks.insert_one(task)
    task["_id"] = str(result.inserted_id)
    task["userId"] = str(task["userId"])
    return task

# Update a task
@router.put("/{task_id}")
def update_task(task_id: str, body: dict):
    tasks.update_one({"_id": ObjectId(task_id)}, {"$set": body})
    updated = tasks.find_one({"_id": ObjectId(task_id)})
    updated["_id"] = str(updated["_id"])
    updated["userId"] = str(updated["userId"])
    return updated

# Delete a task
@router.delete("/{task_id}")
def delete_task(task_id: str):
    tasks.delete_one({"_id": ObjectId(task_id)})
    return {"message": "Deleted"}