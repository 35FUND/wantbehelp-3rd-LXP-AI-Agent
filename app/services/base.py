import google.generativeai as genai
import asyncio
import os
import boto3
from app.core import settings
from botocore.exceptions import ClientError

class BaseGeminiService :
    """
    공통 Gemini 서비스 로직
    """
    def __init__(self, api_key: str) :
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.generation_config = {"response_mime_type" : "application/json"}
        self.model = genai.GenerativeModel(
            model_name=settings.MODEL_NAME
        )

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
            region_name = settings.AWS_REGION
        )


    async def download_from_s3(self, s3_key: str, local_path: str) :
        """S3에서 영상을 다운로드하여 로컬 임시 경로에 저장
        
        Args:
            s3_key (str): S3 버킷 내 파일 키
            local_path (str): 로컬에 저장할 경로

        Returns:
            str: 다운로드된 파일의 로컬 경로
        """
        try :
            self.s3_client.download_file(settings.S3_BUCKET_NAME, s3_key, local_path)
            return local_path
        except ClientError as e :
            raise Exception(f"S3 Download Failed: {str(e)}")


    async def upload_and_wait(self, file_path: str):
        """Google 서버에 파일을 업로드하고 인코딩이 완료될 때까지 대기
        
        Args:
            file_path (str): 업로드할 파일의 로컬 경로

        Returns:
            genai.File: 업로드된 파일 객체
        """
        video_file = genai.upload_file(path=file_path)
        
        while video_file.state.name == "PROCESSING":
            await asyncio.sleep(3)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            raise Exception("Google AI Video Processing Failed")
            
        return video_file


    def delete_remote_file(self, file_name: str):
        """Google 서버의 파일 삭제
        
        Args:
            file_name (str): 삭제할 파일의 이름
        """
        try:
            genai.delete_file(file_name)
        except Exception as e:
            print(f"Failed to delete remote file {file_name}: {e}")