#!/usr/bin/env python3
"""
MCP 테스트용 견적서 생성 스크립트
새로운 회사 데이터로 견적서를 생성합니다.
"""

import json
import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 모듈들을 직접 import
from models import (
    Organization, Site, IntegrationInputs, Options, 
    StandardType, QuoteResult, ProgramBreakdown, ComplexityLevel,
    MandayTable
)
from quote_template import generate_lrqa_quotation_docx

def load_md_tables():
    """MD 테이블 데이터 로드"""
    md_tables = [
        # ISO 9001 테이블
        MandayTable(1, 10, ComplexityLevel.SMALL, 2.0, StandardType.ISO9001),
        MandayTable(11, 25, ComplexityLevel.SMALL, 3.0, StandardType.ISO9001),
        MandayTable(26, 45, ComplexityLevel.SMALL, 4.0, StandardType.ISO9001),
        MandayTable(46, 65, ComplexityLevel.SMALL, 5.0, StandardType.ISO9001),
        MandayTable(66, 85, ComplexityLevel.SMALL, 6.0, StandardType.ISO9001),
        MandayTable(86, 125, ComplexityLevel.SMALL, 7.0, StandardType.ISO9001),
        MandayTable(126, 175, ComplexityLevel.SMALL, 8.0, StandardType.ISO9001),
        MandayTable(176, 275, ComplexityLevel.SMALL, 9.0, StandardType.ISO9001),
        MandayTable(276, 425, ComplexityLevel.SMALL, 10.0, StandardType.ISO9001),
        MandayTable(426, 625, ComplexityLevel.SMALL, 11.0, StandardType.ISO9001),
        
        # ISO 14001 테이블
        MandayTable(1, 10, ComplexityLevel.LOW, 2.0, StandardType.ISO14001),
        MandayTable(11, 25, ComplexityLevel.LOW, 3.0, StandardType.ISO14001),
        MandayTable(26, 45, ComplexityLevel.LOW, 4.0, StandardType.ISO14001),
        MandayTable(46, 65, ComplexityLevel.LOW, 5.0, StandardType.ISO14001),
        MandayTable(66, 85, ComplexityLevel.LOW, 6.0, StandardType.ISO14001),
        MandayTable(86, 125, ComplexityLevel.LOW, 7.0, StandardType.ISO14001),
        MandayTable(126, 175, ComplexityLevel.LOW, 8.0, StandardType.ISO14001),
        MandayTable(176, 275, ComplexityLevel.LOW, 9.0, StandardType.ISO14001),
        MandayTable(276, 425, ComplexityLevel.LOW, 10.0, StandardType.ISO14001),
        MandayTable(426, 625, ComplexityLevel.LOW, 11.0, StandardType.ISO14001),
        
        # ISO 45001 테이블
        MandayTable(1, 10, ComplexityLevel.LOW, 2.0, StandardType.ISO45001),
        MandayTable(11, 25, ComplexityLevel.LOW, 3.0, StandardType.ISO45001),
        MandayTable(26, 45, ComplexityLevel.LOW, 4.0, StandardType.ISO45001),
        MandayTable(46, 65, ComplexityLevel.LOW, 5.0, StandardType.ISO45001),
        MandayTable(66, 85, ComplexityLevel.LOW, 6.0, StandardType.ISO45001),
        MandayTable(86, 125, ComplexityLevel.LOW, 7.0, StandardType.ISO45001),
        MandayTable(126, 175, ComplexityLevel.LOW, 8.0, StandardType.ISO45001),
        MandayTable(176, 275, ComplexityLevel.LOW, 9.0, StandardType.ISO45001),
        MandayTable(276, 425, ComplexityLevel.LOW, 10.0, StandardType.ISO45001),
        MandayTable(426, 625, ComplexityLevel.LOW, 11.0, StandardType.ISO45001),
    ]
    return md_tables

def calculate_enp(site: Site) -> float:
    """ENP 계산"""
    base_enp = site.total_headcount + site.contractor_count
    part_time_adjustment = site.part_time_count * 0.5  # 50% 감축
    shift_adjustment = site.shift_workers * 0.5  # 50% 가산
    seasonal_adjustment = site.seasonal_factor
    repetitive_adjustment = 0.9 if site.repetitive_process else 1.0  # 10% 감축
    
    enp = (base_enp - part_time_adjustment + shift_adjustment) * seasonal_adjustment * repetitive_adjustment
    return max(enp, 1.0)  # 최소 1명

def find_manday_table(enp: float, standard: StandardType, md_tables: list) -> MandayTable:
    """ENP와 표준에 맞는 MD 테이블 찾기"""
    for table in md_tables:
        if (table.standard_type == standard and 
            table.enp_min <= enp <= table.enp_max):
            return table
    
    # 기본값 반환 (가장 큰 테이블)
    max_table = max([t for t in md_tables if t.standard_type == standard], 
                   key=lambda x: x.enp_max, default=None)
    return max_table

def calculate_audit_days(enp: float, standard: StandardType, md_tables: list, options: Options) -> ProgramBreakdown:
    """심사일수 계산"""
    table = find_manday_table(enp, standard, md_tables)
    
    if not table:
        raise ValueError(f"ENP {enp}에 해당하는 {standard.value} 테이블을 찾을 수 없습니다")
    
    # Stage2 기준일수
    stage2_days = table.stage2_days
    
    # Stage1 = Stage2 * 30%
    stage1_days = stage2_days * 0.3 if options.stage1 else 0.0
    
    # Surveillance = Stage2 * 60%
    surveillance_days = stage2_days * 0.6 if options.surveillance else 0.0
    
    # Recert = Stage2 * 100%
    recert_days = stage2_days * 1.0 if options.recert else 0.0
    
    # 0.5일 단위로 라운딩
    stage1_days = round(stage1_days * 2) / 2
    stage2_days = round(stage2_days * 2) / 2
    surveillance_days = round(surveillance_days * 2) / 2
    recert_days = round(recert_days * 2) / 2
    
    return ProgramBreakdown(
        standard=standard,
        stage1_days=stage1_days,
        stage2_days=stage2_days,
        surveillance_days=surveillance_days,
        recert_days=recert_days,
        complexity=table.complexity,
        enp=int(enp)
    )

def generate_mcp_test_quotation():
    """MCP 테스트용 견적서 생성"""
    print("🚀 MCP 테스트 견적서 생성 시작")
    print("="*50)
    
    # MD 테이블 로드
    md_tables = load_md_tables()
    print(f"✅ MD 테이블 로드: {len(md_tables)}개 항목")
    
    # MCP 테스트 데이터 생성
    test_data = {
        "client_name": "MCP 테스트 주식회사",
        "client_name_en": "MCP Test Corporation",
        "standards": ["ISO9001", "ISO14001", "ISO45001"],
        "sites": [
            {
                "name": "본사",
                "address": "서울특별시 강남구 테헤란로 456",
                "standards": ["ISO9001", "ISO14001", "ISO45001"],
                "total_headcount": 200,
                "part_time_count": 20,
                "contractor_count": 15,
                "shift_workers": 30,
                "seasonal_factor": 1.0,
                "repetitive_process": False,
                "remote_audit_ratio": 0.0
            },
            {
                "name": "인천공장",
                "address": "인천광역시 연수구 송도동 789",
                "standards": ["ISO9001", "ISO14001"],
                "total_headcount": 120,
                "part_time_count": 10,
                "contractor_count": 8,
                "shift_workers": 20,
                "seasonal_factor": 1.0,
                "repetitive_process": True,
                "remote_audit_ratio": 0.0
            }
        ],
        "integration": {
            "is_integrated": True,
            "integration_level": 0.8,
            "shared_management_system": True,
            "common_processes": True,
            "same_audit_team": True
        },
        "options": {
            "stage1": True,
            "stage2": True,
            "surveillance": True,
            "recert": False,
            "remote_audit_ratio": 0.0,
            "day_rate": 1450000.0,
            "vat_rate": 0.1
        }
    }
    
    # 표준 변환
    standards = [StandardType(std) for std in test_data.get('standards', [])]
    
    # 사업장 변환
    sites = []
    for site_data in test_data.get('sites', []):
        site_standards = [StandardType(std) for std in site_data.get('standards', [])]
        site = Site(
            name=site_data['name'],
            address=site_data.get('address', ''),
            standards=site_standards,
            total_headcount=site_data.get('total_headcount', 0),
            part_time_count=site_data.get('part_time_count', 0),
            contractor_count=site_data.get('contractor_count', 0),
            shift_workers=site_data.get('shift_workers', 0),
            seasonal_factor=site_data.get('seasonal_factor', 1.0),
            repetitive_process=site_data.get('repetitive_process', False),
            remote_audit_ratio=site_data.get('remote_audit_ratio', 0.0)
        )
        sites.append(site)
    
    # 통합심사 정보
    integration_data = test_data.get('integration', {})
    integration = IntegrationInputs(
        is_integrated=integration_data.get('is_integrated', False),
        integration_level=integration_data.get('integration_level', 0.0),
        shared_management_system=integration_data.get('shared_management_system', False),
        common_processes=integration_data.get('common_processes', False),
        same_audit_team=integration_data.get('same_audit_team', False)
    )
    
    # 옵션
    options_data = test_data.get('options', {})
    options = Options(
        stage1=options_data.get('stage1', True),
        stage2=options_data.get('stage2', True),
        surveillance=options_data.get('surveillance', True),
        recert=options_data.get('recert', False),
        remote_audit_ratio=options_data.get('remote_audit_ratio', 0.0),
        day_rate=options_data.get('day_rate', 1450000.0),
        vat_rate=options_data.get('vat_rate', 0.1)
    )
    
    # Organization 생성
    organization = Organization(
        client_name=test_data['client_name'],
        client_name_en=test_data.get('client_name_en'),
        sites=sites,
        standards=standards,
        integration=integration,
        options=options
    )
    
    print(f"🏢 고객사: {organization.client_name}")
    print(f"📋 적용 표준: {[std.value for std in organization.standards]}")
    print(f"🏭 사업장 수: {len(organization.sites)}")
    
    # 각 사업장별로 견적 계산
    all_breakdowns = []
    total_days = 0.0
    
    for i, site in enumerate(organization.sites, 1):
        print(f"\n📊 사업장 {i}: {site.name}")
        print(f"  - 총 직원수: {site.total_headcount}")
        print(f"  - 파트타임: {site.part_time_count}")
        print(f"  - 외주: {site.contractor_count}")
        print(f"  - 교대근무: {site.shift_workers}")
        
        # ENP 계산
        enp = calculate_enp(site)
        print(f"  - 계산된 ENP: {enp:.1f}명")
        
        # 표준별 심사일수 계산
        site_breakdowns = []
        for standard in site.standards:
            breakdown = calculate_audit_days(enp, standard, md_tables, options)
            site_breakdowns.append(breakdown)
            all_breakdowns.append(breakdown)
            total_days += breakdown.total_days
            
            print(f"  {standard.value}: {breakdown.total_days}일 (Stage1: {breakdown.stage1_days}, Stage2: {breakdown.stage2_days}, Surveillance: {breakdown.surveillance_days})")
    
    # 할인 계산
    integration_discount = integration.get_integration_discount()
    remote_discount = min(options.remote_audit_ratio * 0.1, 0.1)
    total_discount = min(integration_discount + remote_discount, 0.15)
    
    print(f"\n💰 할인 계산:")
    print(f"  - 통합심사 할인: {integration_discount*100:.1f}%")
    print(f"  - 원격심사 할인: {remote_discount*100:.1f}%")
    print(f"  - 총 할인: {total_discount*100:.1f}%")
    
    # 비용 계산
    subtotal_cost = total_days * options.day_rate
    vat_amount = subtotal_cost * options.vat_rate
    total_cost = subtotal_cost + vat_amount
    
    print(f"\n💵 비용 계산:")
    print(f"  - 총 심사일수: {total_days} mandays")
    print(f"  - 1 manday 단가: ₩{options.day_rate:,.0f}")
    print(f"  - 서브토탈: ₩{subtotal_cost:,.0f}")
    print(f"  - VAT ({options.vat_rate*100:.1f}%): ₩{vat_amount:,.0f}")
    print(f"  - 총 견적 금액: ₩{total_cost:,.0f}")
    
    # 견적 결과 생성
    result = QuoteResult(
        organization=organization,
        breakdowns=all_breakdowns,
        total_audit_days=total_days,
        subtotal_cost=subtotal_cost,
        vat_amount=vat_amount,
        total_cost=total_cost,
        created_at=datetime.now().isoformat()
    )
    
    # test_results 폴더에 Word 견적서 생성
    test_results_dir = "../test_results"
    if not os.path.exists(test_results_dir):
        os.makedirs(test_results_dir)
    
    # 파일명 생성 (타임스탬프 포함)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"MCP_테스트_견적서_{timestamp}.docx"
    output_path = os.path.join(test_results_dir, output_filename)
    
    print(f"\n📄 Word 견적서 생성 중: {output_path}")
    
    try:
        # Word 견적서 생성
        generated_file = generate_lrqa_quotation_docx(result, output_path)
        
        print(f"✅ Word 견적서 생성 완료!")
        print(f"📄 파일 경로: {generated_file}")
        
        # 파일 크기 출력
        if os.path.exists(generated_file):
            file_size = os.path.getsize(generated_file)
            print(f"📊 파일 크기: {file_size:,} bytes")
        
        return generated_file
        
    except Exception as e:
        print(f"❌ Word 견적서 생성 실패: {str(e)}")
        return None

if __name__ == '__main__':
    generate_mcp_test_quotation()
