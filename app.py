import os
import json
from flask import Flask, request, redirect, url_for, session, render_template, jsonify
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- 1. 기본 설정 ---
app = Flask(__name__)
# 환경 변수에서 SECRET_KEY 가져오기 (Vercel 배포 시 설정 필요)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Flask 세션 설정 (쿠키 기반 세션 사용 - Vercel 서버리스 환경에 적합)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_COOKIE_SECURE"] = os.environ.get('FLASK_ENV') != 'development'  # HTTPS에서만 쿠키 전송
app.config["SESSION_COOKIE_HTTPONLY"] = True  # XSS 공격 방지
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Google OAuth 2.0 설정
# 환경 변수에서 클라이언트 정보 가져오기 (없으면 client_secrets.json 사용 - 로컬 개발용)
SCOPES = ["https://www.googleapis.com/auth/forms.body"]  # Google Forms 생성 권한

def get_client_config():
    """환경 변수 또는 파일에서 클라이언트 설정을 가져옵니다."""
    # Vercel 배포 환경: 환경 변수 사용
    if os.environ.get('GOOGLE_CLIENT_ID') and os.environ.get('GOOGLE_CLIENT_SECRET'):
        return {
            "web": {
                "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
                "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [os.environ.get('GOOGLE_REDIRECT_URI', '')]
            }
        }
    # 로컬 개발 환경: client_secrets.json 파일 사용
    else:
        CLIENT_SECRETS_FILE = "client_secrets.json"
        with open(CLIENT_SECRETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

# --- 2. 라우트(페이지) 정의 ---

@app.route("/")
def index():
    """메인 페이지 렌더링"""
    # 세션에 'credentials'가 있으면 로그인 된 상태로 간주
    if 'credentials' in session:
        return render_template("index.html", logged_in=True)
    return render_template("index.html", logged_in=False)

@app.route("/auth/google")
def auth_google():
    """Google 로그인 시작"""
    # OAuth 2.0 흐름(flow) 객체 생성
    client_config = get_client_config()
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config, scopes=SCOPES)
    
    # 사용자를 어디로 리디렉션할지(콜백 URL) 설정
    flow.redirect_uri = url_for('auth_google_callback', _external=True)

    # 인증 URL 생성 및 리디렉션
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent')

    # 상태(state)를 세션에 저장하여 CSRF 공격 방지
    session['state'] = state
    return redirect(authorization_url)

@app.route("/auth/google/callback")
def auth_google_callback():
    """Google 로그인 후 콜백 처리"""
    # CSRF 방지: 세션의 state와 Google이 보낸 state가 일치하는지 확인
    if 'state' not in session or session['state'] != request.args.get('state'):
        return "Invalid state parameter", 400

    # OAuth 2.0 흐름(flow) 객체 생성
    client_config = get_client_config()
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config, scopes=SCOPES)
    flow.redirect_uri = url_for('auth_google_callback', _external=True)

    # Google로부터 받은 인증 코드로 토큰 교환
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # 발급받은 인증 정보(Access Token, Refresh Token 등)를 세션에 저장
    credentials = flow.credentials
    # credentials 객체를 직렬화 가능한 dict로 변환
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # 로그인 완료 후 메인 페이지로 리디렉션
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    """로그아웃"""
    session.pop('credentials', None)
    return redirect(url_for('index'))

@app.route("/api/create-form", methods=["POST"])
def create_form():
    """프론트엔드로부터 JSON을 받아 Google Form을 생성하는 API"""
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        # 1. 세션에서 인증 정보 복원
        creds_dict = session['credentials']
        credentials = google.oauth2.credentials.Credentials(**creds_dict)

        # 2. Google Forms API 서비스 빌드
        # credentials가 만료되었으면 자동으로 refresh
        forms_service = build('forms', 'v1', credentials=credentials)

        # 3. 프론트엔드에서 보낸 데이터 받기
        request_data = request.json
        if not request_data:
            return jsonify({"error": "No data received"}), 400

        # 설문지 제목과 설명 추출
        survey_title = request_data.get("surveyTitle", "PDF에서 변환된 시험지")
        survey_description = request_data.get("surveyDescription", "")
        questions_data = request_data.get("questions", request_data)  # questions 필드가 없으면 전체를 questions로 간주 (이전 버전 호환)

        # 4. 새 폼 생성 (title만 설정 가능, description은 나중에 batchUpdate로 추가)
        new_form = {
            "info": {
                "title": survey_title if survey_title else "PDF에서 변환된 시험지"
            }
        }
        form = forms_service.forms().create(body=new_form).execute()
        form_id = form['formId']
        form_url = form['responderUri']

        # 5. 문항 데이터를 Google Forms API 형식으로 변환 (batchUpdate)
        requests = []
        
        # 설명이 있으면 먼저 폼 설명을 추가하는 요청을 추가
        if survey_description:
            requests.append({
                "updateFormInfo": {
                    "info": {
                        "description": survey_description
                    },
                    "updateMask": "description"
                }
            })
        
        # 문항 처리
        for i, q in enumerate(questions_data):
            # 문항 번호와 제목 결합
            question_number = q.get("questionNumber", "")
            question_text = q.get("questionText", "제목 없는 질문")
            
            # 문항 번호가 있으면 제목 앞에 추가
            if question_number and question_number.strip():
                title = f"{question_number}. {question_text}".strip()
            else:
                # 문항 번호가 없으면 순서 번호 사용
                title = f"{i+1}. {question_text}".strip()
            
            item_request = {
                "createItem": {
                    "item": {
                        "title": title,
                        "questionItem": {
                            "question": {
                                "required": False,  # 기본값: 필수 아님
                            }
                        }
                    },
                    "location": {"index": i}
                }
            }

            q_type = q.get("questionType", "SHORT_ANSWER")
            options = q.get("options", [])
            
            if q_type == "MULTIPLE_CHOICE" and options:
                # 객관식 (단일 선택, 라디오 버튼)
                item_request["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "RADIO",
                    "options": [{"value": opt} for opt in options]
                }
            elif q_type == "CHECKBOX" and options:
                # 체크박스 (다중 선택)
                item_request["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "CHECKBOX",
                    "options": [{"value": opt} for opt in options]
                }
            elif q_type == "DROPDOWN" and options:
                # 드롭다운
                item_request["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "DROP_DOWN",
                    "options": [{"value": opt} for opt in options]
                }
            elif q_type == "LINEAR_SCALE":
                # 선형 배율 (리커트 척도)
                linear_scale = q.get("linearScale", {})
                item_request["createItem"]["item"]["questionItem"]["question"]["scaleQuestion"] = {
                    "low": linear_scale.get("min", 1),
                    "high": linear_scale.get("max", 5),
                    "lowLabel": linear_scale.get("minLabel", ""),
                    "highLabel": linear_scale.get("maxLabel", "")
                }
            elif q_type == "MULTIPLE_CHOICE_GRID":
                # 객관식 그리드
                # options는 행(questions), 각 option에 대한 선택지는 열(columns)로 구성
                # 예: {"rows": ["항목1", "항목2"], "columns": ["그렇다", "보통", "아니다"]}
                # 구현 복잡도 때문에 단순화: options를 행으로 사용, 기본 5점 척도
                if options:
                    row_questions = options
                    columns = ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다", "전혀 그렇지 않다"]
                    item_request["createItem"]["item"]["questionGroupItem"] = {
                        "questions": [
                            {"required": False, "rowQuestion": {"title": row_q}}
                            for row_q in row_questions
                        ],
                        "grid": {
                            "columns": {
                                "type": "RADIO",
                                "options": [{"value": col} for col in columns]
                            }
                        }
                    }
                    # questionItem 제거
                    del item_request["createItem"]["item"]["questionItem"]
            elif q_type == "CHECKBOX_GRID":
                # 체크박스 그리드
                if options:
                    row_questions = options
                    columns = ["매우 그렇다", "그렇다", "보통이다", "그렇지 않다", "전혀 그렇지 않다"]
                    item_request["createItem"]["item"]["questionGroupItem"] = {
                        "questions": [
                            {"required": False, "rowQuestion": {"title": row_q}}
                            for row_q in row_questions
                        ],
                        "grid": {
                            "columns": {
                                "type": "CHECKBOX",
                                "options": [{"value": col} for col in columns]
                            }
                        }
                    }
                    del item_request["createItem"]["item"]["questionItem"]
            elif q_type == "ESSAY":
                # 주관식 서술형
                item_request["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": True
                }
            else:  # SHORT_ANSWER (기본값)
                # 주관식 단답형
                item_request["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": False
                }
                
            requests.append(item_request)

        # 6. 문항 일괄 추가
        if requests:
            forms_service.forms().batchUpdate(
                formId=form_id, body={"requests": requests}).execute()

        # 7. 성공 응답 (폼 URL 반환)
        return jsonify({
            "message": "Form created successfully!",
            "form_url": form_url
        })

    except HttpError as e:
        print(f"HttpError: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"Error: {e}")
        # 토큰 만료 등의 문제일 수 있으니 세션 클리어
        session.pop('credentials', None)
        return jsonify({"error": f"An error occurred: {e}. Please log in again."}), 500

# --- 3. 서버 실행 ---
if __name__ == "__main__":
    # 로컬 개발 환경에서만 OAUTHLIB_INSECURE_TRANSPORT 설정
    # 프로덕션(Vercel)에서는 HTTPS를 사용하므로 설정하지 않음
    if os.environ.get('FLASK_ENV') == 'development' or not os.environ.get('VERCEL'):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug=True, port=5000)
