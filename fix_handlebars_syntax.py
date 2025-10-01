#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Handlebars 문법을 Jinja2 문법으로 변환하는 스크립트
"""

import zipfile
import os
import re

def fix_handlebars_to_jinja2(template_path, output_path=None):
    """Handlebars 문법을 Jinja2 문법으로 변환"""
    
    if output_path is None:
        output_path = template_path.replace('.docx', '_jinja2_fixed.docx')
    
    print(f"🔧 Handlebars → Jinja2 변환: {template_path}")
    
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_read:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                
                for file_info in zip_read.infolist():
                    content = zip_read.read(file_info.filename)
                    
                    if file_info.filename == 'word/document.xml':
                        content_str = content.decode('utf-8')
                        print("🔍 Handlebars 문법 변환 중...")
                        
                        # Handlebars 조건문을 Jinja2로 변환
                        # {{#has_iso9001}}...{{/has_iso9001}} → {% if has_iso9001 %}...{% endif %}
                        handlebars_patterns = [
                            (r'\{\{#has_iso9001\}\}', r'{% if has_iso9001 %}'),
                            (r'\{\{#has_iso14001\}\}', r'{% if has_iso14001 %}'),
                            (r'\{\{#has_iso45001\}\}', r'{% if has_iso45001 %}'),
                            (r'\{\{/has_iso9001\}\}', r'{% endif %}'),
                            (r'\{\{/has_iso14001\}\}', r'{% endif %}'),
                            (r'\{\{/has_iso45001\}\}', r'{% endif %}'),
                        ]
                        
                        for pattern, replacement in handlebars_patterns:
                            content_str = re.sub(pattern, replacement, content_str)
                        
                        # 기타 Handlebars 문법 정리
                        # {{else}} → {% else %}
                        content_str = re.sub(r'\{\{else\}\}', r'{% else %}', content_str)
                        
                        # 중복된 공백 정리
                        content_str = re.sub(r'\{\{\s+', r'{{ ', content_str)
                        content_str = re.sub(r'\s+\}\}', r' }}', content_str)
                        
                        content = content_str.encode('utf-8')
                        print("✅ Handlebars → Jinja2 변환 완료")
                    
                    zip_write.writestr(file_info, content)
        
        print(f"🎉 변환 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_converted_template(template_path):
    """변환된 템플릿 테스트"""
    print(f"\n🧪 변환된 템플릿 테스트: {template_path}")
    
    try:
        from docxtpl import DocxTemplate
        
        doc = DocxTemplate(template_path)
        print("✅ 템플릿 로드 성공")
        
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
            'iso9001_stage1_2_cost': 6000000,
            'iso14001_stage1_2_cost': 4800000,
            'iso45001_stage1_2_cost': 0,
            'travel_expense': 500000,
            'total_cost_with_travel': 15500000
        }
        
        print(f"📊 컨텍스트: {len(context)}개 변수")
        
        # 렌더링 시도
        doc.render(context)
        print("✅ 템플릿 렌더링 성공")
        
        # 결과 저장
        output_path = "test_converted_output.docx"
        doc.save(output_path)
        print(f"💾 결과 저장: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 렌더링 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    template_path = "quotation-api/templates/LRQA_quotation.docx"
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    # Handlebars → Jinja2 변환
    if fix_handlebars_to_jinja2(template_path):
        # 변환된 템플릿 테스트
        converted_path = template_path.replace('.docx', '_jinja2_fixed.docx')
        if test_converted_template(converted_path):
            # 성공하면 원본 파일 교체
            import shutil
            shutil.copy2(converted_path, template_path)
            print(f"\n🎉 원본 템플릿 교체 완료: {template_path}")
            print("이제 API 서버에서 올바른 템플릿을 사용할 수 있습니다!")

if __name__ == "__main__":
    main()
