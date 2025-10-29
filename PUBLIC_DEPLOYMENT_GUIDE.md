# 타인에게 앱 제공하기 - Google OAuth 설정 가이드

이 앱을 타인에게 제공하려면 Google OAuth 동의 화면을 **Production 모드**로 변경해야 합니다.

## 📋 현재 상태

현재 Google Cloud Console의 OAuth 동의 화면이 **"Testing" 모드**로 설정되어 있을 가능성이 높습니다. 이 경우:
- ✅ **테스트 사용자로 추가된 계정만** 로그인 가능
- ❌ 일반 사용자는 로그인 불가 (차단 메시지 표시)

## 🚀 타인에게 제공하기 위한 설정

### 방법 1: Production 모드로 변경 (권장)

#### 1단계: Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택

#### 2단계: OAuth 동의 화면 설정
1. 왼쪽 메뉴에서 **APIs & Services** → **OAuth consent screen** 클릭
2. **"PUBLISH APP"** 또는 **"가장 위에 있는 편집"** 버튼 클릭

#### 3단계: 앱 정보 확인 및 채우기
다음 정보를 정확히 입력해야 합니다:

**필수 항목:**
- **App name**: 앱 이름 (예: "PDF 설문지 변환기")
- **User support email**: 지원 이메일 (본인 이메일)
- **Developer contact information**: 개발자 이메일
- **App domain**: 배포된 도메인 (예: `https://your-app.vercel.app`)
- **Application homepage link**: 홈페이지 URL
- **Privacy policy link**: 개인정보 처리방침 URL (필수! 생성 필요)
- **Terms of service link**: 이용약관 URL (선택사항)

**스크opes (권한 범위):**
- `https://www.googleapis.com/auth/forms.body` (Google Forms 생성 권한)

#### 4단계: 앱 게시
1. 모든 필수 정보를 입력한 후
2. 페이지 하단의 **"PUBLISH APP"** 또는 **"Save and Continue"** 버튼 클릭
3. 경고 메시지에서 **"Confirm"** 클릭

⚠️ **중요**: 앱을 게시하면 **Google의 검토 과정**이 시작됩니다. 

### 방법 2: 테스트 사용자 추가 (임시 방편)

**Production 모드로 변경하기 전** 또는 **검토 대기 중**에는 다음 방법을 사용할 수 있습니다:

1. Google Cloud Console → OAuth consent screen
2. **"Test users"** 섹션에서 **"ADD USERS"** 클릭
3. 사용할 사용자의 Google 이메일 주소 추가
4. 저장

이 방법의 제한사항:
- ❌ 테스트 사용자로 추가된 계정만 로그인 가능
- ❌ 사용자마다 수동으로 추가 필요
- ❌ 최대 100명까지만 추가 가능

## ⏳ Google 검토 프로세스

앱을 Production 모드로 게시하면 Google의 검토가 필요합니다:

### 일반적인 검토 시간
- **검증되지 않은 앱**: 보통 7-14일 소요
- **검증된 앱**: 더 빠르거나 즉시 승인될 수 있음

### 검토 중에도 사용 가능한 경우
- **Unverified app** 상태: 사용자가 "Advanced" → "Go to [App Name] (unsafe)"를 클릭하면 사용 가능하지만 경고 표시
- 일부 사용자는 보안 경고 때문에 사용을 꺼려할 수 있음

## 🔒 앱 검증 (선택사항, 권장)

검증을 받으면:
- ✅ 보안 경고 없이 사용 가능
- ✅ 더 많은 사용자에게 신뢰성 제공
- ✅ 더 빠른 승인 가능

### 검증을 받으려면:
1. Google Cloud Console → OAuth consent screen
2. **"Submit for verification"** 버튼 클릭
3. 다음 정보 제공:
   - Privacy Policy (개인정보 처리방침)
   - Security practices (보안 관행)
   - YouTube channel or video (선택사항)
   - Support email

## 📝 Privacy Policy 생성

Production 모드로 게시하려면 **Privacy Policy (개인정보 처리방침)** URL이 **필수**입니다.

### 간단한 Privacy Policy 생성 방법:
1. **GitHub Pages** 또는 **GitHub Gist** 사용
2. **Google Sites** 사용
3. **개인 웹사이트**에 페이지 추가
4. **무료 Privacy Policy 생성 도구** 사용:
   - [Privacy Policy Generator](https://www.privacypolicygenerator.info/)
   - [FreePrivacyPolicy](https://www.freeprivacypolicy.com/)

### Privacy Policy에 포함할 내용:
- 어떤 데이터를 수집하는지
- 데이터를 어떻게 사용하는지
- Google OAuth를 통해 어떤 정보에 접근하는지
- 데이터 보관 정책
- 사용자 권리

**예시 Privacy Policy URL:**
```
https://yourname.github.io/privacy-policy
또는
https://sites.google.com/view/your-app-privacy-policy/home
```

## 🎯 배포 전 체크리스트

- [ ] OAuth 동의 화면 설정 완료
- [ ] Privacy Policy URL 생성 및 입력
- [ ] 앱 이름, 이메일 등 필수 정보 입력
- [ ] Production 모드로 게시 (또는 테스트 사용자 추가)
- [ ] Vercel 환경 변수 설정 (`GOOGLE_REDIRECT_URI` 등)
- [ ] Google Cloud Console에 배포된 도메인을 리디렉션 URI로 추가
- [ ] 테스트 로그인 확인

## ⚠️ 주의사항

1. **Production 모드로 게시하지 않으면**
   - 일반 사용자는 로그인할 수 없습니다
   - "This app is blocked" 오류 발생

2. **Privacy Policy가 없으면**
   - Production 모드로 게시할 수 없습니다

3. **검토가 거부되면**
   - 요청한 정보를 보완하여 다시 제출해야 합니다

4. **권한 범위 변경 시**
   - 다시 검토가 필요할 수 있습니다

## 📚 참고 자료

- [Google OAuth 동의 화면 설정 가이드](https://developers.google.com/identity/protocols/oauth2/policy)
- [OAuth 앱 검증 가이드](https://support.google.com/cloud/answer/9110914)
- [Privacy Policy 작성 가이드](https://support.google.com/cloud/answer/10313155)

## 🆘 문제 해결

### "This app is blocked" 오류가 발생하는 경우
1. OAuth 동의 화면이 Production 모드인지 확인
2. 사용자가 테스트 사용자로 추가되었는지 확인 (Testing 모드인 경우)
3. Google 검토가 완료되었는지 확인

### "This app isn't verified" 경고가 표시되는 경우
- 앱 검증을 받지 않은 상태입니다
- 사용자가 "Advanced" → "Go to [App Name]"을 클릭하면 사용 가능
- 검증을 받으면 이 경고가 사라집니다


