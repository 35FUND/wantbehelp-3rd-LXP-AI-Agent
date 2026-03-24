# 환경 변수(.env) 및 상수 관리
from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings) :
    GEMINI_API_KEY: str
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_SESSION_TOKEN: Optional[str] = None
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: str
    MODEL_NAME: str

    # 데이터베이스 설정
    DATABASE_URL: str
    SHORTS_DIR: str = ""

    # 앱 실행 설정
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = False

    # 검수 상태값
    INSPECTION_PENDING_STATUS: str = "PENDING"
    SHORTS_APPROVED_STATUS: str = "PUBLISHED"
    SHORTS_REJECTED_STATUS: str = "REJECTED"

    # 스케줄러 주기 설정 (기본값 설정 가능)
    INSPECTOR_JOB_INTERVAL_DAYS: int = 0
    INSPECTOR_JOB_INTERVAL_HOURS: int = 0
    INSPECTOR_JOB_INTERVAL_MINUTES: int = 1
    INSPECTOR_JOB_INTERVAL_SECONDS: int = 0
    class Config :
        env_file = ".env"
        extra = "ignore"

settings = Settings()
