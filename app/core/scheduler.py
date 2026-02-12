import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from app.models.database import get_session_for_scheduler
from app.models.shorts import Shorts
from app.services.inspector_ai_service import InspectorAIService
from app.core.config import settings

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def auto_inspection_job() :
    """주기적으로 PENDING 상태의 숏츠를 찾아 검수해주는 스케줄러"""

    async with get_session_for_scheduler() as session :
        statement = (
            select(Shorts)
            .where(Shorts.status == "PENDING")
            .options(selectinload(Shorts.author))
            .limit(5)
        )
        result = await session.execute(statement)
        pending_shorts = result.scalars().all()

        if not pending_shorts :
            logger.info("검수 대기 중인 숏츠가 없습니다")
            return
        
        logger.info(f"[Scheduler[ {len(pending_shorts)}건의 검수를 시작합니다.]]")

        inspector_service = InspectorAIService(api_key = settings.GEMINI_API_KEY)

        for shorts in pending_shorts :
            try :
                await inspector_service.run_process_inspection(session, shorts.id)
                logger.info(f"[Scheduler] Shorts ID {shorts.id} 검수가 완료되었습니다.")
            except Exception as e :
                logger.error(f"[Scheduler] Shorts ID {shorts.id} 검수 중 오류 : {str(e)}")
                shorts.status = "REJECT"
                await session.commit()

def start_scheduler() :
    """스케줄러 시작 시간 설정"""

    scheduler.add_job(
        auto_inspection_job, 
        "interval", 
        days=settings.INSPECTOR_JOB_INTERVAL_DAYS,
        hours=settings.INSPECTOR_JOB_INTERVAL_HOURS,
        minutes=settings.INSPECTOR_JOB_INTERVAL_MINUTES,
        seconds=settings.INSPECTOR_JOB_INTERVAL_SECONDS,
        id="video_inspection_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info(
        f"### 비디오 검수 스케줄러 시작됨 "
        f"(주기: {settings.INSPECTOR_JOB_INTERVAL_DAYS}일 "
        f"{settings.INSPECTOR_JOB_INTERVAL_HOURS}시간 "
        f"{settings.INSPECTOR_JOB_INTERVAL_MINUTES}분 "
        f"{settings.INSPECTOR_JOB_INTERVAL_SECONDS}초) ###"
    )