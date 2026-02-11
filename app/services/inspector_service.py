import json, uuid, os, tempfile
from fastapi import HTTPException
from pathlib import Path
from datetime import datetime
from app.core import settings
from .base import BaseGeminiService
from app.core.prompts.inspector_p import IT_INSPECTOR_PROMPT
from app.schemas.inspector_sh import InspectionResult
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.shorts import Shorts
from app.models.shorts_inspection_result import ShortsInspectionResult
import logging

logger = logging.getLogger(__name__)

class InspectorService(BaseGeminiService):
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
        shorts = await session.get(Shorts, shorts_id)
        if not shorts :
            raise HTTPException(status_code = 404, detail=f"[Shorts id : {shorts_id}] 검수 대상 숏츠를 찾을 수 없습니다.")
        
        s3_key = settings.SHORTS_DIR + shorts.video_url.split("/")[-1]
        logger.error(f"s3_key : {s3_key}")
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
        shorts_file = None

        try :
            await self.download_from_s3(s3_key, local_temp_path)
            video_file = await self.upload_and_wait(local_temp_path)

            response = self.model.generate_content(
                [video_file, IT_INSPECTOR_PROMPT],
                generation_config = self.generation_config
            )

            return InspectionResult(**json.loads(response.text))
        
        finally :
            # 리소스 정리
            if os.path.exists(local_temp_path) :
                os.remove(local_temp_path)
            if shorts_file :
                self.delete_remote_file(shorts_file.name)


    async def _save_inspection_result(self, session: AsyncSession, shorts: Shorts, result: InspectionResult) :
        """검수 결과를 DB에 저장
        
        Args:
            session (AsyncSession): 비동기 DB 세션
            shorts (Shorts): 검수 대상 Shorts 객체
            result (InspectionResult): Gemini 분석 결과

        Returns:
            InspectionResult: 저장된 검수 결과 객체
        """
        inspection_status = "Approved" if result.is_it_education else "Rejected"

        new_inspection = ShortsInspectionResult(
            shorts_id = shorts.id,
            inspection_status = inspection_status,
            category = result.category,
            confidence_score = result.confidence_score,
            reason = result.reason,
            created_at = datetime.now()
        )

        # TODO: Shorts 상태 업데이트(AI 검수 완료 / 반려 등)

        session.add(new_inspection)
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