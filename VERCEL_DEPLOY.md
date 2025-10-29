# Vercel 배포 가이드

이 문서는 Flask 앱을 Vercel에 안전하게 배포하는 방법을 설명합니다.

## 📋 사전 준비사항

1. [Vercel 계정](https://vercel.com) 생성
2. [Vercel CLI](https://vercel.com/cli) 설치 (선택사항)
3. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 확인

## 🔐 환경 변수 설정

Vercel 대시보드에서 다음 환경 변수들을 설정해야 합니다:

### 1. Vercel 프로젝트 설정 페이지로 이동
- 프로젝트 선택 → Settings → Environment Variables

### 2. 필수 환경 변수 추가

#### **SECRET_KEY**
```
이름: SECRET_KEY
값: (랜덤한 32자 이상 문자열, 예: openssl rand -hex 32)
```
**용도**: Flask 세션 암호화 키

#### **GOOGLE_CLIENT_ID**
```
이름: GOOGLE_CLIENT_ID
값: (Google Cloud Console의 클라이언트 ID)
예: 52859254833-2psonv27ih0o2os31bak5g0v8prj2b27.apps.googleusercontent.com
```
**용도**: Google OAuth 클라이언트 ID

#### **GOOGLE_CLIENT_SECRET**
```
이름: GOOGLE_CLIENT_SECRET
값: (Google Cloud Console의 클라이언트 비밀번호)
예: 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
```
**용도**: Google OAuth 클라이언트 비밀번호

#### **GOOGLE_REDIRECT_URI**
```
이름: GOOGLE_REDIRECT_URI
값: https://your-app-name.vercel.app/auth/google/callback
```
**용도**: OAuth 콜백 URL (배포 후 실제 도메인으로 변경 필요)

**⚠️ 중요**: 
- 배포 후 생성된 도메인을 확인하고 `GOOGLE_REDIRECT_URI`를 업데이트해야 합니다.
- Google Cloud Console의 "승인된 리디렉션 URI"에도 동일한 URL을 추가해야 합니다.

#### **GEMINI_API_KEY** (선택사항)
```
이름: GEMINI_API_KEY
값: (Gemini API 키)
```
**용도**: 프론트엔드에서 Gemini API 호출 시 사용 (현재는 프론트엔드에 하드코딩되어 있지만, 보안을 위해 환경 변수로 이동 권장)

## 📝 Google Cloud Console 설정

### 1. 승인된 리디렉션 URI 추가
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. APIs & Services → Credentials
3. OAuth 2.0 클라이언트 ID 선택
4. "승인된 리디렉션 URI"에 다음 추가:
   ```
   https://your-app-name.vercel.app/auth/google/callback
   ```
5. 저장

## 🚀 배포 방법

### 방법 1: Vercel CLI 사용 (권장)

```bash
# 1. Vercel CLI 설치 (글로벌)
npm install -g vercel

# 2. Vercel에 로그인
vercel login

# 3. 프로젝트 디렉토리에서 배포
cd form-app
vercel

# 4. 환경 변수 설정 (대시보드에서도 가능)
vercel env add SECRET_KEY
vercel env add GOOGLE_CLIENT_ID
vercel env add GOOGLE_CLIENT_SECRET
vercel env add GOOGLE_REDIRECT_URI

# 5. 프로덕션 배포
vercel --prod
```

### 방법 2: GitHub 연동

1. GitHub에 코드 푸시
2. [Vercel 대시보드](https://vercel.com/new)에서 "Import Project" 클릭
3. GitHub 저장소 선택
4. "Root Directory"를 `.`로 설정
5. 환경 변수 설정 (위의 환경 변수 섹션 참조)
6. "Deploy" 클릭

## 🔍 배포 후 확인사항

1. **도메인 확인**
   - 배포 완료 후 Vercel이 제공하는 URL 확인 (예: `https://form-app-xxx.vercel.app`)
   - 이 URL을 `GOOGLE_REDIRECT_URI`에 설정

2. **Google Cloud Console 업데이트**
   - 승인된 리디렉션 URI에 Vercel 도메인 추가

3. **환경 변수 확인**
   - Vercel 대시보드 → Settings → Environment Variables에서 모든 변수가 설정되었는지 확인

4. **테스트**
   - 배포된 URL 접속
   - Google 로그인 테스트
   - 폼 생성 기능 테스트

## 🔒 보안 고려사항

✅ **권장사항:**
- 환경 변수에 민감한 정보 저장 (client_secrets.json은 로컬 개발용)
- `SECRET_KEY`는 충분히 긴 랜덤 문자열 사용
- HTTPS 강제 (Vercel은 기본적으로 HTTPS 제공)
- 세션 쿠키는 HttpOnly 및 Secure 플래그 설정

⚠️ **주의사항:**
- `client_secrets.json` 파일을 Git에 커밋하지 않도록 `.gitignore`에 추가
- 환경 변수는 Vercel 대시보드에서만 관리
- 프로덕션 환경에서는 `OAUTHLIB_INSECURE_TRANSPORT`를 사용하지 않음 (현재 코드에서 자동 처리)

## 📂 파일 구조

```
form-app/
├── app.py                 # Flask 애플리케이션
├── requirements.txt       # Python 의존성
├── vercel.json           # Vercel 설정 파일
├── .vercelignore         # Vercel 배포 시 제외할 파일
├── client_secrets.json   # 로컬 개발용 (Git에 커밋하지 말 것!)
├── templates/
│   └── index.html        # 프론트엔드
└── VERCEL_DEPLOY.md      # 이 문서
```

## 🐛 문제 해결

### OAuth 오류
- `GOOGLE_REDIRECT_URI`가 Vercel 도메인과 일치하는지 확인
- Google Cloud Console의 리디렉션 URI 설정 확인

### 세션 오류
- `SECRET_KEY`가 올바르게 설정되었는지 확인
- 쿠키가 브라우저에서 허용되는지 확인

### 배포 실패
- `requirements.txt`에 필요한 패키지가 모두 포함되어 있는지 확인
- Vercel 로그 확인: Vercel 대시보드 → Deployments → 해당 배포 → Logs

## 📚 추가 자료

- [Vercel Python 문서](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Google OAuth 2.0 문서](https://developers.google.com/identity/protocols/oauth2)


