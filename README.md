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
- **Word 문서 자동 생성**: 상세한 견적서를 .docx 형식으로 출력

### 3. 관리자 대시보드
- **신청서 관리**: 접수된 신청서 목록 및 상세 보기
- **견적서 생성**: 신청서 데이터를 기반으로 자동 견적서 생성
- **데이터 내보내기**: CSV, Google Sheets 연동
- **통계 대시보드**: 신청서 현황 및 분석

## 🛠️ 기술 스택

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.8+
- **견적 엔진**: ADJ v2.2 기반 Python 모듈
- **문서 생성**: python-docx
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



