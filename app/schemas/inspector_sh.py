from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Any

class InspectionResult(BaseModel) :
    """
    영상 검수 결과 스키마

    is_it_education : IT 교육용 여부
    confidence_score : 확신 점수 (0~1 사이 숫자)
    category : 영상 핵심 카테고리
    """
    is_it_education: bool = Field(..., description="IT 교육용 여부")
    confidence_score: float = Field(..., ge=0, le=1)
    reason: str = Field(..., description="검수 사유")
    category: Literal["web", "mobile", "game", "cloud", "devops", 
        "ai", "ax", "security", "network", "hw", "iot", 
        "planning", "design", "career", "tips", "None"
    ] = Field(..., description="영상 핵심 카테고리")

    model_config = ConfigDict(from_attributes = True)
class APIResponse(BaseModel):
    status: str
    data: Any
    message: str
    
# 출력용 매핑
CATEGORY_MAP = {
    "web": "웹 개발", "mobile": "모바일", "game": "게임 개발", 
    "cloud": "클라우드", "devops": "DevOps", "ai": "AI", "ax": "AX",
    "security": "보안", "network": "네트워크", "hw": "HW", "iot": "IoT",
    "planning": "기획", "design": "UI/UX", "career": "커리어", "tips": "업무 꿀팁", "none": "해당없음"
}