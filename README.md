# PDF to Google Form 변환기

PDF 설문지를 Google Form으로 자동 변환하는 웹 애플리케이션입니다.

## 주요 기능

- 📄 PDF 파일 업로드
- 🤖 AI(Gemini)를 통한 자동 질문 분석 및 구조화
- 📝 Google Forms 자동 생성
- 🔐 Google OAuth 2.0 인증

## 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **AI**: Google Gemini API
- **Google APIs**: Google Forms API, Google OAuth 2.0
- **배포**: Vercel

## 로컬 개발 환경 설정

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`client_secrets.json` 파일을 생성하고 Google OAuth 클라이언트 정보를 입력합니다.

### 3. Flask 앱 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 배포

이 프로젝트는 Vercel을 통해 배포됩니다.

자세한 배포 가이드는 `VERCEL_DEPLOY.md`를 참고하세요.

## 라이선스

MIT

