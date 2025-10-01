#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 템플릿의 XML 구조 상태를 확인하는 도구
"""

import os
import zipfile
import re
from pathlib import Path

def check_xml_structure(template_path):
    """Word 템플릿의 XML 구조를 확인합니다."""
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            document_xml = zip_file.read('word/document.xml')
            xml_content = document_xml.decode('utf-8')
            
            print(f"🔍 XML 구조 확인: {template_path}")
            print("="*80)
            
            # 1. 기본 XML 구조 확인
            print("📊 기본 XML 구조:")
            print("-" * 50)
            
            # XML 태그 개수
            xml_tags = re.findall(r'<[^>]+>', xml_content)
            print(f"   - XML 태그 총 개수: {len(xml_tags)}")
            
            # 텍스트 노드 개수
            text_nodes = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', xml_content)
            print(f"   - 텍스트 노드 개수: {len(text_nodes)}")
            
            # 2. 템플릿 태그 분석
            print("\n📊 템플릿 태그 분석:")
            print("-" * 50)
            
            # 모든 {{ }} 태그 찾기
            template_pattern = r'\{\{[^}]+\}\}'
            template_tags = re.findall(template_pattern, xml_content)
            print(f"   - 템플릿 태그 총 개수: {len(template_tags)}")
            
            # 중복된 템플릿 태그 찾기
            template_counts = {}
            for tag in template_tags:
                # 태그에서 변수명만 추출
                var_name = re.search(r'\{\{\s*([^}]+)\s*\}\}', tag)
                if var_name:
                    var = var_name.group(1).strip()
                    template_counts[var] = template_counts.get(var, 0) + 1
            
            duplicates = {var: count for var, count in template_counts.items() if count > 1}
            print(f"   - 중복된 변수: {len(duplicates)}개")
            
            if duplicates:
                print("   ⚠️ 중복된 변수들:")
                for var, count in duplicates.items():
                    print(f"      - {var}: {count}번")
            
            # 3. 분리된 태그 확인
            print("\n📊 분리된 태그 확인:")
            print("-" * 50)
            
            # XML 구조 내에서 분리된 태그 찾기
            broken_pattern = r'\{\{</w:t></w:r><w:r[^>]*>.*?</w:t></w:r>.*?\}\}'
            broken_tags = re.findall(broken_pattern, xml_content, re.DOTALL)
            print(f"   - 분리된 태그 개수: {len(broken_tags)}")
            
            if broken_tags:
                print("   ⚠️ 분리된 태그들:")
                for i, tag in enumerate(broken_tags[:5], 1):  # 최대 5개만 표시
                    print(f"      {i}. {tag[:100]}...")
            
            # 4. 조건부 태그 확인
            print("\n📊 조건부 태그 확인:")
            print("-" * 50)
            
            if_pattern = r'\{%\s*if\s+[^%]+\s*%\}'
            endif_pattern = r'\{%\s*endif\s*%\}'
            
            if_tags = re.findall(if_pattern, xml_content)
            endif_tags = re.findall(endif_pattern, xml_content)
            
            print(f"   - {{% if %}} 태그: {len(if_tags)}개")
            print(f"   - {{% endif %}} 태그: {len(endif_tags)}개")
            
            if len(if_tags) != len(endif_tags):
                print(f"   ⚠️ 조건부 태그 불균형: if {len(if_tags)}개, endif {len(endif_tags)}개")
            else:
                print(f"   ✅ 조건부 태그 균형 맞음")
            
            # 5. XML 구조 무결성 확인
            print("\n📊 XML 구조 무결성:")
            print("-" * 50)
            
            # 열린 태그와 닫힌 태그 개수 비교
            open_tags = re.findall(r'<w:[^/][^>]*>', xml_content)
            close_tags = re.findall(r'</w:[^>]*>', xml_content)
            
            print(f"   - 열린 태그: {len(open_tags)}개")
            print(f"   - 닫힌 태그: {len(close_tags)}개")
            
            if len(open_tags) != len(close_tags):
                print(f"   ❌ XML 태그 불균형: 열린 {len(open_tags)}개, 닫힌 {len(close_tags)}개")
            else:
                print(f"   ✅ XML 태그 균형 맞음")
            
            # 6. 문제점 요약
            print("\n🎯 문제점 요약:")
            print("="*80)
            
            issues = []
            if len(duplicates) > 0:
                issues.append(f"중복된 변수 {len(duplicates)}개")
            if len(broken_tags) > 0:
                issues.append(f"분리된 태그 {len(broken_tags)}개")
            if len(if_tags) != len(endif_tags):
                issues.append("조건부 태그 불균형")
            if len(open_tags) != len(close_tags):
                issues.append("XML 태그 불균형")
            
            if issues:
                print("❌ 발견된 문제들:")
                for issue in issues:
                    print(f"   - {issue}")
                print(f"\n💡 해결 방안:")
                print(f"   1. 중복된 변수 제거")
                print(f"   2. 분리된 태그 수정")
                print(f"   3. 조건부 태그 균형 맞추기")
                print(f"   4. 완전히 새로운 템플릿 생성 권장")
                return False
            else:
                print("✅ XML 구조가 정상입니다!")
                return True
                
    except Exception as e:
        print(f"❌ XML 구조 확인 오류: {e}")
        return False

def main():
    # 현재 폴더의 모든 .docx 파일 찾기
    current_dir = "."
    docx_files = []
    
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.docx') and 'LRQA_quotation' in file:
                docx_files.append(os.path.join(root, file))
    
    if not docx_files:
        print("❌ LRQA_quotation.docx 파일을 찾을 수 없습니다.")
        return
    
    print(f"📁 발견된 템플릿 파일들: {len(docx_files)}개")
    print("="*80)
    
    for i, file_path in enumerate(docx_files, 1):
        print(f"\n[{i}/{len(docx_files)}] {file_path}")
        print("-" * 60)
        check_xml_structure(file_path)
        print()

if __name__ == "__main__":
    main()
