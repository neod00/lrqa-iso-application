#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로컬 템플릿의 상세 분석 및 문제점 확인
"""

import zipfile
import tempfile
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime

def analyze_local_template():
    """로컬 템플릿을 상세 분석합니다."""
    print("=== 로컬 템플릿 상세 분석 ===")
    print(f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    
    if not os.path.exists(template_path):
        print("❌ 템플릿 파일을 찾을 수 없습니다.")
        return False
    
    print(f"✅ 템플릿 파일 발견: {template_path}")
    print(f"   파일 크기: {os.path.getsize(template_path):,} bytes")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .docx 파일을 .zip으로 복사하여 압축 해제
        zip_path = os.path.join(temp_dir, "template.zip")
        with open(template_path, 'rb') as src, open(zip_path, 'wb') as dst:
            dst.write(src.read())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # document.xml 분석
        doc_path = os.path.join(temp_dir, "word/document.xml")
        if not os.path.exists(doc_path):
            print("❌ document.xml을 찾을 수 없습니다.")
            return False
        
        print("\n=== document.xml 분석 ===")
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   파일 크기: {len(content):,} characters")
        
        # 1. 분리된 변수 패턴 확인
        print("\n1. 분리된 변수 패턴 확인:")
        separated_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)</w:t>.*?<w:t>([a-zA-Z_]+)\s*\}\}</w:t>'
        separated_matches = re.findall(separated_pattern, content, re.DOTALL)
        
        if separated_matches:
            print(f"   ❌ 분리된 변수 발견: {len(separated_matches)}개")
            for i, (part1, part2) in enumerate(separated_matches, 1):
                print(f"      {i}. {{ {part1} }} + {{ {part2} }}")
            return False
        else:
            print("   ✅ 분리된 변수 없음")
        
        # 2. 정상적인 변수들 확인
        print("\n2. 정상적인 변수 확인:")
        normal_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)\s*\}\}</w:t>'
        normal_matches = re.findall(normal_pattern, content)
        unique_vars = set(normal_matches)
        
        print(f"   ✅ 정상적인 변수: {len(unique_vars)}개")
        for var in sorted(unique_vars):
            count = normal_matches.count(var)
            print(f"      - {var}: {count}개")
        
        # 3. XML 구조 검증
        print("\n3. XML 구조 검증:")
        try:
            root = ET.fromstring(content)
            print("   ✅ XML 파싱 성공")
            
            # body 요소 확인
            body = root.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
            if body is not None:
                print("   ✅ body 요소 존재")
                
                # 단락 수 확인
                paragraphs = body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
                print(f"   ✅ 단락 수: {len(paragraphs)}개")
                
                # 테이블 수 확인
                tables = body.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl')
                print(f"   ✅ 테이블 수: {len(tables)}개")
            else:
                print("   ❌ body 요소 없음")
                return False
                
        except ET.ParseError as e:
            print(f"   ❌ XML 파싱 오류: {e}")
            return False
        
        # 4. 특정 변수들의 존재 확인
        print("\n4. 주요 변수 존재 확인:")
        required_vars = [
            'client_name', 'standards_text', 'quotation_date', 
            'quotation_number', 'total_audit_days', 'total_cost_with_travel_formatted'
        ]
        
        for var in required_vars:
            if var in unique_vars:
                print(f"   ✅ {var}: 존재")
            else:
                print(f"   ❌ {var}: 없음")
        
        # 5. 텍스트 내용 샘플 확인
        print("\n5. 텍스트 내용 샘플:")
        text_elements = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', content)
        sample_texts = [text for text in text_elements if text.strip() and len(text.strip()) > 3][:10]
        
        for i, text in enumerate(sample_texts, 1):
            print(f"   {i}. {text[:50]}{'...' if len(text) > 50 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        return False
    finally:
        # 임시 디렉토리 정리
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def check_template_compatibility():
    """docxtemplater 호환성 확인"""
    print("\n=== docxtemplater 호환성 확인 ===")
    
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    
    if not os.path.exists(template_path):
        print("❌ 템플릿 파일을 찾을 수 없습니다.")
        return False
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .docx 파일을 .zip으로 복사하여 압축 해제
        zip_path = os.path.join(temp_dir, "template.zip")
        with open(template_path, 'rb') as src, open(zip_path, 'wb') as dst:
            dst.write(src.read())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # document.xml 분석
        doc_path = os.path.join(temp_dir, "word/document.xml")
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # docxtemplater가 인식할 수 있는 변수 패턴 확인
        print("1. docxtemplater 변수 패턴 확인:")
        
        # 정확한 {{ variable }} 패턴
        exact_pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
        exact_matches = re.findall(exact_pattern, content)
        
        print(f"   ✅ 정확한 변수 패턴: {len(exact_matches)}개")
        for var in set(exact_matches):
            count = exact_matches.count(var)
            print(f"      - {var}: {count}개")
        
        # 잘못된 패턴들 확인
        print("\n2. 잘못된 패턴 확인:")
        
        # 중괄호가 분리된 패턴
        split_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)</w:t>.*?<w:t>([a-zA-Z_]+)\s*\}\}</w:t>'
        split_matches = re.findall(split_pattern, content, re.DOTALL)
        
        if split_matches:
            print(f"   ❌ 분리된 변수: {len(split_matches)}개")
            for part1, part2 in split_matches:
                print(f"      - {{ {part1} }} + {{ {part2} }}")
        else:
            print("   ✅ 분리된 변수 없음")
        
        # 중괄호가 XML 태그로 분리된 패턴
        xml_split_pattern = r'<w:t>\{\{</w:t>.*?<w:t>([a-zA-Z_]+)</w:t>.*?<w:t>\}\}</w:t>'
        xml_split_matches = re.findall(xml_split_pattern, content, re.DOTALL)
        
        if xml_split_matches:
            print(f"   ❌ XML로 분리된 변수: {len(xml_split_matches)}개")
            for var in xml_split_matches:
                print(f"      - {{ {var} }}")
        else:
            print("   ✅ XML로 분리된 변수 없음")
        
        return len(split_matches) == 0 and len(xml_split_matches) == 0
        
    except Exception as e:
        print(f"❌ 호환성 확인 중 오류 발생: {e}")
        return False
    finally:
        # 임시 디렉토리 정리
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("로컬 템플릿 상세 분석 시작...\n")
    
    # 1. 기본 분석
    basic_ok = analyze_local_template()
    
    # 2. 호환성 확인
    compatibility_ok = check_template_compatibility()
    
    print("\n" + "="*60)
    print("=== 최종 결과 ===")
    print(f"기본 분석: {'✅ 통과' if basic_ok else '❌ 실패'}")
    print(f"호환성 확인: {'✅ 통과' if compatibility_ok else '❌ 실패'}")
    
    if basic_ok and compatibility_ok:
        print("\n🎉 로컬 템플릿이 정상입니다!")
        print("   docxtemplater와 완전히 호환됩니다.")
        print("   변수 치환이 정상적으로 작동해야 합니다.")
    else:
        print("\n⚠️  로컬 템플릿에 문제가 있습니다.")
        print("   추가 수정이 필요합니다.")

