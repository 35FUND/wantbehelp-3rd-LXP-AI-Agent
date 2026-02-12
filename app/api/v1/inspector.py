from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated, Optional

from app.core.config import settings
from app.models import get_session, ShortsInspectionResult
from app.schemas import APIResponse, CATEGORY_MAP, InspectionListItem
from app.services import InspectorService, InspectorAIService

router = APIRouter()

# 의존성 주입을 통해 서비스 인스턴스 생성
def get_inspector_service(session: Annotated[AsyncSession, Depends(get_session)]) -> InspectorService:
    return InspectorService(session)
def get_inspector_ai_service(api_key = settings.GEMINI_API_KEY) -> InspectorAIService:
    return InspectorAIService(api_key)

@router.get("/inspections", response_model=APIResponse)
async def get_inspections(
    service: Annotated[InspectorService, Depends(get_inspector_service)],
    offset: int = 0,
    limit: int = 10
):
    """검수 목록 조회 API

    Args:
        service (InspectorService): 영상 검수 서비스 인스턴스
        offset (int, optional): 페이지 오프셋. Defaults to 0.
        limit (int, optional): 페이지 크기. Defaults to 10.

    Returns:
        APIResponse: 검수 목록 응답 모델
    """
    data = await service.get_inspection_list(offset, limit)
    return APIResponse(
        status = "success",
        data = data,
        message = "목록 조회가 완료되었습니다."
    )


@router.post("/inspect/{shorts_id}", response_model = APIResponse, deprecated = True)
async def inspect_shorts(
    shorts_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    service: Annotated[InspectorAIService, Depends(get_inspector_ai_service)]
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
