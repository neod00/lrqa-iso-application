#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
템플릿 파일 직접 수정 도구 - 분리된 태그들을 올바른 형태로 수정
"""

import os
import zipfile
import shutil
import re
from pathlib import Path

def fix_template_direct(template_path):
    """템플릿 파일의 분리된 태그들을 직접 수정합니다."""
    try:
        # 백업 파일 생성
        backup_path = template_path + '.backup_direct'
        shutil.copy2(template_path, backup_path)
        print(f"📁 백업 파일 생성: {backup_path}")
        
        # 임시 디렉토리 생성
        temp_dir = 'temp_template_direct_fix'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        # ZIP 파일 압축 해제
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            zip_file.extractall(temp_dir)
        
        # document.xml 읽기
        document_path = os.path.join(temp_dir, 'word', 'document.xml')
        with open(document_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        print(f"🔧 분리된 태그 직접 수정 시작...")
        
        original_content = xml_content
        
        # 1. 분리된 태그들을 올바른 형태로 수정
        # 패턴: {{</w:t></w:r><w:r...>...변수명...</w:t></w:r>...}}
        # 결과: {{ 변수명 }}
        
        # client_name 태그 수정
        pattern1 = r'\{\{</w:t></w:r><w:r[^>]*>.*?client_name.*?</w:t></w:r>.*?\}\}'
        replacement1 = '{{ client_name }}'
        xml_content = re.sub(pattern1, replacement1, xml_content, flags=re.DOTALL)
        
        # quotation_date 태그 수정
        pattern2 = r'\{\{</w:t></w:r><w:r[^>]*>.*?quotation_date.*?</w:t></w:r>.*?\}\}'
        replacement2 = '{{ quotation_date }}'
        xml_content = re.sub(pattern2, replacement2, xml_content, flags=re.DOTALL)
        
        # quotation_number 태그 수정
        pattern3 = r'\{\{</w:t></w:r><w:r[^>]*>.*?quotation_number.*?</w:t></w:r>.*?\}\}'
        replacement3 = '{{ quotation_number }}'
        xml_content = re.sub(pattern3, replacement3, xml_content, flags=re.DOTALL)
        
        # standards_text 태그 수정
        pattern4 = r'\{\{</w:t></w:r><w:r[^>]*>.*?standards_text.*?</w:t></w:r>.*?\}\}'
        replacement4 = '{{ standards_text }}'
        xml_content = re.sub(pattern4, replacement4, xml_content, flags=re.DOTALL)
        
        # total_employees 태그 수정
        pattern5 = r'\{\{</w:t></w:r><w:r[^>]*>.*?total_employees.*?</w:t></w:r>.*?\}\}'
        replacement5 = '{{ total_employees }}'
        xml_content = re.sub(pattern5, replacement5, xml_content, flags=re.DOTALL)
        
        # total_audit_days 태그 수정
        pattern6 = r'\{\{</w:t></w:r><w:r[^>]*>.*?total_audit_days.*?</w:t></w:r>.*?\}\}'
        replacement6 = '{{ total_audit_days }}'
        xml_content = re.sub(pattern6, replacement6, xml_content, flags=re.DOTALL)
        
        # total_sites 태그 수정
        pattern7 = r'\{\{</w:t></w:r><w:r[^>]*>.*?total_sites.*?</w:t></w:r>.*?\}\}'
        replacement7 = '{{ total_sites }}'
        xml_content = re.sub(pattern7, replacement7, xml_content, flags=re.DOTALL)
        
        # client_address 태그 수정
        pattern8 = r'\{\{</w:t></w:r><w:r[^>]*>.*?client_address.*?</w:t></w:r>.*?\}\}'
        replacement8 = '{{ client_address }}'
        xml_content = re.sub(pattern8, replacement8, xml_content, flags=re.DOTALL)
        
        # iso9001_stage1_2_cost 태그 수정
        pattern9 = r'\{\{</w:t></w:r><w:r[^>]*>.*?iso9001_stage1_2_cost.*?\| format_currency.*?</w:t></w:r>.*?\}\}'
        replacement9 = '{{ iso9001_stage1_2_cost | format_currency }}'
        xml_content = re.sub(pattern9, replacement9, xml_content, flags=re.DOTALL)
        
        # iso9001_stage1_2_days 태그 수정
        pattern10 = r'\{\{</w:t></w:r><w:r[^>]*>.*?iso9001_stage1_2_days.*?</w:t></w:r>.*?\}\}'
        replacement10 = '{{ iso9001_stage1_2_days }}'
        xml_content = re.sub(pattern10, replacement10, xml_content, flags=re.DOTALL)
        
        # iso9001_stage2_days 태그 수정
        pattern11 = r'\{\{</w:t></w:r><w:r[^>]*>.*?iso9001_stage2_days.*?</w:t></w:r>.*?\}\}'
        replacement11 = '{{ iso9001_stage2_days }}'
        xml_content = re.sub(pattern11, replacement11, xml_content, flags=re.DOTALL)
        
        # total_cost_with_travel 태그 수정
        pattern12 = r'\{\{</w:t></w:r><w:r[^>]*>.*?total_cost_with_travel.*?\| format_currency.*?</w:t></w:r>.*?\}\}'
        replacement12 = '{{ total_cost_with_travel | format_currency }}'
        xml_content = re.sub(pattern12, replacement12, xml_content, flags=re.DOTALL)
        
        # {% endif %} 태그 수정 (잘못된 형태)
        pattern13 = r'\{\{</w:t></w:r><w:r[^>]*>.*?% endif %.*?</w:t></w:r>.*?\}\}'
        replacement13 = '{% endif %}'
        xml_content = re.sub(pattern13, replacement13, xml_content, flags=re.DOTALL)
        
        # 변경사항 확인
        changes_made = xml_content != original_content
        
        if changes_made:
            print("✅ 분리된 태그 수정 완료:")
            
            # 수정된 document.xml 저장
            with open(document_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            # 새로운 ZIP 파일 생성
            with zipfile.ZipFile(template_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, temp_dir)
                        new_zip.write(file_path, arc_path)
            
            print(f"💾 수정된 템플릿 저장 완료: {template_path}")
            
            # 임시 디렉토리 정리
            shutil.rmtree(temp_dir)
            
            return True
        else:
            print("ℹ️ 수정할 분리된 태그가 없습니다.")
            # 임시 디렉토리 정리
            shutil.rmtree(temp_dir)
            return False
                
    except Exception as e:
        print(f"❌ 태그 수정 오류: {e}")
        # 오류 발생 시 백업에서 복원
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, template_path)
            print(f"🔄 백업에서 복원: {template_path}")
        return False

def main():
    template_path = 'vercel-deploy/public/templates/LRQA_quotation.docx'
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    success = fix_template_direct(template_path)
    
    if success:
        print(f"\n🎉 템플릿 파일 직접 수정 완료!")
        print(f"   이제 치환 기능이 정상 작동할 것입니다.")
    else:
        print(f"\n⚠️ 수정이 필요하지 않거나 오류가 발생했습니다.")

if __name__ == "__main__":
    main()

