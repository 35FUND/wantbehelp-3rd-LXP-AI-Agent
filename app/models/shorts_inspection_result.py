from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text
from datetime import datetime
from typing import Optional

class ShortsInspectionResult(SQLModel, table = True) :
    """
    AI 검수 결과 모델

    inspection_status: 검수 결과(Approved, Rejected)
    category: AI가 판단한 카테고리
    confidence_score: 확신 점수
    reason: 검수 결과 사유 요약
    created_at: 생성 일시
    """
    __tablename__ = "shorts_inspection_results"

    id: Optional[int] = Field(default = None, primary_key = True)
    shorts_id: int = Field(foreign_key = "shorts.id", index = True)
    
    inspection_status: str # Approved, Rejected
    category: str
    confidence_score: float
    reason: str = Field(sa_column=Column(Text(collation="utf8mb4_unicode_ci")))

    created_at: datetime = Field(default_factory = datetime.now)

    @property
    def is_it_education(self) -> bool :
        return self.inspection_status == "Approved"
    
    @is_it_education.setter
    def is_it_education(self, value: bool) :
        self.inspection_status = "Approved" if value else "Rejected"