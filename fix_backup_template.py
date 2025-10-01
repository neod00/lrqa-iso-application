#!/usr/bin/env python3
"""
백업 파일을 작동하는 파일과 동일한 구조로 수정
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

def fix_backup_template():
    """백업 파일을 작동하는 파일과 동일한 구조로 수정합니다."""
    
    # 파일 경로
    working_file = "vercel-deploy/public/templates/LRQA_quotation.docx"
    backup_file = "vercel-deploy/public/templates/LRQA_quotation_backup_clean.docx"
    fixed_file = "vercel-deploy/public/templates/LRQA_quotation_backup_clean_fixed.docx"
    
    print("🔧 백업 파일을 작동하는 파일과 동일한 구조로 수정...")
    
    # 작동하는 파일의 구조를 백업 파일에 복사
    with zipfile.ZipFile(working_file, 'r') as working_zip:
        with zipfile.ZipFile(backup_file, 'r') as backup_zip:
            with zipfile.ZipFile(fixed_file, 'w', zipfile.ZIP_DEFLATED) as fixed_zip:
                
                # 작동하는 파일의 document.xml 사용
                working_doc = working_zip.read('word/document.xml')
                
                # 모든 파일을 백업 파일에서 복사하되, document.xml만 작동하는 파일에서 가져옴
                for item in backup_zip.infolist():
                    if item.filename == 'word/document.xml':
                        # 작동하는 파일의 document.xml 사용
                        fixed_zip.writestr(item, working_doc)
                    else:
                        # 다른 파일들은 백업 파일에서 복사
                        fixed_zip.writestr(item, backup_zip.read(item.filename))
    
    print(f"✅ 수정된 파일 저장: {fixed_file}")
    
    # 수정된 파일의 변수 확인
    with zipfile.ZipFile(fixed_file, 'r') as zip_ref:
        with zip_ref.open('word/document.xml') as doc_file:
            content = doc_file.read().decode('utf-8')
    
    variables = re.findall(r'\{([^}]+)\}', content)
    unique_variables = set(variables)
    
    print(f"📊 수정된 파일의 변수: {len(unique_variables)}개")
    print(f"\n📋 변수 목록:")
    for var in sorted(unique_variables):
        count = variables.count(var)
        print(f"  - {var} (사용 {count}회)")
    
    # 원본 백업 파일을 수정된 파일로 교체
    shutil.copy2(fixed_file, backup_file)
    print(f"✅ 원본 백업 파일 업데이트 완료")
    
    return fixed_file

if __name__ == "__main__":
    try:
        result = fix_backup_template()
        print(f"\n🎉 백업 파일 수정 완료: {result}")
        print("\n📝 이제 LRQA_quotation_backup_clean.docx 파일도 정상 작동합니다!")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

