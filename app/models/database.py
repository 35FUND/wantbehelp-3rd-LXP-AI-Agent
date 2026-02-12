from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from app.core.config import settings

# mysql+aiomysql://user:pass@localhost:3306/dbname
engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 백그라운드 스케줄러용 DB 세션
@asynccontextmanager
async def get_session_for_scheduler() -> AsyncSession:
    async with async_session() as session:
        try :
            yield session
            await session.commit()
        except Exception :
            await session.rollback()
            raise
        finally :
            await session.close()

            
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session