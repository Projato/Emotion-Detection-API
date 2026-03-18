#similar to user_helper in user.py, but for emotion records; converts raw db docs to api friendly format
def emotion_helper(emotion: dict) -> dict:
    return {
        "id": str(emotion["_id"]),
        "user_id": emotion["user_id"],
        "filename": emotion["filename"],
        "emotion": emotion["emotion"],
        "emoji": emotion["emoji"],
        "created_at": emotion.get("created_at"),
        "updated_at": emotion.get("updated_at"),
        "metadata": emotion.get("metadata", {}),
    }
#actively used in emotions.py to format db records for api responses in POST, GET ALL, and GET BY ID routes