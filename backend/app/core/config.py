import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "MuVora"
    API_V1_STR: str = "/api"
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    
    # Model configuration
    _ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    MODEL_PATH: str = os.path.join(_ROOT, "models", "sentiment_bilstm.keras")
    VOCAB_PATH: str = os.path.join(_ROOT, "models", "vocab.json")
    METADATA_PATH: str = os.path.join(_ROOT, "models", "metadata.json")
    
    VOCAB_SIZE: int = 10000
    MAX_SEQUENCE_LENGTH: int = 200
    EMBEDDING_DIM: int = 128
    
    # Limits
    MAX_REVIEW_LENGTH: int = 10000
    MAX_BATCH_SIZE: int = 20
    
    # Translation
    TRANSLATION_TIMEOUT_SECONDS: int = 8
    MOCK_TRANSLATION: bool = False

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()
