#!/usr/bin/env python3
"""
Vercel 템플릿의 XML 구조를 분석하여 문제점을 찾습니다.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
from pathlib import Path

def analyze_vercel_template():
    """Vercel 템플릿의 XML 구조를 분석합니다."""
    
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    
    print("🔍 Vercel 템플릿 분석 시작...")
    
    # ZIP 파일로 열기
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        # word/document.xml 읽기
        with zip_ref.open('word/document.xml') as doc_file:
            content = doc_file.read().decode('utf-8')
    
    print(f"📄 문서 크기: {len(content)} bytes")
    
    # 문제가 있는 패턴들 찾기
    print("\n🔍 문제 패턴 분석...")
    
    # 1. 중복된 태그 찾기
    duplicate_patterns = [
        (r'\{\{\s*cli\s*\}\}.*\{\{\s*cli\s*\}\}', "중복된 client_name 태그"),
        (r'\{\{\s*ame\s*\}\}.*\{\{\s*ame\s*\}\}', "중복된 name 태그"),
        (r'\{\{\s*sta\s*\}\}.*\{\{\s*sta\s*\}\}', "중복된 standards 태그"),
        (r'\{\{\s*ext\s*\}\}.*\{\{\s*ext\s*\}\}', "중복된 text 태그"),
        (r'\{\{\s*quo\s*\}\}.*\{\{\s*quo\s*\}\}', "중복된 quotation 태그"),
        (r'\{\{\s*ate\s*\}\}.*\{\{\s*ate\s*\}\}', "중복된 date 태그"),
        (r'\{\{\s*ber\s*\}\}.*\{\{\s*ber\s*\}\}', "중복된 number 태그"),
        (r'\{\{\s*tot\s*\}\}.*\{\{\s*tot\s*\}\}', "중복된 total 태그"),
        (r'\{\{\s*iso\s*\}\}.*\{\{\s*iso\s*\}\}', "중복된 iso 태그"),
        (r'\{\{\s*ays\s*\}\}.*\{\{\s*ays\s*\}\}', "중복된 days 태그"),
        (r'\{\{\s*ncy\s*\}\}.*\{\{\s*ncy\s*\}\}', "중복된 currency 태그"),
        (r'\{\{\s*tra\s*\}\}.*\{\{\s*tra\s*\}\}', "중복된 travel 태그"),
        (r'\{\{\s*ess\s*\}\}.*\{\{\s*ess\s*\}\}', "중복된 address 태그"),
    ]
    
    duplicates_found = 0
    for pattern, description in duplicate_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            duplicates_found += len(matches)
            print(f"⚠️  {description}: {len(matches)}개 발견")
            for i, match in enumerate(matches[:3]):  # 처음 3개만 표시
                print(f"    {i+1}. {match[:100]}...")
    
    if duplicates_found == 0:
        print("✅ 중복 태그 없음")
    else:
        print(f"⚠️  총 {duplicates_found}개의 중복 태그 발견")
    
    # 2. 잘못된 문법 찾기
    print("\n🔍 잘못된 문법 분석...")
    
    syntax_errors = [
        (r'\{\{#\{\%', "Handlebars + Jinja2 혼재"),
        (r'\{\{/\{\%', "Handlebars + Jinja2 혼재"),
        (r'\{\{\s*#\s*', "Handlebars 문법"),
        (r'\{\{\s*/\s*', "Handlebars 문법"),
        (r'\{\%\s*if\s+[^%]*\{\{', "Jinja2 + Handlebars 혼재"),
        (r'\}\}\s*\%\}', "Handlebars + Jinja2 혼재"),
    ]
    
    syntax_errors_found = 0
    for pattern, description in syntax_errors:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            syntax_errors_found += len(matches)
            print(f"⚠️  {description}: {len(matches)}개 발견")
            for i, match in enumerate(matches[:3]):  # 처음 3개만 표시
                print(f"    {i+1}. {match}")
    
    if syntax_errors_found == 0:
        print("✅ 문법 오류 없음")
    else:
        print(f"⚠️  총 {syntax_errors_found}개의 문법 오류 발견")
    
    # 3. 분할된 변수명 찾기
    print("\n🔍 분할된 변수명 분석...")
    
    split_patterns = [
        (r'cli\s*ame', "client_name 분할"),
        (r'sta\s*ext', "standards_text 분할"),
        (r'quo\s*ate', "quotation_date 분할"),
        (r'tot\s*ber', "total_audit_days 분할"),
        (r'iso\s*ber', "iso9001_days 분할"),
        (r'iso\s*ays', "iso9001_days 분할"),
        (r'iso\s*ncy', "iso9001_cost_formatted 분할"),
        (r'tra\s*ncy', "travel_expense_formatted 분할"),
        (r'cli\s*ess', "client_address 분할"),
    ]
    
    split_found = 0
    for pattern, description in split_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            split_found += len(matches)
            print(f"⚠️  {description}: {len(matches)}개 발견")
            for i, match in enumerate(matches[:3]):  # 처음 3개만 표시
                print(f"    {i+1}. {match}")
    
    if split_found == 0:
        print("✅ 분할된 변수명 없음")
    else:
        print(f"⚠️  총 {split_found}개의 분할된 변수명 발견")
    
    # 4. 모든 변수 추출
    print("\n📊 변수 목록...")
    variables = re.findall(r'\{\{\s*([^}]+)\s*\}\}', content)
    unique_variables = set(variables)
    
    print(f"총 {len(unique_variables)}개의 고유 변수:")
    for var in sorted(unique_variables):
        count = variables.count(var)
        print(f"  - {var} (사용 {count}회)")
    
    # 5. XML 구조 검사
    print("\n🔍 XML 구조 검사...")
    try:
        # XML 파싱 시도
        root = ET.fromstring(content)
        print("✅ XML 구조 유효함")
        
        # 텍스트 노드에서 변수 찾기
        text_nodes = []
        for elem in root.iter():
            if elem.text and '{{' in elem.text:
                text_nodes.append(elem.text)
        
        print(f"📝 변수가 포함된 텍스트 노드: {len(text_nodes)}개")
        
    except ET.ParseError as e:
        print(f"❌ XML 파싱 오류: {e}")
    
    # 6. 요약
    print(f"\n📋 분석 요약:")
    print(f"  - 중복 태그: {duplicates_found}개")
    print(f"  - 문법 오류: {syntax_errors_found}개")
    print(f"  - 분할된 변수: {split_found}개")
    print(f"  - 총 변수: {len(unique_variables)}개")
    
    if duplicates_found > 0 or syntax_errors_found > 0 or split_found > 0:
        print("\n⚠️  템플릿에 문제가 있어 수정이 필요합니다.")
        return False
    else:
        print("\n✅ 템플릿이 정상입니다.")
        return True

if __name__ == "__main__":
    try:
        result = analyze_vercel_template()
        if not result:
            print("\n🔧 템플릿 수정이 필요합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
