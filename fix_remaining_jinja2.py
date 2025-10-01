#!/usr/bin/env python3
"""
남은 jinja2 문법을 완전히 제거
- {% else %} → {else}
- 기타 남은 jinja2 문법 정리
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

def fix_remaining_jinja2():
    """남은 jinja2 문법을 완전히 제거합니다."""
    
    # 파일 경로
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    backup_path = "vercel-deploy/public/templates/LRQA_quotation_backup2.docx"
    fixed_path = "vercel-deploy/public/templates/LRQA_quotation_final.docx"
    
    print("🔧 남은 jinja2 문법 완전 제거...")
    
    # 백업 생성
    shutil.copy2(template_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # ZIP 파일로 열기
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        # word/document.xml 읽기
        with zip_ref.open('word/document.xml') as doc_file:
            content = doc_file.read().decode('utf-8')
    
    print(f"📄 원본 문서 크기: {len(content)} bytes")
    
    # 남은 jinja2 문법 제거
    fixes = [
        # 1. {% else %} → {else}
        (r'\{\%\s*else\s*\%\}', '{else}'),
        
        # 2. 기타 남은 jinja2 문법 제거
        (r'\{\%[^%]*\%\}', ''),
        
        # 3. 잘못된 변수명 정리
        (r'% else %', 'else'),
        (r'/if', 'if'),
        
        # 4. XML 태그 내의 잘못된 문법 정리
        (r'\{#if has_iso9001\s*\}', '{#if has_iso9001}'),
        (r'\{/\{if has_iso9001\s*\}', '{/if}'),
        
        # 5. 공백 정리
        (r'\s+', ' '),
        (r'\s*\{\s*', '{'),
        (r'\}\s*', '}'),
    ]
    
    # 수정 적용
    original_content = content
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    print(f"📝 수정된 문서 크기: {len(content)} bytes")
    
    # 수정된 내용을 새 ZIP 파일로 저장
    with zipfile.ZipFile(template_path, 'r') as source_zip:
        with zipfile.ZipFile(fixed_path, 'w', zipfile.ZIP_DEFLATED) as target_zip:
            for item in source_zip.infolist():
                if item.filename == 'word/document.xml':
                    # 수정된 document.xml 사용
                    target_zip.writestr(item, content)
                else:
                    # 다른 파일들은 그대로 복사
                    target_zip.writestr(item, source_zip.read(item.filename))
    
    print(f"✅ 수정된 템플릿 저장: {fixed_path}")
    
    # 수정된 템플릿을 원본 위치에 복사
    shutil.copy2(fixed_path, template_path)
    print(f"✅ Vercel 템플릿 업데이트 완료: {template_path}")
    
    # 검증
    print("\n🔍 최종 검증...")
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        with zip_ref.open('word/document.xml') as doc_file:
            fixed_content = doc_file.read().decode('utf-8')
    
    # jinja2 문법 검사
    jinja2_patterns = [
        r'\{\{[^}]+\}\}',
        r'\{\%[^%]+\%\}',
    ]
    
    jinja2_remaining = 0
    for pattern in jinja2_patterns:
        matches = re.findall(pattern, fixed_content)
        if matches:
            jinja2_remaining += len(matches)
            print(f"⚠️  jinja2 문법 남아있음: {pattern} - {len(matches)}개")
            for match in matches[:3]:  # 처음 3개만 표시
                print(f"    - {match}")
    
    if jinja2_remaining == 0:
        print("✅ jinja2 문법 완전 제거됨")
    else:
        print(f"⚠️  {jinja2_remaining}개의 jinja2 문법이 남아있음")
    
    # docxtemplater 문법 검사
    docxtemplater_variables = re.findall(r'\{([^}]+)\}', fixed_content)
    unique_variables = set(docxtemplater_variables)
    
    # 유효한 변수만 필터링 (UUID나 XML 태그 제외)
    valid_variables = []
    for var in unique_variables:
        if not re.match(r'^[A-F0-9-]{36}$', var) and not '<' in var and not '>' in var:
            valid_variables.append(var)
    
    print(f"📊 docxtemplater 변수: {len(valid_variables)}개")
    print(f"\n📋 유효한 변수 목록:")
    for var in sorted(valid_variables):
        count = docxtemplater_variables.count(var)
        print(f"  - {var} (사용 {count}회)")
    
    return fixed_path

if __name__ == "__main__":
    try:
        result = fix_remaining_jinja2()
        print(f"\n🎉 jinja2 문법 완전 제거 완료: {result}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

