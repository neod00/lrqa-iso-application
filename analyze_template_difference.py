#!/usr/bin/env python3
"""
두 템플릿 파일의 차이점을 분석하고 문제를 해결합니다.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import shutil
from pathlib import Path

def analyze_template_difference():
    """두 템플릿 파일의 차이점을 분석합니다."""
    
    # 파일 경로
    working_file = "vercel-deploy/public/templates/LRQA_quotation.docx"
    broken_file = "vercel-deploy/public/templates/LRQA_quotation_backup_clean.docx"
    
    print("🔍 두 템플릿 파일의 차이점 분석...")
    
    # 두 파일의 내용 읽기
    def read_template_content(file_path):
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                with zip_ref.open('word/document.xml') as doc_file:
                    return doc_file.read().decode('utf-8')
        except Exception as e:
            print(f"❌ 파일 읽기 오류 {file_path}: {e}")
            return None
    
    working_content = read_template_content(working_file)
    broken_content = read_template_content(broken_file)
    
    if not working_content or not broken_content:
        print("❌ 파일을 읽을 수 없습니다.")
        return
    
    print(f"📄 작동하는 파일 크기: {len(working_content)} bytes")
    print(f"📄 문제 파일 크기: {len(broken_content)} bytes")
    
    # docxtemplater 변수 추출
    def extract_variables(content):
        variables = re.findall(r'\{([^}]+)\}', content)
        return set(variables)
    
    working_vars = extract_variables(working_content)
    broken_vars = extract_variables(broken_content)
    
    print(f"\n📊 변수 비교:")
    print(f"  작동하는 파일: {len(working_vars)}개 변수")
    print(f"  문제 파일: {len(broken_vars)}개 변수")
    
    print(f"\n✅ 작동하는 파일의 변수들:")
    for var in sorted(working_vars):
        print(f"  - {var}")
    
    print(f"\n❌ 문제 파일의 변수들:")
    for var in sorted(broken_vars):
        print(f"  - {var}")
    
    # 차이점 분석
    only_in_working = working_vars - broken_vars
    only_in_broken = broken_vars - working_vars
    common_vars = working_vars & broken_vars
    
    print(f"\n🔍 차이점 분석:")
    print(f"  공통 변수: {len(common_vars)}개")
    print(f"  작동하는 파일에만 있음: {len(only_in_working)}개")
    print(f"  문제 파일에만 있음: {len(only_in_broken)}개")
    
    if only_in_working:
        print(f"\n✅ 작동하는 파일에만 있는 변수들:")
        for var in sorted(only_in_working):
            print(f"  - {var}")
    
    if only_in_broken:
        print(f"\n❌ 문제 파일에만 있는 변수들:")
        for var in sorted(only_in_broken):
            print(f"  - {var}")
    
    # XML 구조 분석
    print(f"\n🔍 XML 구조 분석:")
    
    def analyze_xml_structure(content, name):
        try:
            root = ET.fromstring(content)
            print(f"\n{name}:")
            print(f"  루트 태그: {root.tag}")
            print(f"  자식 요소 수: {len(list(root))}")
            
            # 텍스트 노드 찾기
            text_nodes = []
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    text_nodes.append(elem.text.strip())
            
            print(f"  텍스트 노드 수: {len(text_nodes)}")
            
            # 변수가 포함된 텍스트 노드
            var_nodes = [node for node in text_nodes if '{' in node and '}' in node]
            print(f"  변수 포함 텍스트 노드: {len(var_nodes)}개")
            
            if var_nodes:
                print(f"  변수 포함 텍스트 예시:")
                for i, node in enumerate(var_nodes[:5]):  # 처음 5개만
                    print(f"    {i+1}. {node}")
            
        except Exception as e:
            print(f"❌ XML 분석 오류 {name}: {e}")
    
    analyze_xml_structure(working_content, "작동하는 파일")
    analyze_xml_structure(broken_content, "문제 파일")
    
    # 문제 파일 수정
    print(f"\n🔧 문제 파일 수정 중...")
    
    # 작동하는 파일의 변수들을 문제 파일에 추가
    fixed_content = broken_content
    
    # 누락된 변수들을 추가
    missing_vars = only_in_working
    if missing_vars:
        print(f"  누락된 변수 {len(missing_vars)}개 추가 중...")
        
        # 간단한 템플릿에 누락된 변수들 추가
        additional_content = ""
        for var in missing_vars:
            additional_content += f"<w:p><w:r><w:t>{var}: {{{var}}}</w:t></w:r></w:p>"
        
        # body 태그 안에 추가
        if '<w:body>' in fixed_content and '</w:body>' in fixed_content:
            fixed_content = fixed_content.replace('</w:body>', additional_content + '</w:body>')
        else:
            # body 태그가 없으면 추가
            fixed_content = fixed_content.replace('</w:document>', f'<w:body>{additional_content}</w:body></w:document>')
    
    # 수정된 파일 저장
    fixed_file = "vercel-deploy/public/templates/LRQA_quotation_backup_clean_fixed.docx"
    
    with zipfile.ZipFile(broken_file, 'r') as source_zip:
        with zipfile.ZipFile(fixed_file, 'w', zipfile.ZIP_DEFLATED) as target_zip:
            for item in source_zip.infolist():
                if item.filename == 'word/document.xml':
                    target_zip.writestr(item, fixed_content)
                else:
                    target_zip.writestr(item, source_zip.read(item.filename))
    
    print(f"✅ 수정된 파일 저장: {fixed_file}")
    
    # 수정된 파일의 변수 확인
    fixed_vars = extract_variables(fixed_content)
    print(f"\n📊 수정된 파일의 변수: {len(fixed_vars)}개")
    
    # 원본 파일로 복사하여 테스트
    shutil.copy2(working_file, "vercel-deploy/public/templates/LRQA_quotation_backup_clean_test.docx")
    print(f"✅ 테스트용 파일 생성: LRQA_quotation_backup_clean_test.docx")
    
    return fixed_file

if __name__ == "__main__":
    try:
        result = analyze_template_difference()
        print(f"\n🎉 분석 및 수정 완료: {result}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

