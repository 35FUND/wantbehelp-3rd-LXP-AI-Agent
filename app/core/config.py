# 환경 변수(.env) 및 상수 관리
from pydantic_settings import BaseSettings

class Settings(BaseSettings) :
    GEMINI_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: str
    MODEL_NAME: str
    class Config :
        env_file = ".env"
        extra = "ignore"

settings = Settings()