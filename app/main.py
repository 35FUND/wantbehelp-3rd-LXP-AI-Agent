# FastAPI 앱 실행 및 미들웨어 설정
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import inspector_router
from sqlmodel import SQLModel
from app.core.scheduler import start_scheduler, scheduler 
from app.models.database import engine
from app.models.shorts import Shorts
from app.models.shorts_inspection_result import ShortsInspectionResult

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