# AI 보고서 생성기

다양한 AI 모델을 활용하여 전문적인 보고서를 자동으로 생성하는 웹 애플리케이션입니다.

## 주요 기능

- 다중 AI 모델 지원 (GPT-4o, Gemini 2.0 Flash, Claude 3.5, Llama 3.3, Mistral AI)
- 자동 전문가 프로필 생성
- 웹 검색 기반 정보 수집 (Google, Naver, Bing)
- 사용자 정의 프롬프트 지원
- PDF 보고서 생성

## 설치 방법

1. Python 3.8 이상 설치
2. 저장소 클론
   ```bash
   git clone <repository-url>
   cd ai-report-generator
   ```

3. 가상환경 생성 및 활성화
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

4. 필요한 패키지 설치
   ```bash
   pip install -r requirements.txt
   ```

5. 환경 변수 설정
   - `.env.example` 파일을 `.env`로 복사
   - 각 AI 서비스의 API 키 입력

## 실행 방법

```bash
streamlit run app.py
```

## API 키 발급 방법

1. OpenAI API 키
   - https://platform.openai.com/ 방문
   - 계정 생성 및 API 키 발급

2. Google Gemini API 키
   - https://makersuite.google.com/ 방문
   - API 키 발급

3. Anthropic Claude API 키
   - https://console.anthropic.com/ 방문
   - API 키 발급

4. Perplexity AI API 키
   - https://www.perplexity.ai/ 방문
   - API 키 발급

5. Meta Llama API 키
   - https://ai.meta.com/ 방문
   - API 키 발급

6. Mistral AI API 키
   - https://console.mistral.ai/ 방문
   - API 키 발급

## 사용 방법

1. 웹 인터페이스 접속 (기본: http://localhost:8501)
2. 필요한 API 키 입력
3. 입력 방식 선택 (구글 시트 연동 또는 직접 입력)
4. 사용할 AI 모델 선택
5. 프롬프트 모드 선택 (자동 전문가 모드 또는 사용자 정의 모드)
6. 보고서 옵션 설정
7. "보고서 생성" 버튼 클릭

## 주의사항

- API 키는 절대 공개하지 마세요
- API 사용량과 비용에 주의하세요
- 생성된 보고서의 내용을 반드시 검증하세요

## 라이선스

MIT License 