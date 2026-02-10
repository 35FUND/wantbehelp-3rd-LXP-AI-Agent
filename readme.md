📺 IT Video Inspector Agent
FastAPI와 Gemini 2.5 Flash를 활용한 IT 전문 교육 콘텐츠 자동 검수 시스템이다. 업로드된 영상이 개발, 기획, 디자인, 데이터 등 IT 실무자를 위한 교육적 가치가 있는지 AI Agent가 심층 분석하여 승인 여부를 결정한다.

🚀 핵심 기능
멀티모달 분석: 영상의 시각적 요소(코드, 도식, IDE)와 오디오(기술 용어, 강의 내용)를 동시에 분석.

지능형 검수 로직: 단순 키워드 매칭이 아닌, '실무 적용 가능성'과 '학습 맥락'을 기준으로 판별.

Rate Limit 방어: 무료 티어 API의 제한을 고려한 asyncio.Lock 기반의 요청 제어.

자동 리소스 정리: 분석 완료 후 Google AI 스토리지 및 로컬 임시 파일을 즉시 삭제하여 효율성 유지.

🏗 프로젝트 구조 (Package Structure)
확장성을 고려하여 관심사 분리(SoC) 원칙에 따라 설계되었다. 추후 '추천 Agent' 등 새로운 기능이 추가되어도 기존 로직을 수정하지 않고 확장 가능하다.

Plaintext

app/
├── main.py              # FastAPI 진입점 및 라우팅
├── core/
│   ├── config.py        # 환경 변수 및 설정 (Gemini API Key 등)
│   └── security.py      # Rate Limiter 및 보안 로직
├── services/
│   ├── __init__.py      # Service Layer 진입점
│   ├── inspector.py     # 영상 검수 핵심 로직 (Gemini 연동)
│   └── recommender.py   # (예정) 추천 엔진 로직
├── schemas/
│   ├── __init__.py
│   └── inspection.py    # Pydantic 모델 (Request/Response 정의)
└── utils/
    └── video_tools.py   # 파일 저장, 포맷 변환 등 유틸리티
.env                     # API_KEY 설정 파일
requirements.txt         # 의존성 패키지
🛠 기술 스택
Backend: FastAPI (Python 3.10+)

AI Model: Google Gemini 2.5 Flash (Multimodal)

Async Control: asyncio (Non-blocking I/O)

Environment: python-dotenv, google-generativeai

📋 검수 기준 (Inspection Policy)
AI Agent는 다음 4가지 카테고리를 기준으로 영상을 평가한다.

Development: 코딩, CS 지식, 인프라, 아키텍처.

Product/Design: 서비스 기획, UI/UX, 협업 툴(Figma/Jira) 가이드.

Data/AI: 데이터 분석, LLM, 프롬프트 엔지니어링.

Tech Trend: 단순 뉴스가 아닌 실무 인사이트를 포함한 기술 동향.

[Strict Rule] 화면에 코드나 툴이 잠깐 등장하는 것만으로는 부족하며, 반드시 설명/절차/데모 등 학습 맥락이 동반되어야 is_it_education: true를 반환한다.

⚙️ 설치 및 실행
1. 환경 변수 설정
.env 파일을 생성하고 발급받은 Gemini API 키를 입력한다.

코드 스니펫

GEMINI_API_KEY=your_google_api_key_here
2. 패키지 설치
Bash

pip install -r requirements.txt
3. 서버 실행
Bash

uvicorn app.main:app --reload
📤 API 사용법 (Example)
POST /check-video
영상을 업로드하면 AI가 분석 결과를 JSON으로 반환한다.

Response Body:

JSON

{
  "is_it_education": true,
  "confidence_score": 0.95,
  "category": "Development",
  "reason": "화면에서 VS Code와 FastAPI 코드가 확인되며, 오디오에서 비동기 처리에 대한 기술적 설명이 명확하게 전달됨."
}
💡 개발자 노트 (Self-Refined)
Error Handling: json.loads() 호출 시 발생할 수 있는 JSONDecodeError를 방지하기 위해, Gemini 모델에 response_mime_type: "application/json" 설정을 권장함. (Pylance의 UndefinedVariable 이슈 해결 포인트)

Scalability: services/ 하위의 각 에이전트는 독립적인 prompt와 schema를 가지도록 설계하여, 추천 에이전트 추가 시 코드 간섭을 최소화함.