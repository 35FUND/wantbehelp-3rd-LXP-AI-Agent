import json, uuid, os, tempfile
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote, urlparse
from app.core import settings
from .base import BaseGeminiService
from app.core.prompts.inspector_p import IT_INSPECTOR_PROMPT
from app.schemas.inspector_sh import InspectionResult
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.shorts import Shorts
from app.models.shorts_inspection_result import InspectionStatus, ShortsInspectionResult
import logging

logger = logging.getLogger(__name__)

class InspectorAIService(BaseGeminiService):
    """영상 검수 에이전트 서비스"""

    async def run_process_inspection(self, session: AsyncSession, shorts_id: int) -> InspectionResult :
        """숏츠 검수 전체 프로세스 실행
        비디오 조회 -> AI 분석 -> 결과 DB 저장

        Args:
            session (AsyncSession): 비동기 DB 세션
            shorts_id (int): 검수 대상 숏츠 ID

        Returns:
            InspectionResult: 저장된 검수 결과 객체
        """
        statement = (
            select(Shorts)
            .where(Shorts.id == shorts_id)
            .options(selectinload(Shorts.author))
        )
        result = await session.execute(statement)
        shorts = result.scalar_one_or_none()

        if not shorts :
            raise HTTPException(status_code = 404, detail=f"[Shorts id : {shorts_id}] 검수 대상 숏츠를 찾을 수 없습니다.")

        s3_key = self._resolve_s3_key(shorts.video_url)
        analysis_result = await self._analyze_with_gemini(s3_key)

        return await self._save_inspection_result(session, shorts, analysis_result)


    async def _analyze_with_gemini(self, s3_key: str) -> InspectionResult :
        """S3 파일을 Gemini로 분석하여 구조화된 결과를 반환합니다
        
        Args:
            s3_key (str): S3 버킷 내 파일 키

        Returns:
            InspectorResult: 검수 결과 데이터 스키마
        """
        local_temp_path = self._get_unique_temp_path(s3_key)
        remote_file = None

        try :
            await self.download_from_s3(s3_key, local_temp_path)
            remote_file = await self.upload_and_wait(local_temp_path)

            response = self.model.generate_content(
                [remote_file, IT_INSPECTOR_PROMPT],
                generation_config = self.generation_config
            )

            return InspectionResult(**json.loads(response.text))
        
        finally :
            # 리소스 정리
            if os.path.exists(local_temp_path) :
                os.remove(local_temp_path)
            if remote_file :
                self.delete_remote_file(remote_file.name)


    async def _save_inspection_result(self, session: AsyncSession, shorts: Shorts, result: InspectionResult) :
        """검수 결과를 DB에 저장
        
        Args:
            session (AsyncSession): 비동기 DB 세션
            shorts (Shorts): 검수 대상 Shorts 객체
            result (InspectionResult): Gemini 분석 결과

        Returns:
            InspectionResult: 저장된 검수 결과 객체
        """
        inspection_status = (
            InspectionStatus.APPROVED.value
            if result.is_it_education
            else InspectionStatus.REJECTED.value
        )
        author_name = shorts.author.nickname if shorts.author else "Unknown"
        
        new_inspection = ShortsInspectionResult(
            shorts_id = shorts.id,
            title = shorts.title,
            author = author_name,
            inspection_status = inspection_status,
            category = result.category,
            confidence_score = result.confidence_score,
            reason = result.reason,
            created_at = datetime.now()
        )

        shorts.status = (
            settings.SHORTS_APPROVED_STATUS
            if result.is_it_education
            else settings.SHORTS_REJECTED_STATUS
        )
        shorts.updated_at = datetime.now()

        session.add(new_inspection)
        session.add(shorts)
        await session.commit()
        await session.refresh(new_inspection)

        return new_inspection

    def _get_unique_temp_path(self, original_filename: str) -> str:
        """
        고유한 UUID 파일명을 생성합니다.
        예: my_video.mp4 -> /tmp/7b9f1...8e2.mp4
        """
        # 1. 파일 확장자 추출 (.mp4 등)
        extension = Path(original_filename).suffix
        
        # 2. UUID 생성 및 확장자 결합
        unique_filename = f"{uuid.uuid4()}{extension}"
        
        # 3. 시스템의 임시 디렉토리(OS 독립적)와 결합
        # 리눅스는 보통 /tmp, 윈도우는 Temp 폴더로 자동 지정됨
        temp_dir = Path(tempfile.gettempdir()) 
        return str(temp_dir / unique_filename)

    def _resolve_s3_key(self, video_url: str | None) -> str:
        if not video_url:
            raise HTTPException(status_code=400, detail="검수 대상 숏츠의 video_url 이 비어 있습니다.")

        parsed = urlparse(video_url)
        raw_path = parsed.path if parsed.scheme else video_url
        normalized_path = unquote(raw_path).lstrip("/")

        if settings.SHORTS_DIR and normalized_path.startswith(settings.SHORTS_DIR):
            return normalized_path

        filename = Path(normalized_path).name
        prefix = settings.SHORTS_DIR.strip("/")
        return f"{prefix}/{filename}" if prefix else filename
