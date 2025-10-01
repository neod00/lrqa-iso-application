#!/usr/bin/env python3
"""
Vercel 템플릿을 docxtemplater 문법으로 수정
- jinja2 문법 → docxtemplater 문법 변환
- 중복 태그 제거
- XML 구조 복구
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

def fix_vercel_template_docxtemplater():
    """Vercel 템플릿을 docxtemplater 문법으로 수정합니다."""
    
    # 파일 경로
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    backup_path = "vercel-deploy/public/templates/LRQA_quotation_backup.docx"
    fixed_path = "vercel-deploy/public/templates/LRQA_quotation_docxtemplater.docx"
    
    print("🔧 Vercel 템플릿을 docxtemplater 문법으로 수정...")
    
    # 백업 생성
    shutil.copy2(template_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # ZIP 파일로 열기
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        # word/document.xml 읽기
        with zip_ref.open('word/document.xml') as doc_file:
            content = doc_file.read().decode('utf-8')
    
    print(f"📄 원본 문서 크기: {len(content)} bytes")
    
    # docxtemplater 문법으로 변환
    fixes = [
        # 1. jinja2 → docxtemplater 변수 문법 변환
        (r'\{\{\s*([^}]+)\s*\}\}', r'{\1}'),
        
        # 2. jinja2 조건문 → docxtemplater 조건문 변환
        (r'\{\%\s*if\s+([^%]+)\s*\%\}', r'{#if \1}'),
        (r'\{\%\s*endif\s*\%\}', r'{/if}'),
        (r'\{\%\s*for\s+([^%]+)\s*\%\}', r'{#each \1}'),
        (r'\{\%\s*endfor\s*\%\}', r'{/each}'),
        
        # 3. 중복된 태그 제거 (docxtemplater는 중복을 허용하지 않음)
        (r'\{([^}]+)\}\s*\{([^}]+)\}', r'{\1}'),
        
        # 4. 분할된 변수명 복구
        (r'cli\s*ame', 'client_name'),
        (r'sta\s*ext', 'standards_text'),
        (r'quo\s*ate', 'quotation_date'),
        (r'tot\s*ber', 'total_audit_days'),
        (r'iso\s*ber', 'iso9001_days'),
        (r'iso\s*ays', 'iso9001_days'),
        (r'iso\s*ncy', 'iso9001_cost_formatted'),
        (r'tra\s*ncy', 'travel_expense_formatted'),
        (r'cli\s*ess', 'client_address'),
        
        # 5. 필터 제거 (docxtemplater는 필터를 지원하지 않음)
        (r'\|format_currency', ''),
        (r'\|format_number', ''),
        (r'\|format_date', ''),
        (r'\|format_boolean', ''),
        (r'\|safe_divide', ''),
        
        # 6. 잘못된 문법 정리
        (r'\{\{\s*#\s*', '{#'),
        (r'\{\{\s*/\s*', '{/'),
        (r'\}\}\s*#\s*', '}'),
        (r'\}\}\s*/\s*', '}'),
        
        # 7. 공백 정리
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
    print("\n🔍 수정 결과 검증...")
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        with zip_ref.open('word/document.xml') as doc_file:
            fixed_content = doc_file.read().decode('utf-8')
    
    # docxtemplater 문법 검사
    print("📊 docxtemplater 문법 검사...")
    
    # 변수 문법 검사
    variables = re.findall(r'\{([^}]+)\}', fixed_content)
    jinja2_variables = re.findall(r'\{\{([^}]+)\}\}', fixed_content)
    
    print(f"✅ docxtemplater 변수: {len(variables)}개")
    print(f"⚠️  jinja2 변수: {len(jinja2_variables)}개")
    
    if jinja2_variables:
        print("⚠️  아직 jinja2 문법이 남아있습니다:")
        for var in jinja2_variables[:5]:  # 처음 5개만 표시
            print(f"    - {var}")
    
    # 조건문 검사
    if_blocks = re.findall(r'\{#if\s+([^}]+)\}', fixed_content)
    endif_blocks = re.findall(r'\{/if\}', fixed_content)
    
    print(f"📊 조건문 블록: {len(if_blocks)}개 시작, {len(endif_blocks)}개 종료")
    
    if len(if_blocks) != len(endif_blocks):
        print("⚠️  조건문 블록이 맞지 않습니다!")
    else:
        print("✅ 조건문 블록이 올바르게 매칭됩니다")
    
    # 변수 목록 출력
    unique_variables = set(variables)
    print(f"\n📋 사용된 변수 목록 ({len(unique_variables)}개):")
    for var in sorted(unique_variables):
        count = variables.count(var)
        print(f"  - {var} (사용 {count}회)")
    
    return fixed_path

if __name__ == "__main__":
    try:
        result = fix_vercel_template_docxtemplater()
        print(f"\n🎉 Vercel 템플릿 수정 완료: {result}")
        print("\n📝 다음 단계:")
        print("1. Git에 변경사항 커밋")
        print("2. Vercel에 배포")
        print("3. 견적서 생성 테스트")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
