#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드 템플릿의 분리된 변수들을 수정하는 최종 스크립트
"""

import zipfile
import tempfile
import shutil
import os
import re
import xml.etree.ElementTree as ET

def fix_template_final(template_path, output_path):
    """워드 템플릿의 분리된 변수들을 수정합니다."""
    print(f"최종 템플릿 수정 중: {template_path}")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .docx 파일을 .zip으로 복사하여 압축 해제
        zip_path = os.path.join(temp_dir, "template.zip")
        shutil.copy2(template_path, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # document.xml 수정
        doc_path = os.path.join(temp_dir, "word/document.xml")
        if os.path.exists(doc_path):
            print("document.xml 수정 중...")
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modifications_made = 0
            
            # 1. 분리된 변수들을 찾아서 수정
            # 패턴: {{ 변수명의 일부 + </w:t> + 중간 태그들 + <w:t> + 변수명의 나머지 }}
            
            # 복잡한 패턴을 단계별로 처리
            patterns_to_fix = [
                # {{ iso + 9001_stage1_2_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>9001_stage1_2_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso9001_stage1_2_days }}</w:t>'),
                
                # {{ iso + 9001_stage1_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>9001_stage1_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso9001_stage1_days }}</w:t>'),
                
                # {{ iso + 9001_stage2_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>9001_stage2_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso9001_stage2_days }}</w:t>'),
                
                # {{ iso + 9001_stage1_2_cost_formatted }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>9001_stage1_2_cost_formatted\s*\}\}</w:t>', 
                 '<w:t>{{ iso9001_stage1_2_cost_formatted }}</w:t>'),
                
                # {{ iso + 14001_stage1_2_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>14001_stage1_2_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso14001_stage1_2_days }}</w:t>'),
                
                # {{ iso + 14001_stage1_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>14001_stage1_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso14001_stage1_days }}</w:t>'),
                
                # {{ iso + 14001_stage2_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>14001_stage2_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso14001_stage2_days }}</w:t>'),
                
                # {{ iso + 14001_stage1_2_cost_formatted }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>14001_stage1_2_cost_formatted\s*\}\}</w:t>', 
                 '<w:t>{{ iso14001_stage1_2_cost_formatted }}</w:t>'),
                
                # {{ iso + 45001_stage1_2_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>45001_stage1_2_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso45001_stage1_2_days }}</w:t>'),
                
                # {{ iso + 45001_stage1_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>45001_stage1_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso45001_stage1_days }}</w:t>'),
                
                # {{ iso + 45001_stage2_ + days }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>45001_stage2_</w:t>.*?<w:t>days\s*\}\}</w:t>', 
                 '<w:t>{{ iso45001_stage2_days }}</w:t>'),
                
                # {{ iso + 45001_stage1_2_cost_formatted }}
                (r'<w:t>\{\{\s*iso</w:t>.*?<w:t>45001_stage1_2_cost_formatted\s*\}\}</w:t>', 
                 '<w:t>{{ iso45001_stage1_2_cost_formatted }}</w:t>'),
            ]
            
            for pattern, replacement in patterns_to_fix:
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    print(f"  패턴 수정: {pattern[:50]}...")
                    print(f"    발견된 매치: {len(matches)}개")
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    modifications_made += len(matches)
            
            # 2. 더 일반적인 패턴으로 남은 분리된 변수들 처리
            # {{ 변수명의 일부 + </w:t> + ... + <w:t> + 변수명의 나머지 }}
            general_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)</w:t>.*?<w:t>([a-zA-Z_]+)\s*\}\}</w:t>'
            general_matches = re.findall(general_pattern, content, re.DOTALL)
            
            if general_matches:
                print(f"  일반 패턴으로 추가 수정: {len(general_matches)}개")
                for part1, part2 in general_matches:
                    # 변수명을 합쳐서 수정
                    combined_var = f"{part1}_{part2}"
                    old_pattern = f'<w:t>{{{{ {part1}</w:t>.*?<w:t>{part2} }}}}</w:t>'
                    new_replacement = f'<w:t>{{{{ {combined_var} }}}}</w:t>'
                    content = re.sub(old_pattern, new_replacement, content, flags=re.DOTALL)
                    modifications_made += len(general_matches)
            
            if modifications_made > 0:
                print(f"  총 {modifications_made}개의 분리된 변수를 수정했습니다.")
                
                # 수정된 내용을 파일에 저장
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print("  수정할 분리된 변수를 찾지 못했습니다.")
            
            # XML 유효성 검사
            try:
                tree = ET.parse(doc_path)
                print("  ✓ XML 구조가 유효합니다.")
            except ET.ParseError as e:
                print(f"  ✗ XML 파싱 오류: {str(e)}")
                return False
        
        # 수정된 파일을 새 .docx로 압축
        print("수정된 템플릿을 새 파일로 저장 중...")
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)
        
        print(f"✓ 수정된 템플릿이 저장되었습니다: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ 오류 발생: {str(e)}")
        return False
        
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    output_path = "vercel-deploy/public/templates/LRQA_quotation_fixed.docx"
    
    if os.path.exists(template_path):
        if fix_template_final(template_path, output_path):
            print("\n✅ 템플릿 수정이 완료되었습니다!")
            print(f"수정된 파일: {output_path}")
            print("\n이제 이 파일을 원본 템플릿으로 교체하세요.")
        else:
            print("\n❌ 템플릿 수정에 실패했습니다.")
    else:
        print(f"템플릿 파일을 찾을 수 없습니다: {template_path}")