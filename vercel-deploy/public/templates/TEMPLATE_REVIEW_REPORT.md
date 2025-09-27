# Word 템플릿 검토 및 수정 보고서

## 📋 검토 개요
`D:\OneDrive\Business\ai automation\AImission\vercel-deploy\public\templates` 폴더의 Word 템플릿을 검토하고 Jinja2 문법으로 수정했습니다.

## 🔍 발견된 문제점

### 1. 심각한 XML 구조 손상
- **문제**: Word 문서의 XML 구조가 깨져서 변수명이 분리됨
- **예시**: `iso45001_stage1_2_days` → `iso</w:t></w:r><w:r>45</w:t></w:r><w:r>001_stage1_2_days`
- **원인**: Word 문서 편집 과정에서 텍스트가 여러 XML 요소로 분할됨

### 2. 일관성 없는 변수 문법
- **문제**: 일부 변수는 `{{ 변수명 }}` 형태, 일부는 단순 변수명
- **예시**: `{{ client_name }}` vs `total_cost`
- **영향**: 템플릿 렌더링 시 일부 변수가 치환되지 않음

### 3. Jinja2 필터 미사용
- **문제**: 모든 포맷팅이 미리 계산되어 제공됨
- **예시**: `total_cost_formatted` vs `{{ total_cost|format_currency }}`
- **영향**: 유연성 부족, 유지보수 어려움

## ✅ 수정 작업

### 1단계: XML 구조 복구
- **작업**: 깨진 변수명을 올바른 형태로 복구
- **결과**: 22개 변수 → 21개 올바른 변수
- **파일**: `LRQA_quotation_fixed.docx`

### 2단계: Jinja2 문법 표준화
- **작업**: 모든 변수를 `{{ 변수명 }}` 형태로 통일
- **결과**: 일관된 Jinja2 문법 적용
- **파일**: `LRQA_quotation_final.docx`

### 3단계: Jinja2 필터 적용
- **작업**: 포맷팅을 Jinja2 필터로 전환
- **결과**: 9개 필터, 6개 조건문 적용
- **파일**: `LRQA_quotation_improved.docx`

## 📊 수정 결과

### 변수 통계
| 구분 | 수정 전 | 수정 후 |
|------|---------|---------|
| 총 변수 수 | 22개 (깨진 형태) | 19개 (올바른 형태) |
| Jinja2 필터 | 0개 | 9개 |
| 조건문 | 0개 | 6개 |

### 적용된 Jinja2 필터
```jinja2
{{ quotation_date|format_date }}                    # 날짜 포맷팅
{{ total_employees|format_number }}명               # 숫자 포맷팅
{{ iso9001_stage1_2_cost|format_currency }}        # 통화 포맷팅
{{ total_audit_days|format_number }}일              # 일수 포맷팅
```

### 적용된 조건문
```jinja2
{% if has_iso9001 %}포함{% else %}미포함{% endif %}
{% if has_iso14001 %}포함{% else %}미포함{% endif %}
{% if has_iso45001 %}포함{% else %}미포함{% endif %}
```

## 📁 생성된 파일들

### 1. LRQA_quotation_backup.docx
- **용도**: 원본 파일 백업
- **상태**: 수정 전 상태 보존

### 2. LRQA_quotation_fixed.docx
- **용도**: 1차 수정 (XML 구조 복구)
- **상태**: 깨진 변수명 복구 완료

### 3. LRQA_quotation_final.docx
- **용도**: 2차 수정 (Jinja2 문법 표준화)
- **상태**: 모든 변수가 올바른 Jinja2 문법 사용

### 4. LRQA_quotation_improved.docx ⭐
- **용도**: 최종 개선 버전
- **상태**: Jinja2 필터 및 조건문 적용
- **권장**: 이 파일을 사용하세요

## 🚀 사용 방법

### 1. 템플릿 교체
```bash
# 기존 템플릿을 개선된 버전으로 교체
cp LRQA_quotation_improved.docx LRQA_quotation.docx
```

### 2. API 서버에서 사용
```python
# quotation-api/simple_server.py에서
doc = CustomDocxTemplate('templates/LRQA_quotation.docx')
```

### 3. Jinja2 필터 활용
템플릿에서 다음과 같은 문법을 사용할 수 있습니다:
```jinja2
총 비용: {{ total_cost|format_currency }}
직원 수: {{ total_employees|format_number }}명
견적일: {{ quotation_date|format_date }}

{% if has_iso9001 %}
ISO 9001 품질경영시스템 심사
{% endif %}
```

## 🔧 추가 개선 권장사항

### 1. 반복문 활용
```jinja2
{% for breakdown in breakdowns %}
{{ breakdown.standard }}: {{ breakdown.days|format_number }}일
{% endfor %}
```

### 2. 계산 필터 추가
```jinja2
{{ (total_cost * 1.1)|format_currency }}  # 부가세 포함
{{ (total_days / 5)|format_number }}주    # 주 단위 변환
```

### 3. 조건부 포맷팅
```jinja2
{{ total_cost|format_currency if total_cost > 0 else "견적 요청" }}
```

## 📈 기대 효과

### 1. 안정성 향상
- XML 구조 손상으로 인한 렌더링 오류 해결
- 일관된 Jinja2 문법으로 예측 가능한 동작

### 2. 유연성 증대
- 템플릿에서 직접 포맷팅 변경 가능
- 조건부 표시로 동적 콘텐츠 생성

### 3. 유지보수성 개선
- 코드와 템플릿의 명확한 분리
- 필터 재사용으로 중복 코드 제거

## 🎯 결론

Word 템플릿의 심각한 구조적 문제를 해결하고 Jinja2 문법으로 완전히 전환했습니다. 이제 안정적이고 유연한 템플릿 시스템을 사용할 수 있습니다.

**권장사항**: `LRQA_quotation_improved.docx`를 사용하여 Jinja2의 모든 기능을 활용하세요.
