#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
템플릿 완전 수정 스크립트
"""

import zipfile
import os
import re

def fix_template_completely(template_path, output_path=None):
    """템플릿을 완전히 수정"""
    
    if output_path is None:
        output_path = template_path.replace('.docx', '_completely_fixed.docx')
    
    print(f"🔧 템플릿 완전 수정: {template_path}")
    
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_read:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                
                for file_info in zip_read.infolist():
                    content = zip_read.read(file_info.filename)
                    
                    if file_info.filename == 'word/document.xml':
                        content_str = content.decode('utf-8')
                        print("🔍 템플릿 완전 수정 중...")
                        
                        # 1. Handlebars 문법을 Jinja2로 변환
                        # {{#has_iso9001}} → {% if has_iso9001 %}
                        content_str = re.sub(r'\{\{#has_iso9001\}\}', r'{% if has_iso9001 %}', content_str)
                        content_str = re.sub(r'\{\{#has_iso14001\}\}', r'{% if has_iso14001 %}', content_str)
                        content_str = re.sub(r'\{\{#has_iso45001\}\}', r'{% if has_iso45001 %}', content_str)
                        
                        # {{/has_iso9001}} → {% endif %}
                        content_str = re.sub(r'\{\{/has_iso9001\}\}', r'{% endif %}', content_str)
                        content_str = re.sub(r'\{\{/has_iso14001\}\}', r'{% endif %}', content_str)
                        content_str = re.sub(r'\{\{/has_iso45001\}\}', r'{% endif %}', content_str)
                        
                        # {{else}} → {% else %}
                        content_str = re.sub(r'\{\{else\}\}', r'{% else %}', content_str)
                        
                        # 2. 모든 {{ }} 문법 정리
                        # {{ 변수명 }} 형태로 정리
                        content_str = re.sub(r'\{\{\s*([^}]+)\s*\}\}', r'{{ \1 }}', content_str)
                        
                        # 3. 중복된 공백 제거
                        content_str = re.sub(r'\s+', ' ', content_str)
                        
                        # 4. Jinja2 태그 정리
                        content_str = re.sub(r'\{%\s+', r'{% ', content_str)
                        content_str = re.sub(r'\s+%\}', r' %}', content_str)
                        
                        content = content_str.encode('utf-8')
                        print("✅ 템플릿 완전 수정 완료")
                    
                    zip_write.writestr(file_info, content)
        
        print(f"🎉 완전 수정 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def create_simple_test_template():
    """간단한 테스트 템플릿 생성"""
    print("\n🧪 간단한 테스트 템플릿 생성")
    
    # 간단한 HTML 기반 템플릿 생성
    simple_template = """
<!DOCTYPE html>
<html>
<head>
    <title>LRQA 견적서</title>
</head>
<body>
    <h1>LRQA 서비스 제안서</h1>
    
    <h2>기본 정보</h2>
    <p>고객명: {{ client_name }}</p>
    <p>견적일: {{ quotation_date|format_date }}</p>
    <p>견적번호: {{ quotation_number }}</p>
    <p>주소: {{ client_address }}</p>
    
    <h2>ISO 표준</h2>
    <p>표준: {{ standards_text }}</p>
    <p>총 사이트: {{ total_sites|format_number }}개</p>
    <p>총 직원: {{ total_employees|format_number }}명</p>
    
    <h2>심사 일수</h2>
    <p>총 심사일수: {{ total_audit_days|format_number }}일</p>
    
    {% if has_iso9001 %}
    <p>ISO 9001: {{ iso9001_stage1_2_days|format_number }}일</p>
    {% endif %}
    
    {% if has_iso14001 %}
    <p>ISO 14001: {{ iso14001_stage1_2_days|format_number }}일</p>
    {% endif %}
    
    {% if has_iso45001 %}
    <p>ISO 45001: {{ iso45001_stage1_2_days|format_number }}일</p>
    {% endif %}
    
    <h2>비용</h2>
    <p>총 비용: {{ total_cost|format_currency }}</p>
    <p>여행비: {{ travel_expense|format_currency }}</p>
    <p>총 비용 (여행비 포함): {{ total_cost_with_travel|format_currency }}</p>
</body>
</html>
"""
    
    with open("simple_test_template.html", "w", encoding="utf-8") as f:
        f.write(simple_template)
    
    print("✅ 간단한 테스트 템플릿 생성: simple_test_template.html")

def test_simple_template():
    """간단한 템플릿 테스트"""
    print("\n🧪 간단한 템플릿 테스트")
    
    try:
        from jinja2 import Template
        
        with open("simple_test_template.html", "r", encoding="utf-8") as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # 테스트 컨텍스트
        context = {
            'client_name': '테스트 화학공장',
            'quotation_date': '2024-01-15',
            'quotation_number': 'Q2024-001',
            'standards_text': 'ISO 9001, ISO 14001, ISO 45001',
            'client_address': '서울시 강남구 테헤란로 123',
            'total_sites': 1,
            'total_employees': 150,
            'total_audit_days': 12.5,
            'total_cost': 15000000,
            'has_iso9001': True,
            'has_iso14001': True,
            'has_iso45001': False,
            'iso9001_stage1_2_days': 5.0,
            'iso14001_stage1_2_days': 4.0,
            'iso45001_stage1_2_days': 0,
            'travel_expense': 500000,
            'total_cost_with_travel': 15500000
        }
        
        # 필터 함수 정의
        def format_currency(value):
            if value is None:
                return "0원"
            try:
                return f"{float(value):,.0f}원"
            except:
                return f"{value}원"
        
        def format_number(value):
            if value is None:
                return "0"
            try:
                return f"{float(value):,.0f}"
            except:
                return str(value)
        
        def format_date(value):
            if value is None:
                return ""
            return str(value)
        
        # 템플릿 렌더링
        rendered = template.render(
            **context,
            format_currency=format_currency,
            format_number=format_number,
            format_date=format_date
        )
        
        # 결과 저장
        with open("test_simple_output.html", "w", encoding="utf-8") as f:
            f.write(rendered)
        
        print("✅ 간단한 템플릿 렌더링 성공")
        print("💾 결과 저장: test_simple_output.html")
        
        # 결과 미리보기
        print("\n📄 렌더링 결과 미리보기:")
        print("=" * 50)
        lines = rendered.split('\n')
        for line in lines[:20]:  # 처음 20줄만 표시
            print(line)
        if len(lines) > 20:
            print("...")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 간단한 템플릿 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 템플릿 완전 수정 및 테스트")
    print("=" * 60)
    
    # 1. 간단한 테스트 템플릿 생성 및 테스트
    create_simple_test_template()
    if test_simple_template():
        print("\n✅ Jinja2 필터 시스템이 정상 작동합니다!")
    
    # 2. Word 템플릿 수정
    template_path = "quotation-api/templates/LRQA_quotation.docx"
    if os.path.exists(template_path):
        if fix_template_completely(template_path):
            print(f"\n🎉 Word 템플릿 수정 완료!")
            print("이제 API 서버에서 올바른 템플릿을 사용할 수 있습니다.")

if __name__ == "__main__":
    main()
