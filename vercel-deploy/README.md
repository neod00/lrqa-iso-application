# LRQA ISO 인증 심사 신청 시스템 (Vercel 버전)

이 프로젝트는 LRQA Korea의 ISO 9001, 14001, 45001 인증 심사 신청 및 견적서 생성 시스템입니다.

## 주요 기능

- ✅ **온라인 신청서 제출**: 웹 폼을 통한 신청서 작성 및 제출
- ✅ **자동 견적서 생성**: Python 기반 복잡한 견적 계산 엔진
- ✅ **Word 문서 생성**: LRQA_quotation.docx 템플릿 기반 견적서 생성
- ✅ **이메일 전송**: 견적서 자동 이메일 발송
- ✅ **실시간 견적 계산**: ENP 계산, 할인 적용, 통합심사 지원

## 기술 스택

### Backend
- **Python 3.9**: Vercel Functions
- **docxtpl**: Word 템플릿 처리
- **python-docx**: Word 문서 생성
- **Jinja2**: 템플릿 엔진

### Frontend
- **HTML5/CSS3**: 반응형 웹 디자인
- **JavaScript**: 클라이언트 사이드 로직
- **Fetch API**: 서버 통신

### 배포
- **Vercel**: 서버리스 배포 플랫폼
- **Vercel Functions**: Python 런타임 지원

## 프로젝트 구조

```
vercel-deploy/
├── api/                          # Vercel Functions (Python API)
│   ├── create-quotation.py      # 견적서 생성 API
│   ├── submit-application.py    # 신청서 제출 API
│   └── send-email.py            # 이메일 전송 API
├── adj_quote_engine/            # Python 견적 계산 엔진
│   ├── models.py                # 데이터 모델
│   ├── quote_template.py        # Word 템플릿 처리
│   └── templates/
│       └── LRQA_quotation.docx  # 견적서 템플릿
├── public/                      # 정적 파일
│   ├── index.html              # 메인 페이지
│   └── lrqa-logo.png           # 로고 이미지
├── requirements.txt             # Python 의존성
├── vercel.json                 # Vercel 설정
└── README.md                   # 프로젝트 문서
```

## API 엔드포인트

### 1. 신청서 제출
```
POST /api/submit-application
Content-Type: application/json

{
  "company_name": "회사명",
  "contact_name": "담당자명",
  "contact_email": "이메일",
  "contact_phone": "전화번호",
  "standards": ["ISO 9001", "ISO 14001"],
  "total_employees": 50,
  "sites": [...],
  "integration": {...},
  "options": {...}
}
```

### 2. 견적서 생성
```
POST /api/create-quotation
Content-Type: application/json

{
  // 신청서 데이터와 동일
}
```

### 3. 이메일 전송
```
POST /api/send-email
Content-Type: application/json

{
  "recipient_email": "수신자 이메일",
  "quotation": {
    // 견적서 데이터
  }
}
```

## 로컬 개발 환경 설정

### 1. Vercel CLI 설치
```bash
npm install -g vercel
```

### 2. 프로젝트 클론
```bash
git clone <repository-url>
cd vercel-deploy
```

### 3. 로컬 개발 서버 실행
```bash
vercel dev
```

### 4. 브라우저에서 확인
```
http://localhost:3000
```

## 배포 방법

### 1. Vercel 계정 생성
- [Vercel](https://vercel.com)에서 계정 생성

### 2. GitHub 연동
- GitHub 저장소와 Vercel 계정 연동

### 3. 자동 배포
- `main` 브랜치에 푸시하면 자동 배포
- 또는 Vercel 대시보드에서 수동 배포

### 4. 환경 변수 설정 (선택사항)
- Vercel 대시보드에서 환경 변수 설정
- 이메일 서비스 API 키 등

## 견적 계산 로직

### ENP (Equivalent Number of Personnel) 계산
```
ENP = (총직원수 + 외주직원수 - 파트타임직원수×0.5 + 교대근무직원수×0.5) 
      × 계절성가중치 × 반복프로세스가중치
```

### 심사일수 계산
- **Stage1**: Stage2 × 30%
- **Stage2**: MD 테이블 기준
- **Surveillance**: Stage2 × 60%
- **Recert**: Stage2 × 100%

### 할인 적용
- **통합심사 할인**: 최대 10%
- **원격심사 할인**: 최대 10%
- **총 할인**: 최대 15%

## Word 템플릿 사용법

1. `adj_quote_engine/templates/LRQA_quotation.docx` 파일 수정
2. Jinja2 문법 사용:
   - `{{ client_name }}`: 회사명
   - `{{ total_cost }}`: 총 견적 금액
   - `{% for breakdown in breakdowns %}`: 반복문

## 문제 해결

### 1. Python 모듈 import 오류
- `PYTHONPATH` 환경 변수 확인
- `adj_quote_engine` 폴더 구조 확인

### 2. Word 문서 생성 실패
- `LRQA_quotation.docx` 템플릿 파일 존재 확인
- `docxtpl` 라이브러리 설치 확인

### 3. CORS 오류
- `vercel.json`의 CORS 헤더 설정 확인
- API 응답 헤더 확인

## 라이선스

© 2024 LRQA Korea. All rights reserved.

## 문의

- **이메일**: info@lrqa.co.kr
- **전화**: 02-1234-5678
- **웹사이트**: https://lrqa.co.kr

