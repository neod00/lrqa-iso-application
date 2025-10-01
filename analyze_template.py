#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 템플릿 파일 분석 도구 - 중복 태그 문제 해결
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re

def analyze_template_tags(template_path):
    """템플릿 파일의 태그들을 분석하고 중복 문제를 찾습니다."""
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            # word/document.xml 파일 읽기
            document_xml = zip_file.read('word/document.xml')
            
            # XML을 문자열로 변환
            xml_content = document_xml.decode('utf-8')
            
            # 템플릿 태그들 찾기
            template_pattern = r'\{\{[^}]+\}\}'
            conditional_pattern = r'\{%[^%]+\%\}'
            
            template_tags = re.findall(template_pattern, xml_content)
            conditional_tags = re.findall(conditional_pattern, xml_content)
            
            # 중복 태그 찾기
            template_tag_counts = {}
            conditional_tag_counts = {}
            
            for tag in template_tags:
                template_tag_counts[tag] = template_tag_counts.get(tag, 0) + 1
            
            for tag in conditional_tags:
                conditional_tag_counts[tag] = conditional_tag_counts.get(tag, 0) + 1
            
            # 중복된 태그들
            duplicate_template_tags = {tag: count for tag, count in template_tag_counts.items() if count > 1}
            duplicate_conditional_tags = {tag: count for tag, count in conditional_tag_counts.items() if count > 1}
            
            return {
                'template_tags': template_tags,
                'conditional_tags': conditional_tags,
                'duplicate_template_tags': duplicate_template_tags,
                'duplicate_conditional_tags': duplicate_conditional_tags,
                'xml_content': xml_content
            }
    except Exception as e:
        return f"템플릿 분석 오류: {e}"

def find_problematic_sections(xml_content):
    """문제가 있는 섹션들을 찾습니다."""
    # 중복 태그가 있는 라인들 찾기
    lines = xml_content.split('\n')
    problematic_lines = []
    
    for i, line in enumerate(lines, 1):
        # 중복된 {{ 태그가 있는 라인 찾기
        if line.count('{{') > 1:
            problematic_lines.append({
                'line_number': i,
                'content': line.strip(),
                'issue': 'Multiple {{ tags in one line'
            })
        
        # 중복된 }} 태그가 있는 라인 찾기
        if line.count('}}') > 1:
            problematic_lines.append({
                'line_number': i,
                'content': line.strip(),
                'issue': 'Multiple }} tags in one line'
            })
        
        # {% if %} 태그가 닫히지 않은 경우
        if '{% if' in line and '{% endif' not in line:
            # 다음 몇 라인을 확인
            next_lines = lines[i:i+10]
            if not any('{% endif' in next_line for next_line in next_lines):
                problematic_lines.append({
                    'line_number': i,
                    'content': line.strip(),
                    'issue': 'Unclosed {% if %} tag'
                })
    
    return problematic_lines

def main():
    # Vercel에서 사용하는 템플릿 파일 분석
    template_path = Path('vercel-deploy/public/templates/LRQA_quotation.docx')
    
    if not template_path.exists():
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    print(f"🔍 템플릿 파일 분석: {template_path}")
    print("="*80)
    
    # 템플릿 분석
    analysis = analyze_template_tags(template_path)
    
    if isinstance(analysis, str):
        print(f"❌ {analysis}")
        return
    
    print(f"📊 템플릿 태그 총 개수: {len(analysis['template_tags'])}")
    print(f"📊 조건부 태그 총 개수: {len(analysis['conditional_tags'])}")
    
    # 중복 태그 출력
    if analysis['duplicate_template_tags']:
        print(f"\n⚠️ 중복된 템플릿 태그 ({len(analysis['duplicate_template_tags'])}개):")
        for tag, count in analysis['duplicate_template_tags'].items():
            print(f"   - {tag} ({count}번 중복)")
    
    if analysis['duplicate_conditional_tags']:
        print(f"\n⚠️ 중복된 조건부 태그 ({len(analysis['duplicate_conditional_tags'])}개):")
        for tag, count in analysis['duplicate_conditional_tags'].items():
            print(f"   - {tag} ({count}번 중복)")
    
    # 문제가 있는 섹션들 찾기
    print(f"\n🔍 문제가 있는 섹션들:")
    problematic_sections = find_problematic_sections(analysis['xml_content'])
    
    if problematic_sections:
        for section in problematic_sections[:10]:  # 최대 10개만 표시
            print(f"   라인 {section['line_number']}: {section['issue']}")
            print(f"   내용: {section['content'][:100]}...")
            print()
    else:
        print("   문제가 있는 섹션을 찾을 수 없습니다.")
    
    # 고유한 템플릿 태그들 출력
    print(f"\n📋 사용된 템플릿 태그들:")
    unique_template_tags = list(set(analysis['template_tags']))
    for tag in sorted(unique_template_tags):
        print(f"   - {tag}")
    
    # 고유한 조건부 태그들 출력
    print(f"\n📋 사용된 조건부 태그들:")
    unique_conditional_tags = list(set(analysis['conditional_tags']))
    for tag in sorted(unique_conditional_tags):
        print(f"   - {tag}")

if __name__ == "__main__":
    main()
