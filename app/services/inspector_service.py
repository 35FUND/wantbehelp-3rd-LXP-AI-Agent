from sqlmodel import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.models import ShortsInspectionResult
from app.schemas import InspectionListItem

class InspectorService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_inspection_list(
        self, skip: int, limit: int
    ) -> List[InspectionListItem]:
        """검수 목록 조회 및 UI 포맷팅"""
        statement = select(ShortsInspectionResult).order_by(desc(ShortsInspectionResult.created_at))
        
        statement = statement.offset(skip).limit(limit)
        result = await self.session.execute(statement)
        items = result.scalars().all()

        return [
            InspectionListItem(
                shorts_id = item.shorts_id,
                shorts_title = item.title,
                author = item.author,
                inspection_status = item.inspection_status,
                confidence_score = item.confidence_score,
                reason = item.reason,
                created_at=item.created_at
            ) for item in items
        ]