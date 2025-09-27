# Jinja2 템플릿 사용 가이드

## 개요
Word 문서 템플릿에서 Jinja2 문법을 사용하여 변수 치환을 수행합니다.

## 사용 가능한 필터

### 1. format_currency
통화 형식으로 포맷팅합니다.
```jinja2
{{ total_cost|format_currency }}
{{ 1500000|format_currency }}
```
결과: `1,500,000원`

### 2. format_number
숫자에 천단위 구분자를 추가합니다.
```jinja2
{{ total_employees|format_number }}
{{ 1500|format_number }}
```
결과: `1,500`

### 3. format_date
날짜를 지정된 형식으로 포맷팅합니다.
```jinja2
{{ quotation_date|format_date }}
{{ quotation_date|format_date('%Y-%m-%d') }}
```
결과: `2024년 01월 15일` 또는 `2024-01-15`

### 4. format_boolean
불린 값을 한글로 변환합니다.
```jinja2
{{ has_iso9001|format_boolean }}
{{ has_iso9001|format_boolean('포함', '미포함') }}
```
결과: `예` 또는 `아니오`

### 5. safe_divide
안전한 나눗셈을 수행합니다 (0으로 나누기 방지).
```jinja2
{{ total_cost|safe_divide(total_audit_days) }}
{{ 1000|safe_divide(0, 0) }}
```
결과: 나눗셈 결과 또는 기본값

## 조건문 사용

### 기본 조건문
```jinja2
{% if has_iso9001 %}
ISO 9001 인증 심사
{% endif %}

{% if has_iso14001 %}
ISO 14001 환경경영시스템 심사
{% else %}
환경경영시스템 심사 없음
{% endif %}
```

### 복합 조건문
```jinja2
{% if has_iso9001 and has_iso14001 %}
품질경영시스템 및 환경경영시스템 통합 심사
{% elif has_iso9001 %}
품질경영시스템 심사
{% elif has_iso14001 %}
환경경영시스템 심사
{% endif %}
```

## 반복문 사용

### breakdowns 반복
```jinja2
{% for breakdown in breakdowns %}
표준: {{ breakdown.standard }}
1단계 일수: {{ breakdown.stage1_days|format_number }}일
2단계 일수: {{ breakdown.stage2_days|format_number }}일
총 일수: {{ (breakdown.stage1_days + breakdown.stage2_days)|format_number }}일
비용: {{ breakdown.stage1_2_cost|format_currency }}
{% endfor %}
```

## 템플릿 변수 예시

### 기본 정보
```jinja2
고객명: {{ client_name }}
고객명(영문): {{ client_name_en }}
주소: {{ client_address }}
견적일: {{ quotation_date|format_date }}
견적번호: {{ quotation_number }}
```

### 비용 정보
```jinja2
총 심사일수: {{ total_audit_days|format_number }}일
일당 단가: {{ day_rate|format_currency }}
총 비용: {{ total_cost|format_currency }}
부가세: {{ vat_amount|format_currency }}
최종 비용: {{ final_cost|format_currency }}
```

### ISO 표준별 정보
```jinja2
{% if has_iso9001 %}
ISO 9001:
- 1단계: {{ iso9001_stage1_days|format_number }}일
- 2단계: {{ iso9001_stage2_days|format_number }}일
- 총 비용: {{ iso9001_stage1_2_cost|format_currency }}
{% endif %}

{% if has_iso14001 %}
ISO 14001:
- 1단계: {{ iso14001_stage1_days|format_number }}일
- 2단계: {{ iso14001_stage2_days|format_number }}일
- 총 비용: {{ iso14001_stage1_2_cost|format_currency }}
{% endif %}
```

## 디버깅 정보
```jinja2
{% if debug_info.api_success %}
✅ 핵심두뇌 API를 통한 정확한 계산
{% else %}
⚠️ 폴백 계산 사용
{% endif %}

계산 방법: {{ debug_info.calculation_method }}
생성 시간: {{ debug_info.generated_at|format_date('%Y-%m-%d %H:%M:%S') }}
```

## 주의사항

1. **변수명 대소문자**: Python 변수명과 정확히 일치해야 합니다.
2. **None 값 처리**: 필터가 None 값을 안전하게 처리합니다.
3. **오류 처리**: 템플릿 렌더링 중 오류가 발생하면 로그에 상세 정보가 출력됩니다.
4. **성능**: 필터는 템플릿 렌더링 시에만 실행되므로 성능에 미치는 영향이 최소화됩니다.

## 템플릿 테스트

템플릿을 테스트하려면 다음 명령을 사용하세요:
```bash
python test_template.py
```

이 스크립트는 샘플 데이터로 템플릿을 렌더링하여 결과를 확인할 수 있습니다.
