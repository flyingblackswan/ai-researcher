from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DOCKER_WORKPLACE_NAME: str = 'workplace_meta'
    GITHUB_AI_TOKEN: Optional[str] = None
    AI_USER: str = "ai-sin"
    LOCAL_ROOT: str = '.'
    DEBUG: bool = True
    DEFAULT_LOG: bool = True
    LOG_PATH: Optional[str] = None
    EVAL_MODE: bool = False
    BASE_IMAGES: str = "tjbtech1/paperapp:latest"
    COMPLETION_MODEL: str = "gpt-4o-2024-08-06"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHEEP_MODEL: str = "gpt-4o-mini-2024-07-18"
    GPUS: Optional[str] = None
    PLATFORM: str = "linux/amd64"
    FN_CALL: bool = True
    API_BASE_URL: Optional[str] = None
    ADD_USER: bool = False
    NON_FN_CALL: bool = False
    CATEGORY: str = "vq"
    INSTANCE_ID: str = "rotation_vq"
    TASK_LEVEL: str = "task1"
    CONTAINER_NAME: str = "paper_eval"
    WORKPLACE_NAME: str = "workplace"
    CACHE_PATH: str = "cache"
    PORT: int = 7020
    MAX_ITER_TIMES: int = 0
    CORS_ORIGINS: str = "*"
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
