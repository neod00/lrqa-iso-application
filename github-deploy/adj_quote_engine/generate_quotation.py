#!/usr/bin/env python3
"""
견적서 Word 문서 생성 스크립트
Netlify Functions에서 호출되어 실제 .docx 파일을 생성합니다.
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

# adj_quote_engine 모듈 import
sys.path.append(os.path.dirname(__file__))

try:
    from adj_quote_engine.models import QuoteResult, Organization, Site, StandardType, ProgramBreakdown
    from adj_quote_engine.quote_template import LRQAQuotationTemplate
except ImportError as e:
    print(f"모듈 import 오류: {e}")
    sys.exit(1)

def create_quote_result_from_data(data):
    """JSON 데이터를 QuoteResult 객체로 변환"""
    try:
        # 표준 타입 변환
        standards = []
        for std in data.get('standards', []):
            if std == 'ISO 9001':
                standards.append(StandardType.ISO9001)
            elif std == 'ISO 14001':
                standards.append(StandardType.ISO14001)
            elif std == 'ISO 45001':
                standards.append(StandardType.ISO45001)
            else:
                standards.append(StandardType.ISO9001)  # 기본값
        
        # 사업장 정보 생성
        sites = []
        for site_data in data.get('sites', []):
            site = Site(
                name=site_data.get('name', '본사'),
                address=site_data.get('address', '서울시 강남구'),
                standards=standards,
                total_headcount=site_data.get('total_headcount', data.get('total_employees', 30))
            )
            sites.append(site)
        
        # 조직 정보 생성
        organization = Organization(
            client_name=data.get('company_name', '알 수 없음'),
            client_name_en=data.get('company_name_en', data.get('company_name', 'Unknown')),
            contact_name=data.get('contact_name', '알 수 없음'),
            contact_email=data.get('contact_email', 'unknown@example.com'),
            contact_phone=data.get('contact_phone', '010-0000-0000'),
            standards=standards,
            sites=sites
        )
        
        # 견적서 결과 생성
        quote_result = QuoteResult(
            organization=organization,
            total_audit_days=3,  # 기본값
            total_cost=data.get('total_cost', 1800000),
            breakdowns=[]  # 간단한 버전이므로 빈 리스트
        )
        
        return quote_result
        
    except Exception as e:
        print(f"QuoteResult 생성 오류: {e}")
        return None

def main():
    if len(sys.argv) != 3:
        print("사용법: python generate_quotation.py <input_json> <output_docx>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # JSON 데이터 로드
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"입력 데이터 로드 완료: {input_file}")
        
        # QuoteResult 객체 생성
        quote_result = create_quote_result_from_data(data)
        if not quote_result:
            print("QuoteResult 객체 생성 실패")
            sys.exit(1)
        
        # Word 문서 생성
        template_generator = LRQAQuotationTemplate()
        result_path = template_generator.generate_quotation_docx(quote_result, output_file)
        
        print(f"Word 문서 생성 완료: {result_path}")
        
        # 파일 존재 확인
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"생성된 파일 크기: {file_size} bytes")
        else:
            print("파일이 생성되지 않았습니다!")
            sys.exit(1)
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

