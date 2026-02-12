# FastAPI 앱 실행 및 미들웨어 설정
import logging, sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import inspector_router
from sqlmodel import SQLModel
from app.core.scheduler import start_scheduler, scheduler 
from app.models.database import engine
from app.models.shorts import Shorts
from app.models.shorts_inspection_result import ShortsInspectionResult

def setup_logging():
    # 1. 기본 로그 레벨 설정
    logging.basicConfig(level=logging.INFO)
    
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING) # SQL 출력 차단
    logging.getLogger('apscheduler').setLevel(logging.WARNING)       # 스케줄러 알림 차단
    logging.getLogger('uvicorn.access').setLevel(logging.INFO)    # HTTP 요청 로그 차단 (필요시)

    # 3. 내 애플리케이션 로그는 INFO로 유지
    logging.getLogger('app').setLevel(logging.INFO)

setup_logging()

# 스케줄러 로거가 부모 로거(root)로 로그를 전파하도록 설정
logging.getLogger("app.core.scheduler").propagate = True

@asynccontextmanager
async def lifespan(app: FastAPI) :
    async with engine.begin() as conn :
        await conn.run_sync(SQLModel.metadata.create_all)

    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="LXP AI Agent", 
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(inspector_router, prefix="/api/v1")