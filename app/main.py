# FastAPI 앱 실행 및 미들웨어 설정
from fastapi import FastAPI
from app.api.v1 import inspector_router

app = FastAPI(title="LXP AI Agent", version="1.0.0")

app.include_router(inspector_router, prefix="/api/v1")