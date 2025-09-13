# ADJ v2.2 기반 ISO 인증심사 견적 계산 엔진

이 패키지는 ADJ v2.2 규칙에 따라 ISO 인증심사 견적을 자동으로 계산하고 Word 문서로 출력하는 기능을 제공합니다.

## 🎯 주요 기능

- **ENP(유효인원수) 기반 심사일수 산정**: 정규직, 외주, 파트타임, 교대근무자 등을 고려한 정확한 ENP 계산
- **MD5/MD1/MD11 기준 테이블 적용**: IAF MD 표준에 따른 최소 심사일수 테이블
- **통합심사 및 원격심사 감축**: 최대 15%까지 할인 적용
- **Stage별 일수 계산**: Stage1(30%), Stage2(100%), Surveillance(60%), Recert(100%)
- **Word 문서 자동 생성**: 상세한 견적서를 .docx 형식으로 출력

## 📦 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# 패키지 설치 (개발 모드)
pip install -e .
```

## 🚀 사용법

### 1. 명령행 사용

```bash
# 기본 사용
python -m adj_quote_engine.cli --input sample.json --output quotation.docx

# 단가 및 VAT 비율 지정
python -m adj_quote_engine.cli --input sample.json --output quotation.docx --day-rate 1500000 --vat-rate 0.1

# 상세 출력
python -m adj_quote_engine.cli --input sample.json --output quotation.docx --verbose
```

### 2. Python 코드에서 사용

```python
from adj_quote_engine import QuoteEngine, Organization, Site, StandardType

# Organization 객체 생성
organization = Organization(
    client_name="ACME Corporation",
    sites=[
        Site(
            name="본사",
            address="서울시 강남구",
            standards=[StandardType.ISO9001, StandardType.ISO14001],
            total_headcount=100,
            part_time_count=10,
            contractor_count=5,
            shift_workers=20
        )
    ],
    standards=[StandardType.ISO9001, StandardType.ISO14001]
)

# 견적 계산
engine = QuoteEngine()
result = engine.calculate_quote(organization)

# Word 문서 생성
from adj_quote_engine import DocxExporter
exporter = DocxExporter()
exporter.export_docx(result, "quotation.docx")
```

## 📋 JSON 입력 형식

```json
{
  "client_name": "ACME Corporation",
  "client_name_en": "ACME Corporation Ltd.",
  "standards": ["ISO9001", "ISO14001", "ISO45001"],
  "sites": [
    {
      "name": "본사",
      "address": "서울시 강남구 테헤란로 123",
      "standards": ["ISO9001", "ISO14001", "ISO45001"],
      "total_headcount": 150,
      "part_time_count": 15,
      "contractor_count": 8,
      "shift_workers": 25,
      "seasonal_factor": 1.0,
      "repetitive_process": false,
      "remote_audit_ratio": 0.0
    }
  ],
  "integration": {
    "is_integrated": true,
    "integration_level": 0.8,
    "shared_management_system": true,
    "common_processes": true,
    "same_audit_team": true
  },
  "options": {
    "stage1": true,
    "stage2": true,
    "surveillance": true,
    "recert": false,
    "day_rate": 1300000.0,
    "vat_rate": 0.1
  }
}
```

## 🧮 ADJ v2.2 계산 규칙

### ENP(유효인원수) 계산
- 정규직 + 외주 인력 포함
- 파트타임 50% 감축
- 반복공정 10% 감축
- 계절성 가중치 적용 (≥1.0)
- 교대근무자 50% 가산

### Stage별 일수 계산
- Stage2 = MD 테이블 기준일수
- Stage1 = Stage2 × 30%
- Surveillance = Stage2 × 60%
- Recert = Stage2 × 100%

### 할인 적용
- 통합심사: 최대 10% 감축
- 원격심사: 최대 10% 감축
- 총 할인: 최대 15%

### 라운딩 규칙
- 0.5일 단위 라운딩
- 최소 0.5일, 최대 12.5일

## 📁 프로젝트 구조

```
adj_quote_engine/
├── __init__.py              # 패키지 초기화
├── models.py                # 데이터 모델
├── md_tables.py             # MD 테이블
├── adj_rules_v22.py         # ADJ v2.2 규칙
├── pricing.py               # 비용 계산
├── justification.py         # 근거 생성
├── quote_docx.py            # Word 출력
├── cli.py                   # 명령행 인터페이스
├── requirements.txt         # 의존성
├── README.md               # 문서
└── tests/
    ├── __init__.py
    └── sample_payload.json  # 테스트 데이터
```

## 🔧 개발 및 테스트

```bash
# 테스트 실행
python -m adj_quote_engine.cli --input tests/sample_payload.json --output test_quotation.docx --verbose

# 템플릿 생성
python -c "from adj_quote_engine.quote_docx import docx_exporter; docx_exporter.create_template('template.docx')"
```

## 📝 라이선스

이 프로젝트는 LRQA Korea의 내부 사용을 위해 개발되었습니다.

## 🤝 기여

버그 리포트나 기능 요청은 개발팀에 문의해주세요.

## 📞 지원

- 이메일: dal.kim@lrqa.com
- 전화: +82 10-5438-3060
