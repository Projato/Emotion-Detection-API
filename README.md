# Emotion Detection API

## Setup

### 1. Clone the repository
```
git clone <repo-url>
cd emotion-detection-api
```

### 2. Install dependencies (uv)
```
uv sync
```

### 3. Create .env file
```
MONGODB_URI=your_mongodb_uri
MONGODB_DB_NAME=emotion_detection_db

JWT_SECRET_KEY=secret_key
JWT_ALGORITHM=HS256

GROQ_API_KEY=groq_api_key
GROQ_VISION_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
```

### 4. Run (uv)
```
uv run uvicorn src.main:app --reload
```