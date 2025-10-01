#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 템플릿 태그들을 확인하는 도구
"""

import os
import zipfile
import re
from pathlib import Path

def check_actual_tags(template_path):
    """실제 템플릿 태그들을 확인합니다."""
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            document_xml = zip_file.read('word/document.xml')
            xml_content = document_xml.decode('utf-8')
            
            print(f"🔍 실제 템플릿 태그 확인: {template_path}")
            print("="*80)
            
            # 1. 모든 템플릿 태그 찾기
            template_pattern = r'\{\{[^}]+\}\}'
            template_tags = re.findall(template_pattern, xml_content)
            
            print(f"📊 발견된 템플릿 태그들 ({len(template_tags)}개):")
            print("-" * 50)
            for i, tag in enumerate(template_tags, 1):
                print(f"{i:2d}. {tag}")
            print()
            
            # 2. 조건부 태그 찾기
            if_pattern = r'\{%\s*if\s+[^%]+\s*%\}'
            endif_pattern = r'\{%\s*endif\s*%\}'
            
            if_tags = re.findall(if_pattern, xml_content)
            endif_tags = re.findall(endif_pattern, xml_content)
            
            print(f"📊 발견된 조건부 태그들:")
            print("-" * 50)
            print(f"{{% if %}} 태그 ({len(if_tags)}개):")
            for i, tag in enumerate(if_tags, 1):
                print(f"  {i}. {tag}")
            print()
            
            print(f"{{% endif %}} 태그 ({len(endif_tags)}개):")
            for i, tag in enumerate(endif_tags, 1):
                print(f"  {i}. {tag}")
            print()
            
            # 3. 분리된 태그 확인
            broken_pattern = r'\{\{</w:t></w:r><w:r[^>]*>.*?</w:t></w:r>.*?\}\}'
            broken_tags = re.findall(broken_pattern, xml_content, re.DOTALL)
            
            print(f"📊 분리된 태그들 ({len(broken_tags)}개):")
            print("-" * 50)
            for i, tag in enumerate(broken_tags, 1):
                print(f"{i:2d}. {tag[:100]}...")
            print()
            
            # 4. 정상적인 태그들만 필터링
            normal_tags = []
            for tag in template_tags:
                if not re.search(r'</w:t></w:r><w:r', tag):
                    normal_tags.append(tag)
            
            print(f"📊 정상적인 템플릿 태그들 ({len(normal_tags)}개):")
            print("-" * 50)
            for i, tag in enumerate(normal_tags, 1):
                print(f"{i:2d}. {tag}")
            print()
            
            # 5. 필수 변수 확인
            essential_vars = [
                'client_name', 'quotation_date', 'quotation_number', 
                'standards_text', 'total_employees', 'total_audit_days'
            ]
            
            found_vars = []
            missing_vars = []
            
            for var in essential_vars:
                found = False
                for tag in normal_tags:
                    if var in tag:
                        found = True
                        found_vars.append(tag)
                        break
                if not found:
                    missing_vars.append(var)
            
            print(f"📊 필수 변수 상태:")
            print("-" * 50)
            if found_vars:
                print("✅ 발견된 필수 변수들:")
                for tag in found_vars:
                    print(f"  - {tag}")
                print()
            
            if missing_vars:
                print("❌ 누락된 필수 변수들:")
                for var in missing_vars:
                    print(f"  - {{{{ {var} }}}}")
                print()
            
            # 6. 최종 상태 요약
            print(f"🎯 최종 상태 요약:")
            print("="*80)
            print(f"✅ 정상적인 템플릿 태그: {len(normal_tags)}개")
            print(f"❌ 분리된 태그: {len(broken_tags)}개")
            print(f"✅ {{% if %}} 태그: {len(if_tags)}개")
            print(f"❌ {{% endif %}} 태그: {len(endif_tags)}개")
            print(f"✅ 발견된 필수 변수: {len(found_vars)}개")
            print(f"❌ 누락된 필수 변수: {len(missing_vars)}개")
            
            if len(broken_tags) == 0 and len(endif_tags) == len(if_tags) and len(missing_vars) == 0:
                print(f"\n🎉 템플릿이 완벽합니다!")
                return True
            else:
                print(f"\n⚠️ 템플릿에 문제가 있습니다.")
                return False
                
    except Exception as e:
        print(f"❌ 템플릿 확인 오류: {e}")
        return False

def main():
    template_path = 'vercel-deploy/public/templates/LRQA_quotation.docx'
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    check_actual_tags(template_path)

if __name__ == "__main__":
    main()
