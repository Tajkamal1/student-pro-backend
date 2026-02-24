from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, dashboard, tasks
from notify import start_scheduler  # Import scheduler

app = FastAPI()

# -----------------------------
# CORS CONFIGURATION
# -----------------------------
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://student-pro-delta.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ROUTERS
# -----------------------------
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

# -----------------------------
# STARTUP EVENT
# -----------------------------
@app.on_event("startup")
def startup_event():
    # Start the scheduler when FastAPI starts
    start_scheduler()

# -----------------------------
# ROOT ROUTE
# -----------------------------
@app.get("/")
def root():
    return {"message": "Student Pro Backend Running 🚀"}