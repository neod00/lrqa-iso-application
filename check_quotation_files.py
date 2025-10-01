#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 견적서 파일 내용 확인 도구
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def extract_text_from_docx(docx_path):
    """Word 파일에서 텍스트 내용을 추출합니다."""
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_file:
            # word/document.xml 파일 읽기
            document_xml = zip_file.read('word/document.xml')
            
            # XML 파싱
            root = ET.fromstring(document_xml)
            
            # 모든 텍스트 추출
            text_content = []
            for elem in root.iter():
                if elem.text:
                    text_content.append(elem.text.strip())
            
            return '\n'.join(text_content)
    except Exception as e:
        return f"파일 읽기 오류: {e}"

def check_template_tags(docx_path):
    """템플릿 태그들을 확인합니다."""
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_file:
            document_xml = zip_file.read('word/document.xml')
            
            # 텍스트 내용을 문자열로 변환
            xml_text = document_xml.decode('utf-8')
            
            # 템플릿 태그들 찾기
            import re
            template_tags = re.findall(r'\{\{[^}]+\}\}', xml_text)
            conditional_tags = re.findall(r'\{%[^%]+\%\}', xml_text)
            
            return {
                'template_tags': template_tags,
                'conditional_tags': conditional_tags,
                'duplicate_template_tags': [tag for tag in template_tags if template_tags.count(tag) > 1],
                'duplicate_conditional_tags': [tag for tag in conditional_tags if conditional_tags.count(tag) > 1]
            }
    except Exception as e:
        return f"템플릿 태그 확인 오류: {e}"

def main():
    # .playwright-mcp 폴더에서 최근 생성된 견적서 파일들 확인
    playwright_dir = Path('.playwright-mcp')
    
    if not playwright_dir.exists():
        print("❌ .playwright-mcp 폴더를 찾을 수 없습니다.")
        return
    
    # 최근 생성된 견적서 파일들 찾기
    quotation_files = list(playwright_dir.glob('LRQA-견적서-*.docx'))
    quotation_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print("🔍 생성된 견적서 파일들:")
    for i, file_path in enumerate(quotation_files[:5], 1):  # 최근 5개만 확인
        print(f"{i}. {file_path.name}")
    
    print("\n" + "="*80)
    
    # 최근 2개 파일 상세 분석
    for i, file_path in enumerate(quotation_files[:2], 1):
        print(f"\n📄 파일 {i}: {file_path.name}")
        print("-" * 60)
        
        # 파일 크기 확인
        file_size = file_path.stat().st_size
        print(f"📊 파일 크기: {file_size:,} bytes")
        
        # 텍스트 내용 추출
        print("\n📝 텍스트 내용:")
        text_content = extract_text_from_docx(file_path)
        if len(text_content) > 500:
            print(text_content[:500] + "...")
        else:
            print(text_content)
        
        # 템플릿 태그 확인
        print("\n🏷️ 템플릿 태그 분석:")
        tag_analysis = check_template_tags(file_path)
        
        if isinstance(tag_analysis, str):
            print(f"❌ {tag_analysis}")
        else:
            print(f"📋 템플릿 태그 개수: {len(tag_analysis['template_tags'])}")
            print(f"📋 조건부 태그 개수: {len(tag_analysis['conditional_tags'])}")
            
            if tag_analysis['duplicate_template_tags']:
                print(f"⚠️ 중복된 템플릿 태그: {len(tag_analysis['duplicate_template_tags'])}개")
                for tag in set(tag_analysis['duplicate_template_tags']):
                    count = tag_analysis['duplicate_template_tags'].count(tag)
                    print(f"   - {tag} ({count}번 중복)")
            
            if tag_analysis['duplicate_conditional_tags']:
                print(f"⚠️ 중복된 조건부 태그: {len(tag_analysis['duplicate_conditional_tags'])}개")
                for tag in set(tag_analysis['duplicate_conditional_tags']):
                    count = tag_analysis['duplicate_conditional_tags'].count(tag)
                    print(f"   - {tag} ({count}번 중복)")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    main()
