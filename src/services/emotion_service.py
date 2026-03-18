#emotion logic service, for actual emotion detection logic, creates emotion record in the database with detected emotion and metadata and inserts
from datetime import datetime, timezone
from pymongo.database import Database

from src.utils.constants import EMOTION_EMOJI_MAP


def detect_emotion_placeholder() -> dict[str, str]: #real emotion logic
    emotion = "neutral" #hardcoded atm
    emoji = EMOTION_EMOJI_MAP[emotion]
    return {
        "emotion": emotion,
        "emoji": emoji,
    }


def create_emotion_record( #creates a record in the database with the detected emotion and metadata and inserts to DB, returns the created record
    db: Database, #expects mongodb db object, imported above for this exact reasoning (type hint), likely from depends(get_db)
    user_id: str, #accepts user id, #from sub claim in jwt
    filename: str, #acepts filename, #from file.filename (likely)
    metadata: dict, #accepts meetada
) -> dict:
    detected = detect_emotion_placeholder() #calls the emotion detection logic, 

    document = { #creates the mongodb doc to insert, with the detected emotion and metadata and timestamps
        "user_id": user_id,
        "filename": filename,
        "emotion": detected["emotion"],
        "emoji": detected["emoji"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "metadata": metadata,
    }

    result = db.emotions.insert_one(document) #inserts the document into the emotions collection, result contains the inserted_id which is the _id of the new document
    document["_id"] = str(result.inserted_id)

    return document