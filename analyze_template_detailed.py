#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드 템플릿의 변수 분리 문제를 상세히 분석하는 스크립트
"""

import zipfile
import tempfile
import shutil
import os
import re

def analyze_template_detailed(template_path):
    """템플릿의 변수 분리 문제를 상세히 분석합니다."""
    print(f"상세 템플릿 분석 중: {template_path}")
    
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
            
            print("=== 템플릿 변수 분석 ===")
            
            # 1. 모든 {{ }} 패턴 찾기
            all_template_pattern = r'\{\{[^}]*\}\}'
            all_matches = re.findall(all_template_pattern, content)
            print(f"1. 전체 템플릿 변수: {len(all_matches)}개")
            
            # 2. 분리된 변수 패턴 찾기 (더 정확한 패턴)
            separated_patterns = [
                # {{ cli + ame }}
                (r'<w:t>\{\{\s*cli</w:t>', r'<w:t>ame\s*\}\}</w:t>', 'client_name'),
                # {{ sta + ext }}
                (r'<w:t>\{\{\s*sta</w:t>', r'<w:t>ext\s*\}\}</w:t>', 'standards_text'),
                # {{ quo + ate }}
                (r'<w:t>\{\{\s*quo</w:t>', r'<w:t>ate\s*\}\}</w:t>', 'quotation_date'),
                # {{ tot + ees }}
                (r'<w:t>\{\{\s*tot</w:t>', r'<w:t>ees\s*\}\}</w:t>', 'total_employees'),
                # {{ iso + ays }}
                (r'<w:t>\{\{\s*iso</w:t>', r'<w:t>ays\s*\}\}</w:t>', 'iso_days'),
                # {{ iso + ted }}
                (r'<w:t>\{\{\s*iso</w:t>', r'<w:t>ted\s*\}\}</w:t>', 'iso_integrated'),
                # {{ tra + ted }}
                (r'<w:t>\{\{\s*tra</w:t>', r'<w:t>ted\s*\}\}</w:t>', 'travel_expense'),
            ]
            
            separated_count = 0
            for start_pattern, end_pattern, var_name in separated_patterns:
                start_matches = re.findall(start_pattern, content)
                end_matches = re.findall(end_pattern, content)
                if start_matches and end_matches:
                    print(f"2. 분리된 변수 '{var_name}': {len(start_matches)}개")
                    separated_count += len(start_matches)
                    
                    # 주변 컨텍스트 출력
                    for i, match in enumerate(start_matches[:3]):  # 처음 3개만
                        start_pos = content.find(match)
                        if start_pos != -1:
                            context_start = max(0, start_pos - 50)
                            context_end = min(len(content), start_pos + 100)
                            context = content[context_start:context_end]
                            print(f"   컨텍스트 {i+1}: ...{context}...")
            
            print(f"   총 분리된 변수: {separated_count}개")
            
            # 3. 정상적인 변수 패턴 찾기
            normal_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)\s*\}\}</w:t>'
            normal_matches = re.findall(normal_pattern, content)
            print(f"3. 정상적인 변수: {len(normal_matches)}개")
            
            # 4. 텍스트 노드 내의 {{ }} 패턴 찾기
            text_node_pattern = r'<w:t>([^<]*\{\{[^}]*\}\}[^<]*)</w:t>'
            text_matches = re.findall(text_node_pattern, content)
            print(f"4. 텍스트 노드 내 변수: {len(text_matches)}개")
            
            # 5. 문제가 있는 패턴들 찾기
            print("\n=== 문제 패턴 분석 ===")
            
            # {{ 로 시작하지만 }} 로 끝나지 않는 패턴
            incomplete_start = re.findall(r'<w:t>\{\{[^}]*</w:t>', content)
            print(f"5. 불완전한 시작: {len(incomplete_start)}개")
            
            # }} 로 끝나지만 {{ 로 시작하지 않는 패턴
            incomplete_end = re.findall(r'<w:t>[^{]*\}\}</w:t>', content)
            print(f"6. 불완전한 끝: {len(incomplete_end)}개")
            
            # 6. 실제 문제가 있는 라인들 찾기
            lines = content.split('\n')
            problem_lines = []
            for i, line in enumerate(lines, 1):
                if '{{' in line and '}}' in line:
                    # {{ 와 }} 사이에 </w:t>가 있는지 확인
                    if '{{' in line and '</w:t>' in line and '}}' in line:
                        if line.find('{{') < line.find('</w:t>') < line.find('}}'):
                            problem_lines.append((i, line.strip()))
            
            if problem_lines:
                print(f"\n7. 문제가 있는 라인들: {len(problem_lines)}개")
                for line_num, line_content in problem_lines[:10]:  # 처음 10개만
                    print(f"   라인 {line_num}: {line_content}")
            
            # 8. docxtemplater가 인식할 수 있는 변수들
            print(f"\n=== docxtemplater 호환성 분석 ===")
            
            # 단일 텍스트 노드 내의 변수들
            single_node_vars = []
            for match in re.finditer(r'<w:t>([^<]*\{\{[^}]*\}\}[^<]*)</w:t>', content):
                var_text = match.group(1)
                if '{{' in var_text and '}}' in var_text:
                    single_node_vars.append(var_text.strip())
            
            print(f"8. 단일 노드 내 변수: {len(single_node_vars)}개")
            for var in single_node_vars[:10]:  # 처음 10개만
                print(f"   - {var}")
            
            return separated_count > 0
            
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    
    if os.path.exists(template_path):
        has_issues = analyze_template_detailed(template_path)
        
        if has_issues:
            print("\n⚠️  템플릿에 변수 분리 문제가 있습니다.")
            print("   docxtemplater가 올바르게 파싱하지 못할 수 있습니다.")
        else:
            print("\n✅ 템플릿에 변수 분리 문제가 없습니다.")
    else:
        print(f"템플릿 파일을 찾을 수 없습니다: {template_path}")