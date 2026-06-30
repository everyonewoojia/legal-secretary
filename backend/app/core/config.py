from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "法务小秘 API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./law_secretary.db"
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL_NAME: str = "qwen-max"

    VECTOR_DB_PATH: str = "./vector_store"
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"


settings = Settings()

if not settings.SECRET_KEY:
    import sys
    print("FATAL: SECRET_KEY 未设置，请在 .env 中配置 SECRET_KEY")
    sys.exit(1)
