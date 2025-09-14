# LRQA 견적서 생성 API

이 API는 LRQA ISO 신청서 데이터를 기반으로 정교한 견적서를 생성하는 Python 백엔드 서비스입니다.

## 기능

- **정교한 견적 계산**: `adj_quote_engine` 모듈을 활용한 심사일수 산정
- **Word 문서 생성**: LRQA 템플릿을 사용한 전문적인 견적서 생성
- **RESTful API**: Flask 기반의 간단하고 안정적인 API

## 설치 및 실행

### 로컬 개발

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

### Railway 배포

1. Railway 계정에 로그인
2. 새 프로젝트 생성
3. GitHub 저장소 연결
4. 자동 배포 완료

## API 엔드포인트

### GET /health
헬스 체크

**응답:**
```json
{
  "status": "healthy",
  "message": "Quotation API is running"
}
```

### POST /generate-quotation
견적서 생성

**요청:**
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "applicationData": {
    "법인명(국문)": "ABC회사",
    "ISO표준": "ISO 9001, ISO 14001",
    "총직원수": "50",
    "본사주소": "서울시 강남구",
    "담당자명": "홍길동",
    "담당자이메일": "hong@abc.com",
    "담당자전화": "010-1234-5678"
  }
}
```

**응답:**
- 성공: Word 문서 파일 (.docx)
- 실패: JSON 오류 메시지

## 기술 스택

- **Backend**: Flask, Python
- **Document Generation**: python-docx, docxtemplater
- **Deployment**: Railway
- **CORS**: Flask-CORS

## 파일 구조

```
quotation-api/
├── app.py                 # Flask 메인 애플리케이션
├── requirements.txt       # Python 의존성
├── railway.json          # Railway 배포 설정
├── adj_quote_engine/      # 견적 계산 엔진
│   ├── models.py
│   ├── calculator.py
│   ├── pricing.py
│   └── quote_template.py
└── templates/             # LRQA 템플릿 파일
    └── LRQA_quotation.docx
```

## 개발자 정보

- **개발**: AI Assistant
- **버전**: 1.0.0
- **업데이트**: 2024-09-14
