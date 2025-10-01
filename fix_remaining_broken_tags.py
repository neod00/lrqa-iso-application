#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
남은 분리된 태그들을 수정하는 도구
"""

import os
import zipfile
import re
from pathlib import Path

def fix_remaining_broken_tags(template_path):
    """남은 분리된 태그들을 수정합니다."""
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            document_xml = zip_file.read('word/document.xml')
            xml_content = document_xml.decode('utf-8')
            
            print(f"🔧 분리된 태그 수정: {template_path}")
            print("="*60)
            
            original_content = xml_content
            
            # 1. iso9001_stage 관련 분리된 태그 수정
            # {{ iso9001_stage</w:t></w:r><w:r w:rsidR="000421A6">...2</w:t></w:r>..._days }}
            # 를 {{ iso9001_stage2_days }}로 수정
            pattern1 = r'\{\{\s*iso9001_stage</w:t></w:r><w:r[^>]*>.*?2</w:t></w:r>.*?_days\s*\}\}'
            replacement1 = '{{ iso9001_stage2_days }}'
            xml_content = re.sub(pattern1, replacement1, xml_content, flags=re.DOTALL)
            
            # 2. total_cost_with_travel 관련 분리된 태그 수정
            # {{ </w:t></w:r><w:r w:rsidR="00842B4A">...total_cost_with_travel...| format_currency </w:t></w:r>...}}
            # 를 {{ total_cost_with_travel | format_currency }}로 수정
            pattern2 = r'\{\{\s*</w:t></w:r><w:r[^>]*>.*?total_cost_with_travel.*?\| format_currency\s*</w:t></w:r>.*?\}\}'
            replacement2 = '{{ total_cost_with_travel | format_currency }}'
            xml_content = re.sub(pattern2, replacement2, xml_content, flags=re.DOTALL)
            
            # 변경사항 확인
            changes_made = xml_content != original_content
            
            if changes_made:
                print("✅ 분리된 태그 수정 완료:")
                
                # 수정된 태그들 확인
                template_pattern = r'\{\{[^}]+\}\}'
                template_tags = re.findall(template_pattern, xml_content)
                
                print(f"📊 수정 후 템플릿 태그 개수: {len(template_tags)}")
                print("📋 수정된 태그들:")
                for tag in template_tags:
                    if 'iso9001_stage2_days' in tag or 'total_cost_with_travel' in tag:
                        print(f"   - {tag}")
                
                # 수정된 파일 저장
                with zipfile.ZipFile(template_path, 'w') as zip_file:
                    # 기존 파일들 복사
                    with zipfile.ZipFile(template_path, 'r') as original_zip:
                        for file_info in original_zip.infolist():
                            if file_info.filename != 'word/document.xml':
                                zip_file.writestr(file_info, original_zip.read(file_info.filename))
                    
                    # 수정된 document.xml 추가
                    zip_file.writestr('word/document.xml', xml_content.encode('utf-8'))
                
                print(f"💾 수정된 템플릿 저장 완료: {template_path}")
                return True
            else:
                print("ℹ️ 수정할 분리된 태그가 없습니다.")
                return False
                
    except Exception as e:
        print(f"❌ 태그 수정 오류: {e}")
        return False

def main():
    template_path = 'vercel-deploy/public/templates/LRQA_quotation.docx'
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    success = fix_remaining_broken_tags(template_path)
    
    if success:
        print(f"\n🎉 분리된 태그 수정 완료!")
        print(f"   이제 템플릿이 완전히 수정되었습니다.")
    else:
        print(f"\n⚠️ 수정이 필요하지 않거나 오류가 발생했습니다.")

if __name__ == "__main__":
    main()

