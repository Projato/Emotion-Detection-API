#image validation service, checks file type and size, returns metadata if valid, raises HTTP exceptions if invalid
import os
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile, status #uploadfile: for handling file uploads (fastapi type)

from src.utils.constants import DEFAULT_ALLOWED_IMAGE_TYPES, DEFAULT_MAX_IMAGE_SIZE #if env missing -> fallback

load_dotenv()

MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", DEFAULT_MAX_IMAGE_SIZE)) #assigns env variable or fallback
ALLOWED_IMAGE_TYPES = set(
    os.getenv("ALLOWED_IMAGE_TYPES", "image/jpeg,image/png").split(",")
)


async def validate_image(file: UploadFile) -> dict[str, int | str]: #async because file reading is async, returns dict with metadata if valid, raises HTTPException if invalid
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type: {file.content_type}. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    contents = await file.read() #read the file contents to check the size, this is async cause involves I/O operations
    size = len(contents)

    if size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum allowed size is {MAX_IMAGE_SIZE} bytes.",
        )

    await file.seek(0) #moving file pointer back to the beginning after reading, so it can be read again later (e.g. by the emotion detection logic), this is also async for the same reason as above

    return {
        "filename": file.filename or "unknown", #filename from the upload, if missing use "unknown"
        "content_type": file.content_type, #jpeg/png
        "size": size,
    }