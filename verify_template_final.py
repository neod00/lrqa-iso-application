#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 템플릿 검증 도구 - Vercel 템플릿 파일 완전 분석
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def verify_template_completely(template_path):
    """템플릿 파일을 완전히 검증합니다."""
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            document_xml = zip_file.read('word/document.xml')
            xml_content = document_xml.decode('utf-8')
            
            print(f"🔍 템플릿 파일 완전 검증: {template_path}")
            print("="*80)
            
            # 1. 기본 통계
            template_pattern = r'\{\{[^}]+\}\}'
            conditional_pattern = r'\{%[^%]+\%\}'
            
            template_tags = re.findall(template_pattern, xml_content)
            conditional_tags = re.findall(conditional_pattern, xml_content)
            
            print(f"📊 기본 통계:")
            print(f"   - 템플릿 태그 개수: {len(template_tags)}")
            print(f"   - 조건부 태그 개수: {len(conditional_tags)}")
            
            # 2. 중복 태그 확인
            template_tag_counts = {}
            conditional_tag_counts = {}
            
            for tag in template_tags:
                template_tag_counts[tag] = template_tag_counts.get(tag, 0) + 1
            
            for tag in conditional_tags:
                conditional_tag_counts[tag] = conditional_tag_counts.get(tag, 0) + 1
            
            duplicate_template_tags = {tag: count for tag, count in template_tag_counts.items() if count > 1}
            duplicate_conditional_tags = {tag: count for tag, count in conditional_tag_counts.items() if count > 1}
            
            print(f"\n🔍 중복 태그 분석:")
            print(f"   - 중복 템플릿 태그: {len(duplicate_template_tags)}개")
            print(f"   - 중복 조건부 태그: {len(duplicate_conditional_tags)}개")
            
            if duplicate_template_tags:
                print("   ⚠️ 중복된 템플릿 태그:")
                for tag, count in duplicate_template_tags.items():
                    print(f"      - {tag} ({count}번)")
            
            if duplicate_conditional_tags:
                print("   ⚠️ 중복된 조건부 태그:")
                for tag, count in duplicate_conditional_tags.items():
                    print(f"      - {tag} ({count}번)")
            
            # 3. 조건부 태그 균형 확인
            if_tags = re.findall(r'\{%\s*if\s+[^%]+\s*%\}', xml_content)
            endif_tags = re.findall(r'\{%\s*endif\s*%\}', xml_content)
            
            print(f"\n🔍 조건부 태그 균형:")
            print(f"   - {{% if %}} 태그: {len(if_tags)}개")
            print(f"   - {{% endif %}} 태그: {len(endif_tags)}개")
            
            if len(if_tags) != len(endif_tags):
                print(f"   ⚠️ 조건부 태그 불균형: if {len(if_tags)}개, endif {len(endif_tags)}개")
            else:
                print(f"   ✅ 조건부 태그 균형 맞음")
            
            # 4. 잘못된 태그 구문 확인
            print(f"\n🔍 태그 구문 검증:")
            
            # 잘못된 조건부 태그 ({{ }} 안에 있는 경우)
            wrong_conditional = re.findall(r'\{%\s*if\s*\{\{[^}]+\}\}\s*%\}', xml_content)
            if wrong_conditional:
                print(f"   ❌ 잘못된 조건부 태그: {len(wrong_conditional)}개")
                for tag in wrong_conditional:
                    print(f"      - {tag}")
            else:
                print(f"   ✅ 조건부 태그 구문 정상")
            
            # 5. 분리된 태그 확인
            print(f"\n🔍 분리된 태그 확인:")
            broken_tags = []
            for tag in template_tags:
                if '</w:t>' in tag or '<w:r' in tag or 'xml:space' in tag:
                    broken_tags.append(tag)
            
            if broken_tags:
                print(f"   ❌ 분리된 태그: {len(broken_tags)}개")
                for tag in broken_tags[:5]:  # 최대 5개만 표시
                    print(f"      - {tag[:100]}...")
            else:
                print(f"   ✅ 분리된 태그 없음")
            
            # 6. 필수 변수 확인
            print(f"\n🔍 필수 변수 확인:")
            essential_vars = [
                'client_name', 'quotation_date', 'quotation_number', 
                'standards_text', 'total_employees', 'total_audit_days'
            ]
            
            missing_vars = []
            for var in essential_vars:
                if not any(var in tag for tag in template_tags):
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"   ❌ 누락된 필수 변수: {missing_vars}")
            else:
                print(f"   ✅ 모든 필수 변수 존재")
            
            # 7. 최종 평가
            print(f"\n🎯 최종 평가:")
            
            issues = []
            if duplicate_template_tags:
                issues.append(f"중복 템플릿 태그 {len(duplicate_template_tags)}개")
            if duplicate_conditional_tags:
                issues.append(f"중복 조건부 태그 {len(duplicate_conditional_tags)}개")
            if len(if_tags) != len(endif_tags):
                issues.append("조건부 태그 불균형")
            if wrong_conditional:
                issues.append(f"잘못된 조건부 태그 {len(wrong_conditional)}개")
            if broken_tags:
                issues.append(f"분리된 태그 {len(broken_tags)}개")
            if missing_vars:
                issues.append(f"누락된 필수 변수 {len(missing_vars)}개")
            
            if issues:
                print(f"   ❌ 발견된 문제: {', '.join(issues)}")
                return False
            else:
                print(f"   ✅ 템플릿 검증 통과!")
                return True
                
    except Exception as e:
        print(f"❌ 템플릿 검증 오류: {e}")
        return False

def main():
    # Vercel 템플릿 파일 검증
    template_path = 'vercel-deploy/public/templates/LRQA_quotation.docx'
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    success = verify_template_completely(template_path)
    
    if success:
        print(f"\n🎉 템플릿이 완벽하게 수정되었습니다!")
        print(f"   Vercel에서 이 템플릿을 사용하면 치환 기능이 정상 작동할 것입니다.")
    else:
        print(f"\n⚠️ 템플릿에 여전히 문제가 있습니다.")
        print(f"   추가 수정이 필요할 수 있습니다.")

if __name__ == "__main__":
    main()
