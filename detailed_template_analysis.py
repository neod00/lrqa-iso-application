#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
현재 템플릿을 Vercel 로그 오류 패턴 기준으로 상세 분석
"""

import zipfile
import tempfile
import shutil
import os
import re

def detailed_template_analysis(template_path):
    """Vercel 로그 오류 패턴을 기준으로 템플릿을 상세 분석합니다."""
    print(f"상세 템플릿 분석: {template_path}")
    
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
            
            print("=== Vercel 로그 오류 패턴 기준 분석 ===")
            
            # Vercel 로그에서 보고된 구체적인 오류 패턴들
            vercel_error_patterns = [
                # client_name 관련
                ('{{ cli', 'ame }}', 'client_name'),
                ('{{ cli', 'ess }}', 'client_address'),
                
                # standards_text 관련
                ('{{ sta', 'ext }}', 'standards_text'),
                
                # quotation 관련
                ('{{ quo', 'ate }}', 'quotation_date'),
                ('{{ quo', 'ber }}', 'quotation_number'),
                
                # total_employees 관련
                ('{{ tot', 'ees }}', 'total_employees'),
                ('{{ tot', 'ted }}', 'total_integrated'),
                
                # travel_expense 관련
                ('{{ tra', 'ted }}', 'travel_expense'),
                
                # iso 관련
                ('{{ iso', 'ays }}', 'iso_days'),
                ('{{ iso', 'ted }}', 'iso_integrated'),
            ]
            
            print("1. Vercel 오류 패턴 검사:")
            found_issues = []
            
            for start_part, end_part, var_name in vercel_error_patterns:
                # 시작 부분과 끝 부분이 분리되어 있는지 확인
                start_pattern = f'<w:t>{re.escape(start_part)}</w:t>'
                end_pattern = f'<w:t>{re.escape(end_part)}</w:t>'
                
                start_matches = re.findall(start_pattern, content)
                end_matches = re.findall(end_pattern, content)
                
                if start_matches and end_matches:
                    print(f"  ⚠️  {var_name}: 분리된 패턴 발견!")
                    print(f"    - 시작 부분 '{start_part}': {len(start_matches)}개")
                    print(f"    - 끝 부분 '{end_part}': {len(end_matches)}개")
                    
                    # 실제 컨텍스트 확인
                    for i, match in enumerate(start_matches[:2]):
                        start_pos = content.find(match)
                        if start_pos != -1:
                            context_start = max(0, start_pos - 50)
                            context_end = min(len(content), start_pos + 150)
                            context = content[context_start:context_end]
                            print(f"    컨텍스트 {i+1}: ...{context}...")
                    
                    found_issues.append((var_name, start_part, end_part))
                else:
                    print(f"  ✓ {var_name}: 정상")
            
            # 2. 더 정확한 분리 패턴 검사
            print("\n2. 정확한 분리 패턴 검사:")
            
            # {{ 시작 + </w:t> + 중간 태그들 + <w:t> + 끝 }}
            separated_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)</w:t>.*?<w:t>([a-zA-Z_]+)\s*\}\}</w:t>'
            separated_matches = re.findall(separated_pattern, content, re.DOTALL)
            
            if separated_matches:
                print(f"  ⚠️  분리된 변수 발견: {len(separated_matches)}개")
                for i, (part1, part2) in enumerate(separated_matches, 1):
                    print(f"    {i}. {{ {part1} }} + {{ {part2} }}")
                    
                    # 해당 패턴의 실제 XML 구조 확인
                    pattern = f'<w:t>{{{{ {part1}</w:t>.*?<w:t>{part2} }}}}</w:t>'
                    matches = re.findall(pattern, content, re.DOTALL)
                    if matches:
                        print(f"       실제 구조: {matches[0][:200]}...")
            else:
                print("  ✓ 분리된 변수 없음")
            
            # 3. 모든 템플릿 변수 목록
            print("\n3. 전체 템플릿 변수 목록:")
            
            # 정상적인 변수들
            normal_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)\s*\}\}</w:t>'
            normal_matches = re.findall(normal_pattern, content)
            unique_vars = set(normal_matches)
            
            print(f"  정상적인 변수: {len(unique_vars)}개")
            for var in sorted(unique_vars):
                count = normal_matches.count(var)
                print(f"    - {var}: {count}개")
            
            # 4. 문제가 있는 라인들 찾기
            print("\n4. 문제가 있는 라인들:")
            
            lines = content.split('\n')
            problem_lines = []
            
            for i, line in enumerate(lines, 1):
                if '{{' in line and '}}' in line:
                    # {{ 와 }} 사이에 </w:t>가 있는지 확인
                    if '{{' in line and '</w:t>' in line and '}}' in line:
                        if line.find('{{') < line.find('</w:t>') < line.find('}}'):
                            problem_lines.append((i, line.strip()))
            
            if problem_lines:
                print(f"  문제가 있는 라인: {len(problem_lines)}개")
                for line_num, line_content in problem_lines[:10]:  # 처음 10개만
                    print(f"    라인 {line_num}: {line_content}")
            else:
                print("  ✓ 문제가 있는 라인 없음")
            
            # 5. docxtemplater 호환성 검사
            print("\n5. docxtemplater 호환성 검사:")
            
            # 단일 텍스트 노드 내의 변수들
            single_node_vars = []
            for match in re.finditer(r'<w:t>([^<]*\{\{[^}]*\}\}[^<]*)</w:t>', content):
                var_text = match.group(1)
                if '{{' in var_text and '}}' in var_text:
                    single_node_vars.append(var_text.strip())
            
            print(f"  단일 노드 내 변수: {len(single_node_vars)}개")
            for i, var in enumerate(single_node_vars[:10]):  # 처음 10개만
                print(f"    {i+1}. {var}")
            
            return len(found_issues) > 0 or len(separated_matches) > 0
            
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    
    if os.path.exists(template_path):
        has_issues = detailed_template_analysis(template_path)
        
        if has_issues:
            print("\n⚠️  템플릿에 분리된 변수 문제가 있습니다.")
            print("docxtemplater가 올바르게 파싱하지 못할 수 있습니다.")
        else:
            print("\n✅ 템플릿에 분리된 변수 문제가 없습니다.")
            print("docxtemplater와 호환됩니다.")
    else:
        print(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
