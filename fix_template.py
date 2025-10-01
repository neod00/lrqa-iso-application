#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 템플릿 파일 수정 도구 - 중복 태그 및 잘못된 조건부 태그 수정
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import shutil

def fix_template_tags(template_path, output_path):
    """템플릿 파일의 태그들을 수정합니다."""
    try:
        # 원본 파일 백업
        backup_path = template_path.replace('.docx', '_backup.docx')
        shutil.copy2(template_path, backup_path)
        print(f"✅ 백업 파일 생성: {backup_path}")
        
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            # word/document.xml 파일 읽기
            document_xml = zip_file.read('word/document.xml')
            xml_content = document_xml.decode('utf-8')
            
            print("🔧 템플릿 태그 수정 중...")
            
            # 1. 잘못된 조건부 태그 수정
            # {% if {{ variable }} %} -> {% if variable %}
            xml_content = re.sub(r'\{%\s*if\s*\{\{\s*([^}]+)\s*\}\}\s*%\}', r'{% if \1 %}', xml_content)
            
            # 2. 중복된 standards_text 태그 제거 (첫 번째만 유지)
            standards_count = 0
            def replace_standards_text(match):
                nonlocal standards_count
                standards_count += 1
                if standards_count == 1:
                    return match.group(0)  # 첫 번째는 유지
                else:
                    return ""  # 나머지는 제거
            
            xml_content = re.sub(r'\{\{\s*standards_text\s*\}\}', replace_standards_text, xml_content)
            
            # 3. 중복된 {% endif %} 태그 정리 (필요한 만큼만 유지)
            endif_count = xml_content.count('{% endif %}')
            if_count = xml_content.count('{% if ')
            
            # {% if %} 태그와 {% endif %} 태그 개수가 맞지 않으면 조정
            if endif_count > if_count:
                # {% endif %} 태그를 if_count만큼만 유지
                count = [0]
                def replace_endif(match):
                    count[0] += 1
                    return match.group(0) if count[0] <= if_count else ''
                xml_content = re.sub(r'\{%\s*endif\s*%\}', replace_endif, xml_content)
            
            # 4. XML 구조 정리 - 분리된 태그들을 하나로 합치기
            # {{ tag | filter }} 형태의 분리된 태그들을 수정
            xml_content = re.sub(r'\{\{\s*([^}]+?)\s*\|\s*format_currency\s*\}\}', r'{{ \1 | format_currency }}', xml_content)
            
            # 5. 잘못된 태그 이름들 수정
            tag_fixes = {
                'iso9001_stage1_2_cost </w:t></w:r><w:r w:rsidR="0008427D"><w:rPr><w:rFonts w:ascii="맑은 고딕" w:eastAsia="맑은 고딕" w:hAnsi="맑은 고딕" w:hint="eastAsia"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:eastAsia="ko-KR"/></w:rPr><w:t xml:space="preserve">| </w:t></w:r><w:r w:rsidR="00207F85"><w:rPr><w:rFonts w:ascii="맑은 고딕" w:eastAsia="맑은 고딕" w:hAnsi="맑은 고딕" w:hint="eastAsia"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:eastAsia="ko-KR"/></w:rPr><w:t xml:space="preserve">format_currency </w:t></w:r><w:r w:rsidRPr="00373D8A"><w:rPr><w:rFonts w:ascii="맑은 고딕" w:eastAsia="맑은 고딕" w:hAnsi="맑은 고딕"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:eastAsia="ko-KR"/></w:rPr><w:t>}}': '{{ iso9001_stage1_2_cost | format_currency }}',
                'iso</w:t></w:r><w:r w:rsidR="0008427D"><w:rPr><w:rFonts w:ascii="맑은 고딕" w:eastAsia="맑은 고딕" w:hAnsi="맑은 고딕" w:hint="eastAsia"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:eastAsia="ko-KR"/></w:rPr><w:t xml:space="preserve">| </w:t></w:r><w:r w:rsidR="00207F85"><w:rPr><w:rFonts w:ascii="맑은 고딕" w:eastAsia="맑은 고딕" w:hAnsi="맑은 고딕" w:hint="eastAsia"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:eastAsia="ko-KR"/></w:rPr><w:t xml:space="preserve">format_currency </w:t></w:r><w:r w:rsidRPr="00373D8A"><w:rPr><w:rFonts w:ascii="맑은 고딕" w:eastAsia="맑은 고딕" w:hAnsi="맑은 고딕"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:lang w:eastAsia="ko-KR"/></w:rPr><w:t>}}': '{{ iso9001_stage1_2_cost | format_currency }}'
            }
            
            for old_tag, new_tag in tag_fixes.items():
                xml_content = xml_content.replace(old_tag, new_tag)
            
            # 수정된 XML을 바이트로 변환
            fixed_xml = xml_content.encode('utf-8')
            
            # 새로운 ZIP 파일 생성
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                # 기존 파일들을 복사
                for item in zip_file.infolist():
                    if item.filename != 'word/document.xml':
                        new_zip.writestr(item, zip_file.read(item.filename))
                    else:
                        # 수정된 document.xml 저장
                        new_zip.writestr('word/document.xml', fixed_xml)
            
            print(f"✅ 수정된 템플릿 저장: {output_path}")
            return True
            
    except Exception as e:
        print(f"❌ 템플릿 수정 오류: {e}")
        return False

def verify_fixed_template(template_path):
    """수정된 템플릿을 검증합니다."""
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_file:
            document_xml = zip_file.read('word/document.xml')
            xml_content = document_xml.decode('utf-8')
            
            # 템플릿 태그들 찾기
            template_pattern = r'\{\{[^}]+\}\}'
            conditional_pattern = r'\{%[^%]+\%\}'
            
            template_tags = re.findall(template_pattern, xml_content)
            conditional_tags = re.findall(conditional_pattern, xml_content)
            
            # 중복 태그 확인
            template_tag_counts = {}
            conditional_tag_counts = {}
            
            for tag in template_tags:
                template_tag_counts[tag] = template_tag_counts.get(tag, 0) + 1
            
            for tag in conditional_tags:
                conditional_tag_counts[tag] = conditional_tag_counts.get(tag, 0) + 1
            
            duplicate_template_tags = {tag: count for tag, count in template_tag_counts.items() if count > 1}
            duplicate_conditional_tags = {tag: count for tag, count in conditional_tag_counts.items() if count > 1}
            
            print(f"\n📊 수정 후 템플릿 검증:")
            print(f"   - 템플릿 태그 개수: {len(template_tags)}")
            print(f"   - 조건부 태그 개수: {len(conditional_tags)}")
            print(f"   - 중복 템플릿 태그: {len(duplicate_template_tags)}개")
            print(f"   - 중복 조건부 태그: {len(duplicate_conditional_tags)}개")
            
            if duplicate_template_tags:
                print("   ⚠️ 중복된 템플릿 태그:")
                for tag, count in duplicate_template_tags.items():
                    print(f"      - {tag} ({count}번)")
            
            if duplicate_conditional_tags:
                print("   ⚠️ 중복된 조건부 태그:")
                for tag, count in duplicate_conditional_tags.items():
                    print(f"      - {tag} ({count}번)")
            
            return len(duplicate_template_tags) == 0 and len(duplicate_conditional_tags) == 0
            
    except Exception as e:
        print(f"❌ 템플릿 검증 오류: {e}")
        return False

def main():
    # 템플릿 파일 경로
    template_path = 'vercel-deploy/public/templates/LRQA_quotation.docx'
    fixed_template_path = 'vercel-deploy/public/templates/LRQA_quotation_fixed.docx'
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return
    
    print(f"🔧 템플릿 파일 수정 시작: {template_path}")
    print("="*80)
    
    # 템플릿 수정
    if fix_template_tags(template_path, fixed_template_path):
        print("\n✅ 템플릿 수정 완료!")
        
        # 수정된 템플릿 검증
        if verify_fixed_template(fixed_template_path):
            print("✅ 템플릿 검증 통과!")
            
            # 원본 파일을 수정된 파일로 교체
            shutil.copy2(fixed_template_path, template_path)
            print("✅ 원본 템플릿 파일 업데이트 완료!")
            
            # 임시 파일 삭제
            os.remove(fixed_template_path)
            print("✅ 임시 파일 정리 완료!")
        else:
            print("❌ 템플릿 검증 실패!")
    else:
        print("❌ 템플릿 수정 실패!")

if __name__ == "__main__":
    main()
