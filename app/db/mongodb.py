from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None

# Initialize database helper object
db_helper = Database()

async def connect_to_mongo():
    """
    Establish connection to the local MongoDB server
    """
    mongo_url = os.getenv("MONGO_DETAILS")
    db_helper.client = AsyncIOMotorClient(mongo_url)
    
    # Reference the specific database name
    db_helper.db = db_helper.client.football_scout_db
    print("✅ Successfully connected to MongoDB!")

async def close_mongo_connection():
    """
    Close the database connection when the app shuts down
    """
    if db_helper.client:
        db_helper.client.close()
        print("❌ MongoDB connection closed.")