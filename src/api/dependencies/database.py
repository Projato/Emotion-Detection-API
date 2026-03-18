import os
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "emotion_detection_db") #with a fallback name

client: AsyncMongoClient | None = None #store mongodb client instance globally


async def connect_to_mongo(): #create if already does not exist, o.w.
    global client #referring to the global client variable

    if client is None:
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI is not set in the environment.")

        client = AsyncMongoClient(
            MONGODB_URI,
            server_api=ServerApi("1"),
            serverSelectionTimeoutMS=5000,
        )

        await client.admin.command("ping") #pymongo uses lazy connection behavior; MongoClient alone does not necessarily gurantee a real live connection immediately. 

    return client


async def close_mongo_connection() -> None: #to close
    global client

    if client is not None:
        client.close()
        client = None #to restart the connection if needed later


async def get_database(): #get the database instance from the client
    mongo_client = await connect_to_mongo()
    return mongo_client[MONGODB_DB_NAME] #accessing the database by name


async def get_db(): #so Depends(get_db) can be implemented, i.e., route fns can receive db automatically
    """
    FastAPI dependency to provide database.
    """
    return await get_database()
