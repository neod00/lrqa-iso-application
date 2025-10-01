#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드 템플릿의 변수 분리 문제를 수정하는 스크립트
"""

import zipfile
import tempfile
import shutil
import os
import re
import xml.etree.ElementTree as ET

def fix_template_variables(template_path, output_path):
    """워드 템플릿의 변수 분리 문제를 수정합니다."""
    print(f"템플릿 변수 수정 중: {template_path}")
    
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
            
            # 변수 분리 패턴 찾기 및 수정
            patterns_to_fix = [
                # client_name 변수
                (r'<w:t>\{\{\s*cli</w:t>\s*<w:t>ame\s*\}\}</w:t>', 
                 '<w:t>{{ client_name }}</w:t>'),
                
                # standards_text 변수
                (r'<w:t>\{\{\s*sta</w:t>\s*<w:t>ext\s*\}\}</w:t>', 
                 '<w:t>{{ standards_text }}</w:t>'),
                
                # quotation_date 변수
                (r'<w:t>\{\{\s*quo</w:t>\s*<w:t>ate\s*\}\}</w:t>', 
                 '<w:t>{{ quotation_date }}</w:t>'),
                
                # total_employees 변수
                (r'<w:t>\{\{\s*tot</w:t>\s*<w:t>ees\s*\}\}</w:t>', 
                 '<w:t>{{ total_employees }}</w:t>'),
                
                # iso_days 변수들
                (r'<w:t>\{\{\s*iso</w:t>\s*<w:t>ays\s*\}\}</w:t>', 
                 '<w:t>{{ iso_days }}</w:t>'),
                
                (r'<w:t>\{\{\s*iso</w:t>\s*<w:t>ted\s*\}\}</w:t>', 
                 '<w:t>{{ iso_integrated }}</w:t>'),
                
                # travel_expense 변수
                (r'<w:t>\{\{\s*tra</w:t>\s*<w:t>ted\s*\}\}</w:t>', 
                 '<w:t>{{ travel_expense }}</w:t>'),
                
                # 기타 분리된 변수들
                (r'<w:t>\{\{\s*([a-zA-Z_]+)</w:t>\s*<w:t>([a-zA-Z_]+)\s*\}\}</w:t>', 
                 r'<w:t>{{ \1_\2 }}</w:t>'),
            ]
            
            original_content = content
            modifications_made = 0
            
            for pattern, replacement in patterns_to_fix:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"  패턴 수정: {pattern[:50]}...")
                    print(f"    발견된 매치: {len(matches)}개")
                    content = re.sub(pattern, replacement, content)
                    modifications_made += len(matches)
            
            if modifications_made > 0:
                print(f"  총 {modifications_made}개의 변수 분리 문제를 수정했습니다.")
                
                # 수정된 내용을 파일에 저장
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print("  수정할 변수 분리 문제를 찾지 못했습니다.")
            
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

def analyze_template_variables(template_path):
    """템플릿의 변수 분리 문제를 분석합니다."""
    print(f"템플릿 변수 분석 중: {template_path}")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .docx 파일을 .zip으로 복사하여 압축 해제
        zip_path = os.path.join(temp_dir, "template.zip")
        shutil.copy2(template_path, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # document.xml 분석
        doc_path = os.path.join(temp_dir, "word/document.xml")
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 분리된 변수 패턴 찾기
            separated_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)</w:t>\s*<w:t>([a-zA-Z_]+)\s*\}\}</w:t>'
            matches = re.findall(separated_pattern, content)
            
            print(f"분리된 변수 발견: {len(matches)}개")
            for i, (part1, part2) in enumerate(matches, 1):
                print(f"  {i}. {{ {part1} }} + {{ {part2} }}")
            
            # 정상적인 변수 패턴 찾기
            normal_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)\s*\}\}</w:t>'
            normal_matches = re.findall(normal_pattern, content)
            
            print(f"정상적인 변수: {len(normal_matches)}개")
            unique_vars = set(normal_matches)
            for var in sorted(unique_vars):
                count = normal_matches.count(var)
                print(f"  - {var}: {count}개")
        
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    output_path = "vercel-deploy/public/templates/LRQA_quotation_fixed.docx"
    
    if os.path.exists(template_path):
        # 먼저 분석
        analyze_template_variables(template_path)
        
        print("\n" + "="*60)
        
        # 수정 실행
        if fix_template_variables(template_path, output_path):
            print("\n✓ 템플릿 수정이 완료되었습니다!")
            print(f"수정된 파일: {output_path}")
        else:
            print("\n✗ 템플릿 수정에 실패했습니다.")
    else:
        print(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
