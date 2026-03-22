"""
Main for emotion related routers, auth, db, image validation, emotion creation and formatting helpers.
"""
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Request
from src.api.dependencies.limiter import limiter
from src.api.dependencies.auth import get_current_user #auth dependency to get current user info from JWT, extract current JWT payload
from src.api.dependencies.database import get_db #db dependency to get MongoDB database object into route functions for db operations
from src.schemas.emotion import emotion_helper
from src.services.emotion_service import (
    create_emotion_record,
    reanalyze_emotion_record,
)
from src.services.image_service import validate_image


router = APIRouter(prefix="/emotions", tags=["Emotions"]) #grouping all emotion related routes under /emotions path with "Emotions" tag for documentation


@router.post("", status_code=status.HTTP_201_CREATED) #main upload route for emotion images; accepts multipart/form-data with file upload, validates image, creates emotion record in db, and returns formatted response
@limiter.limit("2/minute")
async def upload_emotion_image(
    request: Request, 
    files: List[UploadFile] = File(...), #expects a file upload in the request; File(...) indicates it's required and should be treated as a file input
    db = Depends(get_db), #fastapi calls get_db() from database.py to yield a MongoDB database object and injects it into this route function for db operations
    current_user: dict = Depends(get_current_user), #fastapi calls get_current_user() from auth.py to extract and validate the JWT from the request, return dict
) -> dict:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded.",
        )
    
    created_items = []

    for file in files:
        metadata = await validate_image(file) #calls validate_image() from image_service.py to check validity; sinc validate_image async, we await
        image_bytes = await file.read()

        try:
            created_record = await create_emotion_record(
                db=db,
                user_id=current_user.get("sub", "unknown_user"),
                filename=metadata["filename"],
                metadata=metadata,
                image_bytes=image_bytes,
                content_type=metadata["content_type"],
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc

        created_items.append(emotion_helper(created_record))

    return {
        "message": "Emotion analysis record created successfully.",
        "data": created_items,
    }


@router.get("", status_code=status.HTTP_200_OK) #get all emotion records for the current user; queries the database for records matching the user_id from JWT, formats them with emotion_helper, and returns in a list
@limiter.limit("10/minute")
async def get_all_emotions(
    request: Request,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user), #injecting current user payload
) -> dict:
    user_id = current_user.get("sub") #getting the user ID
    cursor = db.emotions.find({"user_id": user_id}) #querying the emotions collection for all records where user_id matches the current user's ID
    records = await cursor.to_list(length=None)
    items = [emotion_helper(record) for record in records] #transform

    return {"items": items}


@router.get("/{emotion_id}", status_code=status.HTTP_200_OK) #single user emotion record by ID; accepts emotion_id as a path parameter, queries the database for a record matching that ID and the current user's ID, similar logic^
async def get_emotion_by_id(
    emotion_id: str,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not ObjectId.is_valid(emotion_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid emotion record ID."
        )

    record = await db.emotions.find_one( #one record that matches _id and user_id; ensures users can only access their own emotion records by checking both the record ID and the user ID from the JWT
        {"_id": ObjectId(emotion_id), "user_id": current_user.get("sub")}
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emotion record not found.",
        )

    return {"data": emotion_helper(record)}

@router.put("/{emotion_id}", status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
async def update_emotion_record(
    request: Request,
    emotion_id: str,
    file: UploadFile = File(...),
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not ObjectId.is_valid(emotion_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid emotion record ID.",
        )

    existing_record = await db.emotions.find_one(
        {"_id": ObjectId(emotion_id), "user_id": current_user.get("sub")}
    )

    if not existing_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emotion record not found.",
        )

    metadata = await validate_image(file)
    image_bytes = await file.read()

    try:
        updated_record = await reanalyze_emotion_record(
            db=db,
            emotion_id=ObjectId(emotion_id),
            user_id=current_user.get("sub"),
            filename=metadata["filename"],
            metadata=metadata,
            image_bytes=image_bytes,
            content_type=metadata["content_type"],
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return {
        "message": "Emotion record updated successfully.",
        "data": emotion_helper(updated_record),
    }


@router.delete("/{emotion_id}", status_code=status.HTTP_200_OK)
@limiter.limit("2/minute")
async def delete_emotion_record(
    request: Request,
    emotion_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not ObjectId.is_valid(emotion_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid emotion record ID.",
        )

    result = await db.emotions.delete_one(
        {"_id": ObjectId(emotion_id), "user_id": current_user.get("sub")}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emotion record not found.",
        )

    return {"message": "Emotion record deleted successfully."}