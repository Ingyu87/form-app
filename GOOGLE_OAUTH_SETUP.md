# Google OAuth 설정 가이드

## 문제: 액세스 차단됨 (403 오류: access_denied)

### 원인
- OAuth 동의 화면이 "테스트" 모드로 설정되어 있음
- 사용자 이메일이 테스트 사용자 목록에 등록되지 않음

### 해결 방법

#### 1. Google Cloud Console 접속
https://console.cloud.google.com/

#### 2. 프로젝트 선택
상단에서 해당 프로젝트 선택 (Client ID가 속한 프로젝트)

#### 3. OAuth 동의 화면 설정
1. 좌측 메뉴: **APIs & Services** → **OAuth consent screen**
2. **User Type** 선택:
   - **External**: 외부 사용자 (개발/테스트용)
   - **Internal**: 조직 내부 사용자만 (G Suite)
   
3. **앱 정보 입력**:
   - App name: `PDF to Google Form` (또는 원하는 이름)
   - User support email: 본인 이메일
   - Developer contact information: 본인 이메일

4. **Scopes** 설정:
   - **ADD OR REMOVE SCOPES** 클릭
   - `https://www.googleapis.com/auth/forms.body` 추가

5. **Test users** 섹션:
   - **ADD USERS** 클릭
   - 테스트하려는 사용자 이메일 추가 (`ingyu8705@gmail.com`)
   - **SAVE** 클릭

#### 4. 승인된 리디렉션 URI 확인
1. 좌측 메뉴: **APIs & Services** → **Credentials**
2. OAuth 2.0 Client ID 클릭
3. **Authorized redirect URIs**에 다음이 있는지 확인:
   ```
   http://localhost:5000/auth/google/callback
   ```
   없으면 추가하고 저장

### 참고사항
- 테스트 모드에서는 최대 100명의 테스트 사용자만 추가 가능
- 모든 사용자에게 공개하려면 앱 검증이 필요 (복잡한 과정)
- 로컬 테스트용으로는 테스트 사용자 추가만으로 충분합니다


