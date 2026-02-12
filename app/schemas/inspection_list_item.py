from pydantic import BaseModel, Field
from datetime import datetime

class InspectionListItem(BaseModel) :
    """영상 검수 상태 스키마(목록용)
    
    """
    shorts_id : int = Field(..., description = "숏츠 ID")
    shorts_title : str = Field(..., description = "숏츠 제목")
    author : str = Field(..., description = "숏츠 작성자")
    inspection_status : str = Field(..., description = "검수 상태")
    confidence_score: float = Field(..., ge=0, le=1)
    reason: str = Field(..., description="검수 사유")
    registed_at : datetime = Field(default = None, description = "숏츠 등록 일시")
