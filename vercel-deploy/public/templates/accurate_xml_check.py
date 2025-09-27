#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정확한 XML 구조 검사 스크립트
"""

import xml.etree.ElementTree as ET
import os
import zipfile
import tempfile
import shutil
import re

def accurate_xml_check(file_path):
    """정확한 XML 구조를 검사합니다."""
    print(f"정확한 XML 검사 중: {file_path}")
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .docx 파일을 .zip으로 복사하여 압축 해제
        zip_path = os.path.join(temp_dir, "template.zip")
        shutil.copy2(file_path, zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # document.xml 정확한 분석
        doc_path = os.path.join(temp_dir, "word/document.xml")
        if os.path.exists(doc_path):
            print("\n" + "="*60)
            print("정확한 XML 구조 검사")
            print("="*60)
            
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. 실제 XML 파싱 테스트
            print("1. XML 파싱 테스트:")
            try:
                tree = ET.parse(doc_path)
                root = tree.getroot()
                print("   ✓ XML 파싱 성공 - 파일이 유효한 XML입니다")
                
                # 루트 요소 확인
                print(f"   ✓ 루트 요소: {root.tag}")
                
                # 네임스페이스 확인
                if root.tag.startswith('{'):
                    namespace = root.tag.split('}')[0] + '}'
                    print(f"   ✓ 네임스페이스: {namespace}")
                
            except ET.ParseError as e:
                print(f"   ✗ XML 파싱 실패: {str(e)}")
                return False
            except Exception as e:
                print(f"   ✗ 기타 오류: {str(e)}")
                return False
            
            # 2. 정규식 기반 태그 분석 (더 정확한 패턴)
            print("\n2. 정규식 기반 태그 분석:")
            
            # 자체 닫는 태그 (정확한 패턴)
            self_closing_pattern = r'<(\w+)(?:\s+[^>]*)?\s*/>'
            self_closing_matches = re.findall(self_closing_pattern, content)
            self_closing_count = {}
            for tag in self_closing_matches:
                self_closing_count[tag] = self_closing_count.get(tag, 0) + 1
            
            print(f"   ✓ 자체 닫는 태그 종류: {len(self_closing_count)}")
            for tag, count in sorted(self_closing_count.items()):
                print(f"     - {tag}: {count}개")
            
            # 일반 열린 태그 (자체 닫는 태그 제외)
            open_pattern = r'<(\w+)(?:\s+[^>]*)?>(?![^<]*/>)'
            open_matches = re.findall(open_pattern, content)
            open_count = {}
            for tag in open_matches:
                open_count[tag] = open_count.get(tag, 0) + 1
            
            # 닫는 태그
            close_pattern = r'</(\w+)>'
            close_matches = re.findall(close_pattern, content)
            close_count = {}
            for tag in close_matches:
                close_count[tag] = close_count.get(tag, 0) + 1
            
            print(f"   ✓ 열린 태그 수: {len(open_matches)}")
            print(f"   ✓ 닫힌 태그 수: {len(close_matches)}")
            
            # 3. 태그 균형 분석
            print("\n3. 태그 균형 분석:")
            
            all_tags = set(open_count.keys()) | set(close_count.keys())
            balanced_tags = []
            unbalanced_tags = []
            
            for tag in all_tags:
                open_num = open_count.get(tag, 0)
                close_num = close_count.get(tag, 0)
                if open_num == close_num:
                    balanced_tags.append((tag, open_num))
                else:
                    unbalanced_tags.append((tag, open_num, close_num))
            
            print(f"   ✓ 균형 잡힌 태그: {len(balanced_tags)}개")
            if balanced_tags:
                for tag, count in sorted(balanced_tags):
                    print(f"     - {tag}: {count}개")
            
            if unbalanced_tags:
                print(f"   ✗ 불균형 태그: {len(unbalanced_tags)}개")
                for tag, open_num, close_num in sorted(unbalanced_tags):
                    diff = open_num - close_num
                    print(f"     - {tag}: 열림 {open_num}, 닫힘 {close_num} (차이: {diff:+d})")
            else:
                print("   ✓ 모든 태그가 균형을 이룸")
            
            # 4. XML 구조 검증
            print("\n4. XML 구조 검증:")
            
            # ElementTree로 실제 구조 확인
            try:
                # 모든 요소의 개수 확인
                all_elements = root.findall('.//*')
                print(f"   ✓ 총 XML 요소 수: {len(all_elements)}")
                
                # body 요소 확인
                body = root.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
                if body is not None:
                    print("   ✓ body 요소 존재")
                    print(f"   ✓ body 자식 요소 수: {len(body)}")
                else:
                    print("   ✗ body 요소 없음")
                
                # 단락 수 확인
                paragraphs = root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
                print(f"   ✓ 단락 수: {len(paragraphs)}")
                
                # 표 수 확인
                tables = root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl')
                print(f"   ✓ 표 수: {len(tables)}")
                
            except Exception as e:
                print(f"   ✗ 구조 검증 중 오류: {str(e)}")
            
            # 5. 최종 결론
            print("\n" + "="*60)
            print("최종 결론")
            print("="*60)
            
            if not unbalanced_tags:
                print("✅ XML 구조가 완전히 정상입니다!")
                print("   - 모든 태그가 올바르게 균형을 이룹니다")
                print("   - XML 파싱이 성공적으로 됩니다")
                print("   - 워드 템플릿이 정상적으로 작동할 것입니다")
            else:
                print("⚠️  XML 구조에 일부 문제가 있습니다:")
                print("   - 일부 태그가 불균형 상태입니다")
                print("   - 하지만 XML 파싱은 성공하므로 기본적인 기능은 작동할 것입니다")
                print("   - Word에서 다시 저장하면 완전히 수정될 수 있습니다")
            
            return len(unbalanced_tags) == 0
        
        return False
        
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    template_path = "LRQA_quotation.docx"
    if os.path.exists(template_path):
        accurate_xml_check(template_path)
    else:
        print(f"파일을 찾을 수 없습니다: {template_path}")
