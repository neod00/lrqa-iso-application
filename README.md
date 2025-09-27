# LRQA ISO 인증심사 신청서 시스템

## 📋 프로젝트 개요

LRQA의 ISO 9001, 14001, 45001 인증심사 신청서 작성 및 견적서 생성 시스템입니다.

## 🚀 주요 기능

### 1. 웹 ISO 신청서
- **7페이지 다단계 신청서**: 체계적인 ISO 인증 신청서 작성
- **실시간 유효성 검사**: 필드별 입력 검증 및 안내
- **자동 저장 & 복원**: 브라우저 새로고침 시에도 작성 내용 보존
- **다크모드 지원**: 사용자 친화적인 테마 전환
- **반응형 디자인**: 모든 디바이스에서 최적화된 사용 경험

### 2. 심사일수 산정 및 견적서 생성
- **ADJ v2.2 기반 정확한 견적 계산**: IAF MD 표준에 따른 최소 심사일수 테이블 적용
- **ENP(유효인원수) 산정**: 정규직, 외주, 파트타임, 교대근무자 등을 고려한 정확한 계산
- **통합심사 및 원격심사 감축**: 최대 15%까지 할인 적용
- **Stage별 일수 계산**: Stage1(30%), Stage2(100%), Surveillance(60%), Recert(100%)
- **Jinja2 템플릿 시스템**: 안전하고 유연한 Word 문서 생성
- **Word 문서 자동 생성**: 상세한 견적서를 .docx 형식으로 출력

### 3. 관리자 대시보드
- **신청서 관리**: 접수된 신청서 목록 및 상세 보기
- **견적서 생성**: 신청서 데이터를 기반으로 자동 견적서 생성
- **데이터 내보내기**: CSV, Google Sheets 연동
- **통계 대시보드**: 신청서 현황 및 분석

### 4. Jinja2 템플릿 시스템 (NEW!)
- **안전한 변수 치환**: `{{ 변수명 }}` 문법으로 안전한 템플릿 처리
- **포맷팅 필터**: `{{ total_cost|format_currency }}` 등 유연한 데이터 포맷팅
- **조건문 지원**: `{% if has_iso9001 %}포함{% endif %}` 등 동적 콘텐츠 생성
- **오류 처리**: 템플릿 렌더링 오류 시 상세한 디버깅 정보 제공
- **테스트 도구**: `test_template.py`로 템플릿 검증 가능

## 🛠️ 기술 스택

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.8+
- **견적 엔진**: ADJ v2.2 기반 Python 모듈
- **템플릿 엔진**: Jinja2 (안전한 변수 치환 및 필터)
- **문서 생성**: python-docx + DocxTemplate
- **배포**: GitHub Pages + Netlify

## 📁 프로젝트 구조

```
├── index.html              # 메인 신청서 페이지
├── admin.html              # 관리자 대시보드
├── quotation.html          # 견적서 생성 페이지
├── css/                    # 스타일시트
├── js/                     # JavaScript 파일
├── adj_quote_engine/       # 견적서 생성 엔진
│   ├── cli.py             # 명령행 인터페이스
│   ├── models.py          # 데이터 모델
│   ├── adj_rules_v22.py   # ADJ v2.2 규칙
│   ├── pricing.py         # 가격 계산
│   └── quote_docx.py      # Word 문서 생성
├── quotation-api/          # 견적서 API 서버
│   ├── simple_server.py   # Flask API 서버
│   ├── audit_days_api.py  # 심사일수 계산 API
│   ├── test_template.py   # 템플릿 테스트
│   ├── jinja2_template_guide.md  # Jinja2 사용 가이드
│   └── JINJA2_MIGRATION_REPORT.md  # 마이그레이션 보고서
├── vercel-deploy/          # Vercel 배포 파일
│   └── public/templates/   # Word 템플릿
│       ├── LRQA_quotation.docx  # 기본 템플릿
│       └── LRQA_quotation_improved.docx  # Jinja2 개선 템플릿
└── test_data/             # 테스트 데이터
```

## 🚀 설치 및 실행

### 1. 로컬 개발 환경

```bash
# 저장소 클론
git clone https://github.com/neod00/lrqa-iso-application_r1.git
cd lrqa-iso-application_r1

# Python 의존성 설치
pip install -r adj_quote_engine/requirements.txt

# 웹 서버 실행
python -m http.server 8000
```

### 2. 견적서 생성 테스트

```bash
# 테스트 데이터로 견적서 생성
cd adj_quote_engine
python cli.py --input ../test_data/iphone_company_test.json --output test_quotation.docx --verbose
```

### 3. Jinja2 템플릿 테스트

```bash
# 템플릿 렌더링 테스트
cd quotation-api
python test_template.py
```

## 📖 사용 방법

### 1. 신청서 작성
1. `index.html` 접속
2. 7페이지 신청서 작성
3. 실시간 유효성 검사 확인
4. 신청서 제출

### 2. 관리자 대시보드
1. `admin.html` 접속
2. 로그인: `admin` / `lrqa2025`
3. 신청서 목록 확인
4. 견적서 생성

### 3. 견적서 생성
1. 관리자 대시보드에서 "견적서 관리" 탭
2. "견적서 생성하기" 버튼 클릭
3. 신청서 데이터 입력
4. Word 문서 자동 생성

### 4. Jinja2 템플릿 사용

#### 템플릿 문법
```jinja2
<!-- 기본 변수 -->
{{ client_name }}
{{ quotation_date }}

<!-- 필터 사용 -->
{{ total_cost|format_currency }}
{{ total_employees|format_number }}명
{{ quotation_date|format_date }}

<!-- 조건문 -->
{% if has_iso9001 %}
ISO 9001 품질경영시스템 심사
{% endif %}

<!-- 반복문 -->
{% for breakdown in breakdowns %}
{{ breakdown.standard }}: {{ breakdown.days|format_number }}일
{% endfor %}
```

#### 사용 가능한 필터
- `format_currency`: 통화 형식 (예: 1,500,000원)
- `format_number`: 숫자 천단위 구분자 (예: 1,500)
- `format_date`: 날짜 형식 (예: 2024년 01월 15일)
- `format_boolean`: 불린 값 한글 변환 (예: 예/아니오)

## 🔧 설정

### 환경 변수
```bash
# 견적서 설정
DAY_RATE=1300000          # 1 manday 단가 (KRW)
VAT_RATE=0.1             # VAT 비율 (10%)
```

### Netlify Functions (선택사항)
- `/.netlify/functions/get-applications`: 신청서 목록 조회
- `/.netlify/functions/export-csv`: CSV 내보내기
- `/.netlify/functions/update-application`: 신청서 수정

## 📊 견적서 계산 기준

### ADJ v2.2 규칙
- **기본 심사일수**: IAF MD5 표준 적용
- **복잡도 분류**: QMS(위험도), EMS(환경복잡성), OH&SMS(안전보건위험)
- **통합심사**: 최대 15% 감축
- **원격심사**: 최대 30% 감축

### 가격 구조
- **심사비**: 일당 1,300,000원
- **제경비**: 심사비의 10%
- **VAT**: 10% (별도)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

- **프로젝트 링크**: [https://github.com/neod00/lrqa-iso-application_r1](https://github.com/neod00/lrqa-iso-application_r1)
- **LRQA**: [https://www.lrqa.com](https://www.lrqa.com)

## 🙏 감사의 말

- IAF (International Accreditation Forum)
- ADJ (Accreditation and Certification Bodies)
- LRQA (Lloyd's Register Quality Assurance)









