from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    
    # Force connection check
    client.admin.command("ping")
    
    print("✅ MongoDB Connected Successfully!")

except Exception as e:
    print("❌ MongoDB Connection Failed!")
    print(e)

db = client["Student-Pro-DB"]

users = db["users"]
dashboards = db["dashboards"]
tasks = db["tasks"]
storage = db["storage"]
practice = db["practice"]