from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.config import settings
from app.models.database import get_session
from app.schemas.inspector_sh import APIResponse, CATEGORY_MAP
from app.services.inspector_service import InspectorService

router = APIRouter()

# 의존성 주입을 통해 서비스 인스턴스 생성
def get_inspector_service():
    return InspectorService(api_key=settings.GEMINI_API_KEY)

@router.post("/inspect/{shorts_id}", response_model = APIResponse)
async def inspect_shorts(
    shorts_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    service: Annotated[InspectorService, Depends(get_inspector_service)]
) :
    """
    임의의 숏츠 ID를 받아 AI 영상 검수 프로세스 실행
    
    Args:
        shorts_id (int): 검수 대상 숏츠 ID
        session (AsyncSession): 비동기 DB 세션
        service (InspectorService): 영상 검수 서비스 인스턴스

    Returns:
        InspectorResponse: 검수 결과 응답 모델
    """

    try:
        inspection_result = await service.run_process_inspection(session, shorts_id)

        status = inspection_result.inspection_status
        
        return APIResponse(
            status = status,
            data = inspection_result,
            message = f"[Shorts id : {shorts_id}] 검수가 완료되었습니다. 상태: {status}"
        )
    
    except HTTPException as he :
        raise he
    except Exception as e :
        raise HTTPException(status_code=500, detail=f"영상 검수 중 오류 발생: {str(e)}")