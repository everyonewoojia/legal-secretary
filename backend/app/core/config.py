from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "法务小秘 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./legal_secretary.db"
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen-turbo"

    RAG_TOP_K: int = 3
    VECTOR_DIM: int = 768

    class Config:
        env_file = ".env"


settings = Settings()
