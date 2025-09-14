# LRQA Korea ISO 인증심사 신청서

LRQA Korea의 ISO 인증심사 신청서를 위한 웹 애플리케이션입니다. Google Sheets API를 사용하여 데이터를 저장하고 Netlify에서 호스팅됩니다.

## 기능

- 5단계 다중 페이지 신청서 폼
- 실시간 입력 유효성 검사
- Google Sheets에 데이터 자동 저장
- 이메일 알림 기능
- 반응형 웹 디자인
- 접근성 준수

## 기술 스택

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Netlify Functions (Node.js)
- **Database**: Google Sheets API
- **Hosting**: Netlify
- **Email**: Nodemailer (Gmail SMTP)

## 설치 및 설정

### 1. 프로젝트 복제

```bash
git clone <repository-url>
cd netlify-site
npm install
```

### 2. Google Sheets API 설정

#### 2.1 Google Cloud Console에서 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Sheets API 활성화
4. 서비스 계정 생성 및 JSON 키 파일 다운로드

#### 2.2 Google Sheets 생성

1. Google Sheets에서 새 스프레드시트 생성
2. 시트 이름을 "ISO_Applications"로 변경
3. 스프레드시트 ID 복사 (URL에서 확인 가능)
4. 서비스 계정 이메일에 시트 편집 권한 부여

### 3. 환경 변수 설정

Netlify 대시보드에서 다음 환경 변수를 설정하세요:

#### Google Sheets API 관련
- `GOOGLE_SHEET_ID`: Google Sheets 스프레드시트 ID
- `GOOGLE_PROJECT_ID`: Google Cloud 프로젝트 ID
- `GOOGLE_PRIVATE_KEY_ID`: 서비스 계정 키의 private_key_id
- `GOOGLE_PRIVATE_KEY`: 서비스 계정 키의 private_key
- `GOOGLE_CLIENT_EMAIL`: 서비스 계정 이메일
- `GOOGLE_CLIENT_ID`: 서비스 계정 클라이언트 ID

#### 이메일 설정 (선택사항)
- `ADMIN_EMAIL`: 관리자 이메일 주소 (예: dal.kim@lrqa.com)
- `SMTP_USER`: Gmail 계정 (이메일 전송용)
- `SMTP_PASS`: Gmail 앱 비밀번호

**Gmail 앱 비밀번호 생성 방법:**
1. Google 계정에서 2단계 인증 활성화
2. 계정 설정 > 보안 > 2단계 인증 > 앱 비밀번호
3. 앱 비밀번호 생성 후 `SMTP_PASS`로 설정

### 4. 배포

#### Netlify로 배포

1. [Netlify](https://netlify.com)에 로그인
2. "New site from Git" 선택
3. GitHub 저장소 연결
4. 빌드 설정:
   - Build command: `echo "No build required"`
   - Publish directory: `public`
5. 환경 변수 설정
6. 배포 완료

#### 로컬 개발

```bash
# Netlify CLI 설치
npm install -g netlify-cli

# 로컬 개발 서버 실행
netlify dev
```

## 파일 구조

```
netlify-site/
├── public/                 # 정적 파일들
│   ├── index.html         # 메인 신청서 페이지
│   ├── css/
│   │   └── styles.css     # 스타일시트
│   └── js/
│       └── script.js      # 클라이언트 JavaScript
├── netlify/
│   └── functions/         # Netlify Functions
│       └── submit-application.js
├── netlify.toml           # Netlify 설정
├── package.json           # 의존성 관리
└── README.md             # 이 파일
```

## API 엔드포인트

### POST `/.netlify/functions/submit-application`

신청서 데이터를 Google Sheets에 저장합니다.

#### Request Body
```json
{
  "companyNameKo": "회사명(국문)",
  "companyNameEn": "Company Name (English)",
  "contactName": "담당자명",
  "contactEmail": "contact@company.com",
  "contactPhone": "02-1234-5678",
  "certificationScope": "ISO 9001, ISO 14001",
  "totalEmployees": "100",
  "preferredYear": "2025",
  "preferredMonth": "3",
  // ... 기타 필드들
}
```

#### Response
```json
{
  "success": true,
  "message": "신청서가 성공적으로 제출되었습니다."
}
```

## 보안 고려사항

1. **환경 변수**: 모든 민감한 정보는 환경 변수로 관리
2. **CORS**: 적절한 CORS 헤더 설정
3. **입력 검증**: 클라이언트 및 서버 측 입력 검증
4. **HTTPS**: Netlify에서 자동으로 HTTPS 적용
5. **보안 헤더**: 적절한 보안 헤더 설정

## 문제해결

### 일반적인 문제들

1. **Google Sheets API 권한 오류**
   - 서비스 계정 이메일에 시트 편집 권한이 있는지 확인
   - 환경 변수가 올바르게 설정되었는지 확인

2. **이메일 전송 실패**
   - Gmail 2단계 인증 활성화 후 앱 비밀번호 사용
   - SMTP 설정이 올바른지 확인

3. **Netlify Functions 오류**
   - 함수 로그를 확인하여 오류 메시지 확인
   - 환경 변수가 Netlify 대시보드에서 올바르게 설정되었는지 확인

### 로그 확인

```bash
# Netlify 함수 로그 확인
netlify functions:log submit-application
```

## 라이선스

MIT License

## 지원

문제가 발생하거나 문의사항이 있으시면 다음으로 연락해주세요:
- 이메일: kyungmin.yeo@lrqa.com
- 전화: +82 10-5438-3060

## 업데이트 내역

- **v1.0.0**: 초기 릴리스
  - Google Apps Script에서 Netlify로 이전
  - Google Sheets API 직접 연동
  - 이메일 알림 기능 추가
  - 반응형 디자인 적용 