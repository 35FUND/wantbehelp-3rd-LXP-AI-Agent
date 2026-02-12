from app.models.user import User
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Shorts(SQLModel, table=True):
    __tablename__ = "shorts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    category_id: int
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_sec: Optional[int] = None
    like_count: int = Field(default=0)
    view_count: int = Field(default=0)
    status: Optional[str] = None  # DRAFT, PUBLISHED, ARCHIVED -> 여기서 검수 결과에 따라 변경됨
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # 역방향 관계 설정
    author: Optional["User"] = Relationship(back_populates="shorts_list")