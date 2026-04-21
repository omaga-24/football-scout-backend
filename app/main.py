from linecache import cache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 🔥 Critical: Do not forget this for Frontend connection
from app.api.v1 import players
from contextlib import asynccontextmanager
from app.db.mongodb import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events using lifespan logic
    """
    # Startup: Connect to the database
    await connect_to_mongo()
    yield
    # Shutdown: Close the database connection
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# 🔥 CORS Middleware: Mandatory for allowing requests from your React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin (Frontend)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Connect Routes
app.include_router(players.router, prefix="/api/v1")

# Simple in-memory cache
cache = {}

@app.get("/api/v1/suggestions/{query}")
async def get_suggestions(query: str):
    if query in cache:
        print(f"✅ Returning from Cache: {query}")
        return cache[query]

    try:
        # Placeholder for result data coming from your service logic
        data = []

        cache[query] = data
        return data

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "Football Scout Backend is Running!"}