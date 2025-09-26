#!/usr/bin/env python3
"""
Word 템플릿 파일에 {{ }} 구분자를 추가하는 최종 스크립트
"""

import zipfile
import os
import shutil
import re

def add_template_delimiters():
    """템플릿 파일에 {{ }} 구분자 추가"""
    
    # 원본 파일 경로
    original_template = "public/templates/LRQA_quotation.docx"
    backup_template = "public/templates/LRQA_quotation_backup_final.docx"
    fixed_template = "public/templates/LRQA_quotation_fixed_final.docx"
    
    # 백업 생성
    if os.path.exists(original_template):
        shutil.copy2(original_template, backup_template)
        print(f"백업 생성: {backup_template}")
    
    # Word 파일을 ZIP으로 열기
    with zipfile.ZipFile(original_template, 'r') as zip_read:
        with zipfile.ZipFile(fixed_template, 'w', zipfile.ZIP_DEFLATED) as zip_write:
            for file_info in zip_read.infolist():
                # 파일 내용 읽기
                content = zip_read.read(file_info.filename)
                
                # word/document.xml 파일인 경우 구분자 추가
                if file_info.filename == "word/document.xml":
                    content_str = content.decode('utf-8')
                    
                    # 변수명을 {{ 변수명 }}으로 변경
                    variables = [
                        'quotation_date', 'quotation_number', 'client_name', 'client_address',
                        'contact_person', 'contact_email', 'contact_phone', 'standards_text',
                        'total_sites', 'total_employees', 'total_audit_days', 'total_cost_with_travel_formatted',
                        'iso14001_surveillance_days', 'iso14001_stage1_2_days', 'iso14001_stage1_2_cost_formatted',
                        'travel_expense_formatted', 'has_iso9001', 'has_iso14001', 'has_iso45001'
                    ]
                    
                    for var in variables:
                        # 단순 변수명을 {{ 변수명 }}으로 변경
                        content_str = re.sub(rf'\b{var}\b', f'{{{{ {var} }}}}', content_str)
                    
                    # 변경된 내용을 다시 바이트로 변환
                    content = content_str.encode('utf-8')
                    print(f"구분자 추가 완료: {file_info.filename}")
                    print(f"변경된 변수들: {variables[:5]}...")
                
                # 파일 쓰기
                zip_write.writestr(file_info, content)
    
    # 원본 파일을 수정된 파일로 교체
    shutil.move(fixed_template, original_template)
    print(f"템플릿 파일 수정 완료: {original_template}")

if __name__ == "__main__":
    add_template_delimiters()
