from fastapi import APIRouter
from database import tasks
from bson import ObjectId

router = APIRouter()

@router.get("/{user_id}")
def get_tasks(user_id: str):
    data = list(tasks.find({"userId": ObjectId(user_id)}))
    for t in data:
        t["_id"] = str(t["_id"])
    return data

@router.post("/{user_id}")
def create_task(user_id: str, task: dict):
    task["userId"] = ObjectId(user_id)
    result = tasks.insert_one(task)
    task["_id"] = str(result.inserted_id)
    return task

@router.put("/{task_id}")
def update_task(task_id: str, body: dict):
    tasks.update_one({"_id": ObjectId(task_id)}, {"$set": body})
    return {"message": "Updated"}

@router.delete("/{task_id}")
def delete_task(task_id: str):
    tasks.delete_one({"_id": ObjectId(task_id)})
    return {"message": "Deleted"}