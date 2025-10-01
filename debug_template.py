#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
템플릿 디버깅 스크립트
"""

import zipfile
import os
import re

def debug_template():
    """템플릿 파일 디버깅"""
    
    # 템플릿 파일 경로들
    template_paths = [
        "quotation-api/templates/LRQA_quotation.docx",
        "vercel-deploy/public/templates/LRQA_quotation_improved.docx"
    ]
    
    for template_path in template_paths:
        if os.path.exists(template_path):
            print(f"\n📄 템플릿 분석: {template_path}")
            print("=" * 60)
            
            try:
                with zipfile.ZipFile(template_path, 'r') as zip_file:
                    if 'word/document.xml' in zip_file.namelist():
                        xml_content = zip_file.read('word/document.xml').decode('utf-8')
                        
                        # Jinja2 변수 패턴 찾기
                        jinja2_vars = re.findall(r'\{\{\s*([^}]+)\s*\}\}', xml_content)
                        jinja2_tags = re.findall(r'\{\%\s*([^%]+)\s*\%\}', xml_content)
                        
                        print(f"📊 Jinja2 변수: {len(jinja2_vars)}개")
                        print(f"📊 Jinja2 태그: {len(jinja2_tags)}개")
                        
                        # 변수 목록 출력 (처음 10개)
                        if jinja2_vars:
                            print("\n🔍 발견된 변수들:")
                            for i, var in enumerate(jinja2_vars[:10]):
                                print(f"  {i+1}. {var}")
                            if len(jinja2_vars) > 10:
                                print(f"  ... 총 {len(jinja2_vars)}개")
                        
                        # 태그 목록 출력
                        if jinja2_tags:
                            print("\n🏷️ 발견된 태그들:")
                            for i, tag in enumerate(jinja2_tags[:5]):
                                print(f"  {i+1}. {tag}")
                            if len(jinja2_tags) > 5:
                                print(f"  ... 총 {len(jinja2_tags)}개")
                        
                        # 문제가 있는 변수 찾기
                        problematic_vars = [var for var in jinja2_vars if '<' in var or '>' in var or '/' in var]
                        if problematic_vars:
                            print(f"\n⚠️ 문제가 있는 변수들:")
                            for var in problematic_vars:
                                print(f"  - {var}")
                        
                        # 텍스트 샘플 출력
                        print(f"\n📝 텍스트 샘플 (처음 300자):")
                        text_content = re.sub(r'<[^>]+>', '', xml_content)
                        print(text_content[:300] + "..." if len(text_content) > 300 else text_content)
                        
                    else:
                        print("❌ word/document.xml 파일을 찾을 수 없습니다.")
                        
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {template_path}")

def test_simple_render():
    """간단한 렌더링 테스트"""
    print("\n🧪 간단한 렌더링 테스트")
    print("=" * 60)
    
    try:
        from docxtpl import DocxTemplate
        
        # 템플릿 파일 경로
        template_path = "quotation-api/templates/LRQA_quotation.docx"
        
        if not os.path.exists(template_path):
            print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
            return
        
        # 템플릿 로드
        doc = DocxTemplate(template_path)
        print("✅ 템플릿 로드 성공")
        
        # 간단한 컨텍스트
        context = {
            'client_name': '테스트 회사',
            'quotation_date': '2024-01-15',
            'quotation_number': 'Q2024-001',
            'total_audit_days': 10.5,
            'total_cost': 15000000,
            'has_iso9001': True,
            'has_iso14001': True,
            'has_iso45001': False
        }
        
        print(f"📊 컨텍스트: {len(context)}개 변수")
        
        # 렌더링 시도
        try:
            doc.render(context)
            print("✅ 템플릿 렌더링 성공")
            
            # 결과 저장
            output_path = "debug_output.docx"
            doc.save(output_path)
            print(f"💾 결과 저장: {output_path}")
            
        except Exception as e:
            print(f"❌ 렌더링 실패: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🔧 템플릿 디버깅 시작")
    print("=" * 60)
    
    # 템플릿 분석
    debug_template()
    
    # 간단한 렌더링 테스트
    test_simple_render()
