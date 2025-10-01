#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quotation_date 변수 수정 스크립트
"""

import zipfile
import tempfile
import os
import re
import shutil

def fix_quotation_date():
    """quotation_date 변수를 올바른 형식으로 수정합니다."""
    print("=== quotation_date 변수 수정 ===")
    
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    backup_path = "vercel-deploy/public/templates/LRQA_quotation_backup.docx"
    
    if not os.path.exists(template_path):
        print("❌ 템플릿 파일을 찾을 수 없습니다.")
        return False
    
    # 백업 생성
    shutil.copy2(template_path, backup_path)
    print(f"✅ 백업 생성: {backup_path}")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .docx 파일을 .zip으로 복사하여 압축 해제
        zip_path = os.path.join(temp_dir, "template.zip")
        with open(template_path, 'rb') as src, open(zip_path, 'wb') as dst:
            dst.write(src.read())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # document.xml 수정
        doc_path = os.path.join(temp_dir, "word/document.xml")
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("수정 전 패턴 확인:")
        wrong_patterns = re.findall(r'\{[^}]*quotation_date[^}]*\}', content)
        for pattern in wrong_patterns:
            print(f"   - {pattern}")
        
        # 잘못된 패턴을 올바른 패턴으로 수정
        # { quotation_date } -> {{ quotation_date }}
        content = re.sub(r'\{[^}]*quotation_date[^}]*\}', '{{ quotation_date }}', content)
        
        # {quotation_date} -> {{ quotation_date }}
        content = re.sub(r'\{quotation_date\}', '{{ quotation_date }}', content)
        
        print("\n수정 후 패턴 확인:")
        correct_patterns = re.findall(r'\{\{\s*quotation_date\s*\}\}', content)
        print(f"   ✅ {{ quotation_date }} 패턴: {len(correct_patterns)}개")
        
        # 수정된 내용 저장
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 새로운 .docx 파일 생성
        new_zip_path = os.path.join(temp_dir, "template_fixed.zip")
        with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file != "template.zip" and file != "template_fixed.zip":
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zip_ref.write(file_path, arcname)
        
        # 원본 파일 교체
        with open(new_zip_path, 'rb') as src, open(template_path, 'wb') as dst:
            dst.write(src.read())
        
        print(f"✅ 템플릿 수정 완료: {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ 수정 중 오류 발생: {e}")
        # 백업에서 복원
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, template_path)
            print("✅ 백업에서 복원했습니다.")
        return False
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("quotation_date 변수 수정 시작...\n")
    
    success = fix_quotation_date()
    
    if success:
        print("\n🎉 quotation_date 변수 수정 완료!")
        print("   이제 {{ quotation_date }} 패턴이 올바르게 설정되었습니다.")
    else:
        print("\n❌ 수정에 실패했습니다.")

