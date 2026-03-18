#response model for emotion analysis results, like user.py, but with emotion specific fields
from typing import Any
from pydantic import BaseModel


class EmotionResponse(BaseModel):
    id: str #record id as a string; mongodb internally used _id
    user_id: str #would come from jwt sub
    filename: str
    emotion: str #emotion label
    emoji: str #emotion emoji
    metadata: dict[str, Any]