#!/usr/bin/env python3
"""
jinja2 템플릿을 docxtemplater 형식으로 변환
- {{ variable }} → {variable}
- {% if condition %} → {#if condition}
- {% endif %} → {/if}
- 필터 제거 (docxtemplater는 필터를 지원하지 않음)
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

def convert_template_to_js():
    """jinja2 템플릿을 docxtemplater 형식으로 변환합니다."""
    
    # 파일 경로
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    backup_path = "vercel-deploy/public/templates/LRQA_quotation_backup.docx"
    converted_path = "vercel-deploy/public/templates/LRQA_quotation_js.docx"
    
    print("🔄 jinja2 템플릿을 docxtemplater 형식으로 변환...")
    
    # 백업 생성
    shutil.copy2(template_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # ZIP 파일로 열기
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        # word/document.xml 읽기
        with zip_ref.open('word/document.xml') as doc_file:
            content = doc_file.read().decode('utf-8')
    
    print(f"📄 원본 문서 크기: {len(content)} bytes")
    
    # jinja2 → docxtemplater 변환
    conversions = [
        # 1. 변수 문법 변환: {{ variable }} → {variable}
        (r'\{\{\s*([^}]+)\s*\}\}', r'{\1}'),
        
        # 2. 조건문 변환: {% if condition %} → {#if condition}
        (r'\{\%\s*if\s+([^%]+)\s*\%\}', r'{#if \1}'),
        (r'\{\%\s*endif\s*\%\}', r'{/if}'),
        
        # 3. 반복문 변환: {% for item in list %} → {#each list}
        (r'\{\%\s*for\s+([^%]+)\s*in\s+([^%]+)\s*\%\}', r'{#each \2}'),
        (r'\{\%\s*endfor\s*\%\}', r'{/each}'),
        
        # 4. 필터 제거 (docxtemplater는 필터를 지원하지 않음)
        (r'\|format_currency', ''),
        (r'\|format_number', ''),
        (r'\|format_date', ''),
        (r'\|format_boolean', ''),
        (r'\|safe_divide', ''),
        (r'\|int', ''),
        (r'\|string', ''),
        
        # 5. 공백 정리
        (r'\s+', ' '),
        (r'\s*\{\s*', '{'),
        (r'\}\s*', '}'),
    ]
    
    # 변환 적용
    original_content = content
    for pattern, replacement in conversions:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    print(f"📝 변환된 문서 크기: {len(content)} bytes")
    
    # 변환된 내용을 새 ZIP 파일로 저장
    with zipfile.ZipFile(template_path, 'r') as source_zip:
        with zipfile.ZipFile(converted_path, 'w', zipfile.ZIP_DEFLATED) as target_zip:
            for item in source_zip.infolist():
                if item.filename == 'word/document.xml':
                    # 변환된 document.xml 사용
                    target_zip.writestr(item, content)
                else:
                    # 다른 파일들은 그대로 복사
                    target_zip.writestr(item, source_zip.read(item.filename))
    
    print(f"✅ 변환된 템플릿 저장: {converted_path}")
    
    # 변환된 템플릿을 원본 위치에 복사
    shutil.copy2(converted_path, template_path)
    print(f"✅ Vercel 템플릿 업데이트 완료: {template_path}")
    
    # 검증
    print("\n🔍 변환 결과 검증...")
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        with zip_ref.open('word/document.xml') as doc_file:
            converted_content = doc_file.read().decode('utf-8')
    
    # jinja2 문법 검사
    jinja2_patterns = [
        r'\{\{[^}]+\}\}',
        r'\{\%[^%]+\%\}',
    ]
    
    jinja2_remaining = 0
    for pattern in jinja2_patterns:
        matches = re.findall(pattern, converted_content)
        if matches:
            jinja2_remaining += len(matches)
            print(f"⚠️  jinja2 문법 남아있음: {pattern} - {len(matches)}개")
            for match in matches[:3]:  # 처음 3개만 표시
                print(f"    - {match}")
    
    if jinja2_remaining == 0:
        print("✅ jinja2 문법 모두 변환됨")
    else:
        print(f"⚠️  {jinja2_remaining}개의 jinja2 문법이 남아있음")
    
    # docxtemplater 문법 검사
    docxtemplater_patterns = [
        r'\{[^}]+\}',
        r'\{#[^}]+\}',
        r'\{/[^}]+\}',
    ]
    
    docxtemplater_count = 0
    for pattern in docxtemplater_patterns:
        matches = re.findall(pattern, converted_content)
        docxtemplater_count += len(matches)
    
    print(f"📊 docxtemplater 문법: {docxtemplater_count}개")
    
    # 변수 목록 출력
    variables = re.findall(r'\{([^}]+)\}', converted_content)
    unique_variables = set(variables)
    print(f"\n📋 사용된 변수 목록 ({len(unique_variables)}개):")
    for var in sorted(unique_variables):
        count = variables.count(var)
        print(f"  - {var} (사용 {count}회)")
    
    return converted_path

if __name__ == "__main__":
    try:
        result = convert_template_to_js()
        print(f"\n🎉 템플릿 변환 완료: {result}")
        print("\n📝 다음 단계:")
        print("1. Git에 변경사항 커밋")
        print("2. Vercel에 배포")
        print("3. JavaScript 템플릿으로 견적서 생성 테스트")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

