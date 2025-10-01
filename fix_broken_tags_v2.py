#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
분리된 태그들을 수정하는 도구 v2 - 백업 후 수정
"""

import os
import zipfile
import shutil
import re
from pathlib import Path

def fix_broken_tags_v2(template_path):
    """분리된 태그들을 수정합니다."""
    try:
        # 백업 파일 생성
        backup_path = template_path + '.backup'
        shutil.copy2(template_path, backup_path)
        print(f"📁 백업 파일 생성: {backup_path}")
        
        # 임시 디렉토리 생성
        temp_dir = 'temp_template_fix'
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
        
        print(f"🔧 분리된 태그 수정 시작...")
        
        original_content = xml_content
        
        # 1. iso9001_stage 관련 분리된 태그 수정
        # 복잡한 패턴을 단계별로 수정
        pattern1 = r'\{\{\s*iso9001_stage</w:t></w:r><w:r[^>]*>.*?2</w:t></w:r>.*?_days\s*\}\}'
        replacement1 = '{{ iso9001_stage2_days }}'
        xml_content = re.sub(pattern1, replacement1, xml_content, flags=re.DOTALL)
        
        # 2. total_cost_with_travel 관련 분리된 태그 수정
        pattern2 = r'\{\{\s*</w:t></w:r><w:r[^>]*>.*?total_cost_with_travel.*?\| format_currency\s*</w:t></w:r>.*?\}\}'
        replacement2 = '{{ total_cost_with_travel | format_currency }}'
        xml_content = re.sub(pattern2, replacement2, xml_content, flags=re.DOTALL)
        
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
    
    success = fix_broken_tags_v2(template_path)
    
    if success:
        print(f"\n🎉 분리된 태그 수정 완료!")
        print(f"   이제 템플릿이 완전히 수정되었습니다.")
    else:
        print(f"\n⚠️ 수정이 필요하지 않거나 오류가 발생했습니다.")

if __name__ == "__main__":
    main()

