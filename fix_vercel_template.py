#!/usr/bin/env python3
"""
Vercel 배포용 템플릿 수정 스크립트
- 중복 태그 제거
- 잘못된 문법 수정
- XML 구조 복구
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

def fix_vercel_template():
    """Vercel 배포용 템플릿을 수정합니다."""
    
    # 파일 경로
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    backup_path = "vercel-deploy/public/templates/LRQA_quotation_backup.docx"
    fixed_path = "vercel-deploy/public/templates/LRQA_quotation_fixed.docx"
    
    print("🔧 Vercel 템플릿 수정 시작...")
    
    # 백업 생성
    shutil.copy2(template_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # ZIP 파일로 열기
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        # word/document.xml 읽기
        with zip_ref.open('word/document.xml') as doc_file:
            content = doc_file.read().decode('utf-8')
    
    print(f"📄 원본 문서 크기: {len(content)} bytes")
    
    # 문제 패턴들 수정
    fixes = [
        # 1. 중복된 {{ }} 태그 제거
        (r'\{\{\s*cli\s*\}\}\s*\{\{\s*cli\s*\}\}', '{{ client_name }}'),
        (r'\{\{\s*ame\s*\}\}\s*\{\{\s*ame\s*\}\}', '{{ client_name }}'),
        (r'\{\{\s*sta\s*\}\}\s*\{\{\s*sta\s*\}\}', '{{ standards_text }}'),
        (r'\{\{\s*ext\s*\}\}\s*\{\{\s*ext\s*\}\}', '{{ standards_text }}'),
        (r'\{\{\s*quo\s*\}\}\s*\{\{\s*quo\s*\}\}', '{{ quotation_date }}'),
        (r'\{\{\s*ate\s*\}\}\s*\{\{\s*ate\s*\}\}', '{{ quotation_date }}'),
        (r'\{\{\s*ber\s*\}\}\s*\{\{\s*ber\s*\}\}', '{{ total_audit_days }}'),
        (r'\{\{\s*tot\s*\}\}\s*\{\{\s*tot\s*\}\}', '{{ total_cost_with_travel_formatted }}'),
        (r'\{\{\s*iso\s*\}\}\s*\{\{\s*iso\s*\}\}', '{{ iso9001_days }}'),
        (r'\{\{\s*ays\s*\}\}\s*\{\{\s*ays\s*\}\}', '{{ iso9001_days }}'),
        (r'\{\{\s*ncy\s*\}\}\s*\{\{\s*ncy\s*\}\}', '{{ iso9001_cost_formatted }}'),
        (r'\{\{\s*tra\s*\}\}\s*\{\{\s*tra\s*\}\}', '{{ travel_expense_formatted }}'),
        (r'\{\{\s*ess\s*\}\}\s*\{\{\s*ess\s*\}\}', '{{ client_address }}'),
        
        # 2. 잘못된 Handlebars + Jinja2 혼재 문법 수정
        (r'\{\{#\{\%\s*if\s+has_iso14001\s*\%\}\s*\}\}', '{% if has_iso14001 %}'),
        (r'\{\{/\{\%\s*if\s*\%\}\s*\}\}', '{% endif %}'),
        
        # 3. 분할된 변수명 복구
        (r'cli\s*ame', 'client_name'),
        (r'sta\s*ext', 'standards_text'),
        (r'quo\s*ate', 'quotation_date'),
        (r'tot\s*ber', 'total_audit_days'),
        (r'iso\s*ber', 'iso9001_days'),
        (r'iso\s*ays', 'iso9001_days'),
        (r'iso\s*ncy', 'iso9001_cost_formatted'),
        (r'tra\s*ncy', 'travel_expense_formatted'),
        (r'cli\s*ess', 'client_address'),
        
        # 4. 단일 중복 태그 정리
        (r'\{\{\s*cli\s*\}\}', '{{ client_name }}'),
        (r'\{\{\s*ame\s*\}\}', '{{ client_name }}'),
        (r'\{\{\s*sta\s*\}\}', '{{ standards_text }}'),
        (r'\{\{\s*ext\s*\}\}', '{{ standards_text }}'),
        (r'\{\{\s*quo\s*\}\}', '{{ quotation_date }}'),
        (r'\{\{\s*ate\s*\}\}', '{{ quotation_date }}'),
        (r'\{\{\s*ber\s*\}\}', '{{ total_audit_days }}'),
        (r'\{\{\s*tot\s*\}\}', '{{ total_cost_with_travel_formatted }}'),
        (r'\{\{\s*iso\s*\}\}', '{{ iso9001_days }}'),
        (r'\{\{\s*ays\s*\}\}', '{{ iso9001_days }}'),
        (r'\{\{\s*ncy\s*\}\}', '{{ iso9001_cost_formatted }}'),
        (r'\{\{\s*tra\s*\}\}', '{{ travel_expense_formatted }}'),
        (r'\{\{\s*ess\s*\}\}', '{{ client_address }}'),
        
        # 5. 기타 정리
        (r'\{\{\s*iso9\s*days\s*\}\}', '{{ iso9001_days }}'),
        (r'\{\{\s*iso9\s*ber\s*\}\}', '{{ iso9001_days }}'),
    ]
    
    # 수정 적용
    original_content = content
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    print(f"📝 수정된 문서 크기: {len(content)} bytes")
    print(f"🔄 변경된 라인 수: {len(content.splitlines()) - len(original_content.splitlines())}")
    
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
    print("\n🔍 수정 결과 검증...")
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        with zip_ref.open('word/document.xml') as doc_file:
            fixed_content = doc_file.read().decode('utf-8')
    
    # 중복 태그 검사
    duplicate_patterns = [
        r'\{\{\s*cli\s*\}\}.*\{\{\s*cli\s*\}\}',
        r'\{\{\s*ame\s*\}\}.*\{\{\s*ame\s*\}\}',
        r'\{\{\s*sta\s*\}\}.*\{\{\s*sta\s*\}\}',
        r'\{\{\s*ext\s*\}\}.*\{\{\s*ext\s*\}\}',
    ]
    
    duplicates_found = 0
    for pattern in duplicate_patterns:
        matches = re.findall(pattern, fixed_content, re.IGNORECASE)
        if matches:
            duplicates_found += len(matches)
            print(f"⚠️  중복 태그 발견: {pattern} - {len(matches)}개")
    
    if duplicates_found == 0:
        print("✅ 중복 태그 모두 제거됨")
    else:
        print(f"⚠️  {duplicates_found}개의 중복 태그가 남아있음")
    
    # 변수 검사
    variables = re.findall(r'\{\{\s*([^}]+)\s*\}\}', fixed_content)
    unique_variables = set(variables)
    print(f"📊 발견된 변수: {len(unique_variables)}개")
    for var in sorted(unique_variables):
        print(f"  - {var}")
    
    return fixed_path

if __name__ == "__main__":
    try:
        result = fix_vercel_template()
        print(f"\n🎉 Vercel 템플릿 수정 완료: {result}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
