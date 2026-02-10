from fastapi import APIRouter, Depends, HTTPException
from app.services.inspector_service import InspectorService
from app.schemas.inspector_sh import InspectorResult, InspectorResponse, CATEGORY_MAP
from app.core.config import settings

router = APIRouter()

# 의존성 주입을 통해 서비스 인스턴스 생성
def get_inspector_service():
    return InspectorService(api_key=settings.GEMINI_API_KEY)

@router.post("/inspect", response_model=InspectorResponse)
async def inspect_video(
    s3_key: str, 
    service: InspectorService = Depends(get_inspector_service)
):
    """
    S3에 업로드된 영상을 Gemini AI가 검수
    
    Args:
        s3_key: S3 버킷 내의 파일 경로 (예: 'uploads/lecture_01.mp4')
    """
    try:
        # 서비스 호출 (S3 다운로드 -> Gemini 업로드 -> 분석 -> 삭제)
        # result: InspectorResult = await service.inspect_video_from_s3(s3_key)
        result: InspectorResult = await service.inspect_video_mock(s3_key)
        
        # 결과 가공 (사용자에게 줄 상태 메시지 결정)
        status = "Approved" if result.is_it_education else "Rejected"
        
        return InspectorResponse(
            status=status,
            data=result,
            message=f"검수가 완료되었습니다. 결과: {CATEGORY_MAP.get(result.category, '알 수 없음')}"
        )

    except Exception as e:
        # 상세한 에러 로그는 서버 콘솔에 남기고, 클라이언트에게는 500 에러 반환
        print(f"[ERROR] Inspection Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="영상 검수 중 오류가 발생했습니다.")