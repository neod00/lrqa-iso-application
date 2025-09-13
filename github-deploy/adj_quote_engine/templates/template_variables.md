# LRQA 견적서 템플릿 변수 목록

이 문서는 `LRQA_quotation_template.docx` 파일에 추가해야 하는 Jinja2 변수들을 설명합니다.

## 기본 정보 변수

### 회사 정보
- `{{ client_name }}` - 회사명 (한글)
- `{{ client_name_en }}` - 회사명 (영문)
- `{{ client_address }}` - 회사 주소
- `{{ contact_person }}` - 담당자 성함
- `{{ contact_email }}` - 담당자 이메일
- `{{ contact_phone }}` - 담당자 전화번호

### 견적 정보
- `{{ quotation_date }}` - 견적서 작성일 (예: 2025년 09월 06일)
- `{{ quotation_number }}` - 견적서 번호 (예: LRQA-20250906-1234)
- `{{ valid_until }}` - 견적 유효기간 (예: 2025년 12월 06일)

### 표준 정보
- `{{ standards_text }}` - 신청 표준 목록 (예: ISO9001, ISO14001, ISO45001)

## 사업장 정보

### 사업장 목록 (반복)
```
{% for site in sites %}
{{ site.number }}. {{ site.name }}
   주소: {{ site.address }}
   직원수: {{ site.headcount }}명
   적용표준: {{ site.standards }}
   주요활동: {{ site.activities }}
{% endfor %}
```

### 사업장 요약
- `{{ total_sites }}` - 총 사업장 수
- `{{ total_employees }}` - 총 직원 수

## 직원 구성 정보

### 직원 구성표
- `{{ employee_breakdown.total }}` - 총 직원 수
- `{{ employee_breakdown.permanent }}` - 정규직 수
- `{{ employee_breakdown.temporary }}` - 비정규직 수
- `{{ employee_breakdown.contractors }}` - 협력업체 직원 수

## 견적 상세 정보

### 견적 요약
- `{{ total_audit_days }}` - 총 심사일수
- `{{ subtotal }}` - VAT 제외 금액
- `{{ vat_amount }}` - VAT 금액
- `{{ total_cost }}` - 총 견적 금액

### 표준별 상세 (반복)
```
{% for detail in quotation_details %}
{{ detail.standard_name }} ({{ detail.standard }})
   ENP: {{ detail.enp }}명
   복잡도: {{ detail.complexity }}
   Stage1: {{ detail.stage1_days }}일 ({{ detail.stage1_cost | int | format_currency }})
   Stage2: {{ detail.stage2_days }}일 ({{ detail.stage2_cost | int | format_currency }})
   Surveillance: {{ detail.surveillance_days }}일 ({{ detail.surveillance_cost | int | format_currency }})
   Recert: {{ detail.recert_days }}일 ({{ detail.recert_cost | int | format_currency }})
   소계: {{ detail.total_days }}일 ({{ detail.total_cost | int | format_currency }})
{% endfor %}
```

## 할인 정보

### 통합심사 할인
- `{{ is_integrated }}` - 통합심사 여부 (true/false)
- `{{ integration_discount }}` - 통합심사 할인율 (%)

### 원격심사 할인
- `{{ remote_audit_ratio }}` - 원격심사 비율 (%)
- `{{ remote_discount }}` - 원격심사 할인율 (%)

## 가정 및 근거

### 가정 사항
```
{% for assumption in assumptions %}
- {{ assumption }}
{% endfor %}
```

### 근거 사항
```
{% for justification in justification %}
- {{ justification }}
{% endfor %}
```

## 기타 정보

- `{{ created_at }}` - 생성일시
- `{{ prepared_by }}` - 작성자 (예: LRQA Korea)
- `{{ prepared_title }}` - 작성자 소속 (예: 사업개발본부)

## 사용 방법

1. `LRQA_quotation_template.docx` 파일을 열기
2. 변수를 삽입하고 싶은 위치에 `{{ 변수명 }}` 형태로 입력
3. 반복 구문이 필요한 경우 `{% for ... %}` 블록 사용
4. 파일을 저장하고 테스트 실행

## 예시

### 견적서 헤더
```
견적서 번호: {{ quotation_number }}
작성일: {{ quotation_date }}
유효기간: {{ valid_until }}

고객사: {{ client_name }} ({{ client_name_en }})
주소: {{ client_address }}
담당자: {{ contact_person }}
연락처: {{ contact_phone }} / {{ contact_email }}
```

### 견적 요약
```
총 심사일수: {{ total_audit_days }} mandays
서브토탈: {{ subtotal | int | format_currency }}
VAT (10%): {{ vat_amount | int | format_currency }}
총 견적 금액: {{ total_cost | int | format_currency }}
```
