#app entry point; initializes FastAPI app, sets up lifespan events for MongoDB connection management, and includes API routers for authentication and emotion-related endpoints
import os
from contextlib import asynccontextmanager #for managing lifespan events in FastAPI, allows us to define startup and shutdown logic for resources like database connections

from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger

from src.api.dependencies.database import close_mongo_connection, connect_to_mongo
from src.api.routers.auth import router as auth_router #auth router for user registration and login, JWT handling, etc.
from src.api.routers.emotions import router as emotions_router

load_dotenv() #maybe not required here, will have to try

APP_NAME = os.getenv("APP_NAME", "Emotion Detection API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")


@asynccontextmanager #defining the lifespan event handler for FastAPI, which will manage the MongoDB connection lifecycle; connects to MongoDB on startup and ensures the connection is closed on shutdown
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    connect_to_mongo()
    logger.info("MongoDB Atlas connected.")

    yield #startup ends here, the app will run until it receives a shutdown signal, at which point the code after yield will execute

    close_mongo_connection()
    logger.info("MongoDB connection closed.")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)


app.include_router(auth_router, prefix=API_V1_PREFIX) #including the auth router under the /api/v1 path; this will handle all authentication related endpoints like registration and login, and will be available at /api/v1/auth/...
app.include_router(emotions_router, prefix=API_V1_PREFIX) #including the emotions router under the /api/v1 path; this will handle all emotion related endpoints like uploading images and retrieving emotion records, and will be available at /api/v1/emotions/...

@app.get("/")
def root(): 
    return {"message": "Emotion Detection API is running."}