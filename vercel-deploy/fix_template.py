#!/usr/bin/env python3
"""
Word 템플릿 파일의 구분자를 {{ }}에서 { }로 변경하는 스크립트
"""

import zipfile
import os
import shutil

def fix_template_delimiters():
    """템플릿 파일의 구분자를 수정"""
    
    # 원본 파일 경로
    original_template = "public/templates/LRQA_quotation.docx"
    backup_template = "public/templates/LRQA_quotation_backup.docx"
    fixed_template = "public/templates/LRQA_quotation_fixed.docx"
    
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
                
                # word/document.xml 파일인 경우 구분자 변경
                if file_info.filename == "word/document.xml":
                    content_str = content.decode('utf-8')
                    
                    # {{ }}를 { }로 변경
                    content_str = content_str.replace('{{ ', '{')
                    content_str = content_str.replace(' }}', '}')
                    
                    # 변경된 내용을 다시 바이트로 변환
                    content = content_str.encode('utf-8')
                    print(f"구분자 변경 완료: {file_info.filename}")
                
                # 파일 쓰기
                zip_write.writestr(file_info, content)
    
    # 원본 파일을 수정된 파일로 교체
    shutil.move(fixed_template, original_template)
    print(f"템플릿 파일 수정 완료: {original_template}")

if __name__ == "__main__":
    fix_template_delimiters()
