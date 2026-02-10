import json
import uuid
import os
import tempfile
from fastapi import HTTPException
from pathlib import Path
from .base import BaseGeminiService
from app.core.prompts.inspector_p import IT_INSPECTOR_PROMPT
from app.schemas.inspector_sh import InspectorResult

class InspectorService(BaseGeminiService):
    """영상 검수 에이전트 서비스"""
    async def inspect_video_from_s3(self, s3_key: str) -> InspectorResult:
        """
        S3에 저장된 영상을 Gemini로 검수하고 결과 반환

        Args:
            s3_key (str): S3 버킷 내 파일 키

        Returns:
            InspectorResult: 검수 결과 데이터 스키마
        """
        # 1. 로컬 경로 설정
        local_temp_path = _get_unique_temp_path(s3_key)
        video_file = None
        
        try:
            # S3에서 파일 가져오기
            await self.download_from_s3(s3_key, local_temp_path)

            # Gemini 업로드 및 대기
            video_file = await self.upload_and_wait(local_temp_path)

            # 분석 수행
            response = self.model.generate_content([video_file, IT_INSPECTOR_PROMPT])
            validated_data = InspectorResult(**json.loads(response.text))
            
            return validated_data

        finally:
            # 모든 리소스 정리 (로컬 임시 파일 + Gemini 원격 파일)
            if os.path.exists(local_temp_path):
                os.remove(local_temp_path)
            if video_file:
                self.delete_remote_file(video_file.name)


def _get_unique_temp_path(original_filename: str) -> str:
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