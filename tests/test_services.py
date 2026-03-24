import pytest
from src.services import emotion_service
from src.services.emotion_service import _normalize_emotion, _build_data

def test_normalize_emotion_basic():
    assert _normalize_emotion("happy") == "happy"
    assert _normalize_emotion("Joy") == "happy"
    assert _normalize_emotion("sadness") == "sad"
    assert _normalize_emotion("ANGER") == "angry"

def test_normalize_emotion_unknown():
    assert _normalize_emotion("random_text") == "neutral"
    assert _normalize_emotion("") == "neutral"
    assert _normalize_emotion(None) == "neutral"

def test_build_data_creates_base64_prefix():
    data = b"fake_image_bytes"
    result = _build_data(data, "image/png")

    assert result.startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_create_emotion_record_simple():
    
    async def mock_llm(*args, **kwargs): 
        return {"emotion": "happy", "emoji": "😊"} #mock llm

    original_llm = emotion_service.detect_emotion_with_llm
    emotion_service.detect_emotion_with_llm = mock_llm  # temporarily replacing actual llm call with mock

    # mock db
    class FakeInsertResult:
        def __init__(self):
            self.inserted_id = "123"

    class FakeCollection:
        async def insert_one(self, data):
            return FakeInsertResult()

    class FakeDB:
        emotions = FakeCollection()

    db = FakeDB()

    try: 
    # Call function
        result = await emotion_service.create_emotion_record(
            db=db,
            user_id="test_user",
            image_bytes=b"fake",
            metadata={"size": 1234, "content_type": "image/png"}, 
            filename="test.png",
            content_type="image/png"
        )

        # insert
        assert result["user_id"] == "test_user"
        assert result["filename"] == "test.png"
        assert result["emotion"] == "happy"
        assert result["emoji"] == "😊"
        assert result["metadata"] == {"size": 1234, "content_type": "image/png"}
        assert result["_id"] == "123"

    finally:
        emotion_service.detect_emotion_with_llm = original_llm