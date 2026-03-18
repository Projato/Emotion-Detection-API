#Reusuable constants for the application
EMOTION_EMOJI_MAP = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😣",
    "surprised": "😮",
    "neutral": "😐",
    "fearful": "😨",
    "disgusted": "😣",
}

DEFAULT_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"} #set (unique and fast checking)
DEFAULT_MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB