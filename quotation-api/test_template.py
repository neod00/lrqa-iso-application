#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jinja2 템플릿 테스트 스크립트
"""

import os
import sys
from datetime import datetime
from simple_server import CustomDocxTemplate, format_currency, format_number, format_date

def test_template():
    """템플릿 렌더링 테스트"""
    
    # 템플릿 경로
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'LRQA_quotation.docx')
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return False
    
    print(f"📄 템플릿 파일: {template_path}")
    
    try:
        # CustomDocxTemplate 로드
        doc = CustomDocxTemplate(template_path)
        print("✅ CustomDocxTemplate 로드 성공")
        
        # 테스트 데이터 생성
        test_context = {
            # 기본 정보
            'client_name': '테스트 회사',
            'client_name_en': 'Test Company Ltd.',
            'client_address': '서울시 강남구 테헤란로 123',
            'quotation_date': '2024-01-15',
            'quotation_number': 'Q2024-001',
            'standards': 'ISO 9001, ISO 14001',
            'standards_text': 'ISO 9001 품질경영시스템, ISO 14001 환경경영시스템',
            'total_employees': 150,
            'total_sites': 1,
            
            # ISO 표준 선택 여부
            'has_iso9001': True,
            'has_iso14001': True,
            'has_iso45001': False,
            
            # 기본 계산값
            'total_cost': 15000000,
            'vat_amount': 1500000,
            'final_cost': 16500000,
            'total_audit_days': 12.5,
            'day_rate': 1200000,
            
            # ISO 9001 관련
            'iso9001_stage1_days': 2.0,
            'iso9001_stage2_days': 3.0,
            'iso9001_stage1_2_days': 5.0,
            'iso9001_surveillance_days': 2.0,
            'iso9001_stage1_2_cost': 6000000,
            
            # ISO 14001 관련
            'iso14001_stage1_days': 1.5,
            'iso14001_stage2_days': 2.5,
            'iso14001_stage1_2_days': 4.0,
            'iso14001_surveillance_days': 1.5,
            'iso14001_stage1_2_cost': 4800000,
            
            # ISO 45001 관련 (선택되지 않음)
            'iso45001_stage1_days': 0,
            'iso45001_stage2_days': 0,
            'iso45001_stage1_2_days': 0,
            'iso45001_surveillance_days': 0,
            'iso45001_stage1_2_cost': 0,
            
            # 기타 비용
            'travel_expense': 500000,
            'total_cost_with_travel': 15500000,
            
            # breakdowns 데이터
            'breakdowns': [
                {
                    'standard': 'ISO9001',
                    'stage1_days': 2.0,
                    'stage2_days': 3.0,
                    'surveillance_days': 2.0,
                    'stage1_2_cost': 6000000
                },
                {
                    'standard': 'ISO14001',
                    'stage1_days': 1.5,
                    'stage2_days': 2.5,
                    'surveillance_days': 1.5,
                    'stage1_2_cost': 4800000
                }
            ],
            
            # 디버깅 정보
            'debug_info': {
                'api_success': True,
                'calculation_method': 'core_brain',
                'generated_at': datetime.now().isoformat()
            }
        }
        
        print(f"📊 테스트 컨텍스트: {len(test_context)}개 변수")
        
        # 필터 테스트
        print("\n🔧 필터 테스트:")
        print(f"format_currency(1500000): {format_currency(1500000)}")
        print(f"format_number(1500): {format_number(1500)}")
        print(f"format_date('2024-01-15'): {format_date('2024-01-15')}")
        
        # 템플릿 렌더링 테스트
        print("\n🎯 템플릿 렌더링 테스트:")
        if doc.render_with_error_handling(test_context):
            print("✅ 템플릿 렌더링 성공!")
            
            # 결과 파일 저장
            output_path = os.path.join(os.path.dirname(__file__), 'test_output.docx')
            doc.save(output_path)
            print(f"💾 결과 파일 저장: {output_path}")
            return True
        else:
            print("❌ 템플릿 렌더링 실패")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_filters():
    """필터 함수들 개별 테스트"""
    print("\n🧪 필터 함수 테스트:")
    
    # format_currency 테스트
    test_cases = [
        (1500000, "1,500,000원"),
        (0, "0원"),
        (None, "0원"),
        ("invalid", "invalid원")
    ]
    
    for value, expected in test_cases:
        result = format_currency(value)
        status = "✅" if result == expected else "❌"
        print(f"{status} format_currency({value}) = {result} (예상: {expected})")
    
    # format_number 테스트
    test_cases = [
        (1500, "1,500"),
        (0, "0"),
        (None, "0"),
        ("invalid", "invalid")
    ]
    
    for value, expected in test_cases:
        result = format_number(value)
        status = "✅" if result == expected else "❌"
        print(f"{status} format_number({value}) = {result} (예상: {expected})")

if __name__ == "__main__":
    print("🚀 Jinja2 템플릿 테스트 시작")
    print("=" * 50)
    
    # 필터 테스트
    test_filters()
    
    # 템플릿 테스트
    success = test_template()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 모든 테스트 통과!")
    else:
        print("💥 일부 테스트 실패")
        sys.exit(1)
