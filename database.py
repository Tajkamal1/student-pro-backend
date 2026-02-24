from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["Student-Pro-DB"]

users = db["users"]
dashboards = db["dashboards"]
tasks = db["tasks"]
storage = db["storage"]
practice = db["practice"]