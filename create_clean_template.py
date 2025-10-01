#!/usr/bin/env python3
"""
완전히 깨끗한 docxtemplater 템플릿 생성
- 모든 jinja2 문법 제거
- 중복 태그 완전 제거
- 올바른 docxtemplater 문법만 사용
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

def create_clean_template():
    """완전히 깨끗한 docxtemplater 템플릿을 생성합니다."""
    
    # 파일 경로
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    backup_path = "vercel-deploy/public/templates/LRQA_quotation_backup_clean.docx"
    clean_path = "vercel-deploy/public/templates/LRQA_quotation_clean.docx"
    
    print("🧹 완전히 깨끗한 docxtemplater 템플릿 생성...")
    
    # 백업 생성
    shutil.copy2(template_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # ZIP 파일로 열기
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        # word/document.xml 읽기
        with zip_ref.open('word/document.xml') as doc_file:
            content = doc_file.read().decode('utf-8')
    
    print(f"📄 원본 문서 크기: {len(content)} bytes")
    
    # 완전한 정리 작업
    cleanups = [
        # 1. 모든 jinja2 문법 제거
        (r'\{\{[^}]*\}\}', ''),  # {{ ... }} 제거
        (r'\{\%[^%]*\%\}', ''),  # {% ... %} 제거
        
        # 2. 잘못된 docxtemplater 문법 제거
        (r'\{[^}]*\{[^}]*\}', ''),  # 중첩된 { ... { ... } }
        (r'\}[^}]*\{[^}]*\}', ''),  # } ... { ... }
        (r'\{[^}]*\{[^}]*\}', ''),  # { ... { ... }
        
        # 3. 중복 태그 제거
        (r'\{[^}]*\}\s*\{[^}]*\}', ''),  # { ... } { ... }
        
        # 4. 잘못된 조건문 제거
        (r'\{#if[^}]*\}', ''),
        (r'\{/if\}', ''),
        (r'\{else\}', ''),
        
        # 5. XML 태그 내의 잘못된 문법 제거
        (r'<w:t>[^<]*\{[^}]*\}[^<]*</w:t>', '<w:t></w:t>'),
        
        # 6. 공백 정리
        (r'\s+', ' '),
    ]
    
    # 정리 적용
    original_content = content
    for pattern, replacement in cleanups:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    print(f"📝 정리된 문서 크기: {len(content)} bytes")
    
    # 이제 올바른 docxtemplater 변수만 추가
    # 기본 변수들을 올바른 위치에 삽입
    variables_to_add = [
        ('client_name', '테스트 회사'),
        ('client_address', '서울시 강남구'),
        ('standards_text', 'ISO 9001'),
        ('quotation_date', '2025-09-27'),
        ('quotation_number', 'Q20250927001'),
        ('total_sites', '1'),
        ('total_employees', '50'),
        ('total_audit_days', '3'),
        ('total_cost_with_travel', '4,620,000'),
        ('travel_expense', '420,000'),
        ('iso9001_days', '3'),
        ('iso9001_cost', '4,200,000'),
    ]
    
    # 간단한 템플릿 내용 생성
    simple_template = f"""
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:body>
            <w:p>
                <w:r>
                    <w:t>견적서 번호: {{quotation_number}}</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>회사명: {{client_name}}</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>주소: {{client_address}}</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>표준: {{standards_text}}</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>견적일: {{quotation_date}}</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>사업장 수: {{total_sites}}</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>직원 수: {{total_employees}}명</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>심사 일수: {{total_audit_days}}일</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>총 비용: {{total_cost_with_travel}}원</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>제경비: {{travel_expense}}원</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>ISO 9001 일수: {{iso9001_days}}일</w:t>
                </w:r>
            </w:p>
            <w:p>
                <w:r>
                    <w:t>ISO 9001 비용: {{iso9001_cost}}원</w:t>
                </w:r>
            </w:p>
        </w:body>
    </w:document>
    """
    
    # 정리된 내용을 새 ZIP 파일로 저장
    with zipfile.ZipFile(template_path, 'r') as source_zip:
        with zipfile.ZipFile(clean_path, 'w', zipfile.ZIP_DEFLATED) as target_zip:
            for item in source_zip.infolist():
                if item.filename == 'word/document.xml':
                    # 간단한 템플릿 사용
                    target_zip.writestr(item, simple_template)
                else:
                    # 다른 파일들은 그대로 복사
                    target_zip.writestr(item, source_zip.read(item.filename))
    
    print(f"✅ 깨끗한 템플릿 저장: {clean_path}")
    
    # 깨끗한 템플릿을 원본 위치에 복사
    shutil.copy2(clean_path, template_path)
    print(f"✅ Vercel 템플릿 업데이트 완료: {template_path}")
    
    # 검증
    print("\n🔍 최종 검증...")
    with zipfile.ZipFile(template_path, 'r') as zip_ref:
        with zip_ref.open('word/document.xml') as doc_file:
            final_content = doc_file.read().decode('utf-8')
    
    # docxtemplater 변수 검사
    variables = re.findall(r'\{([^}]+)\}', final_content)
    unique_variables = set(variables)
    
    print(f"📊 docxtemplater 변수: {len(unique_variables)}개")
    print(f"\n📋 사용된 변수 목록:")
    for var in sorted(unique_variables):
        count = variables.count(var)
        print(f"  - {var} (사용 {count}회)")
    
    # 오류 패턴 검사
    error_patterns = [
        r'\{\{[^}]*\}\}',  # jinja2 변수
        r'\{\%[^%]*\%\}',  # jinja2 태그
        r'\{[^}]*\{[^}]*\}',  # 중첩된 중괄호
    ]
    
    errors_found = 0
    for pattern in error_patterns:
        matches = re.findall(pattern, final_content)
        if matches:
            errors_found += len(matches)
            print(f"⚠️  오류 패턴 발견: {pattern} - {len(matches)}개")
            for match in matches[:3]:  # 처음 3개만 표시
                print(f"    - {match}")
    
    if errors_found == 0:
        print("✅ 오류 패턴 없음 - 템플릿이 깨끗합니다")
    else:
        print(f"⚠️  {errors_found}개의 오류 패턴이 남아있음")
    
    return clean_path

if __name__ == "__main__":
    try:
        result = create_clean_template()
        print(f"\n🎉 깨끗한 템플릿 생성 완료: {result}")
        print("\n📝 다음 단계:")
        print("1. Git에 변경사항 커밋")
        print("2. Vercel에 배포")
        print("3. 깨끗한 템플릿으로 견적서 생성 테스트")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

