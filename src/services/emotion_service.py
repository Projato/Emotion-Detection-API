#emotion logic service, for actual emotion detection logic, creates emotion record in the database with detected emotion and metadata and inserts
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from groq import Groq
from src.utils.constants import EMOTION_EMOJI_MAP

load_dotenv()

DEFAULT_VISION_MODEL = os.getenv(
    "GROQ_VISION_MODEL",
    "meta-llama/llama-4-scout-17b-16e-instruct",
)

ALLOWED_EMOTIONS=set(EMOTION_EMOJI_MAP.keys())

def _get_groq_client() -> Groq:
    api_key=os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing API key in environment.")
    return Groq(api_key=api_key)

def _build_data(image_bytes: bytes, content_type: str) -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{encoded}"


def _normalize_emotion(value: str | None)-> str: 
    if not value:
        return "neutral"
    
    cleaned = value.strip().lower()

    alias_map= {
        "happiness": "happy",
        "joy": "happy",
        "sadness": "sad",
        "anger": "angry",
        "surprise": "surprised",
        "fear": "fearful",
        "disgust": "disgusted",
    }

    if cleaned in ALLOWED_EMOTIONS:
        return cleaned

    return alias_map.get(cleaned, "neutral")

def detect_emotion_with_llm(
    image_bytes: bytes,
    content_type: str,
    filename: str,
    model: str = DEFAULT_VISION_MODEL,
) -> dict[str, str]:
    client = _get_groq_client()
    image_data_url = _build_data(image_bytes, content_type)

    prompt = """
You are an emotion classifier for uploaded face images.

Return ONLY valid JSON in this exact format:
{"emotion": "<one_label>"}

Allowed labels:
happy
sad
angry
surprised
neutral
fearful
disgusted

Rules:
- Choose exactly one label.
- Do not include explanation.
- If uncertain, return "neutral".
""".strip()

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url},
                    },
                    {
                        "type": "text",
                        "text": f"Filename: {filename}",
                    },
                ],
            }
        ],
    )

    raw_content = response.choices[0].message.content
    parsed = json.loads(raw_content)
    emotion = _normalize_emotion(parsed.get("emotion"))
    emoji = EMOTION_EMOJI_MAP[emotion]

    return {
        "emotion": emotion,
        "emoji": emoji,
    }


async def create_emotion_record( #creates a record in the database with the detected emotion and metadata and inserts to DB, returns the created record
    db,
    user_id: str, #accepts user id, #from sub claim in jwt
    filename: str, #acepts filename, #from file.filename (likely)
    metadata: dict, #accepts meetada
    image_bytes: bytes,
    content_type: str, 
) -> dict:
    detected = detect_emotion_with_llm(
        image_bytes=image_bytes,
        content_type=content_type,
        filename=filename,
    ) #calls the emotion detection logic, 

    document = { #creates the mongodb doc to insert, with the detected emotion and metadata and timestamps
        "user_id": user_id,
        "filename": filename,
        "emotion": detected["emotion"],
        "emoji": detected["emoji"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "metadata": metadata,
    }

    result = await db.emotions.insert_one(document) #inserts the document into the emotions collection, result contains the inserted_id which is the _id of the new document
    document["_id"] = result.inserted_id

    return document