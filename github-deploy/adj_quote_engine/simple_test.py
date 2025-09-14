#!/usr/bin/env python3
"""
ADJ v2.2 견적 계산 엔진 간단 테스트
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
    StandardType, QuoteResult, ProgramBreakdown, ComplexityLevel
)

def test_basic_models():
    """기본 모델 테스트"""
    print("🧪 기본 모델 테스트 시작")
    print("="*40)
    
    # StandardType 테스트
    print("📋 StandardType 테스트:")
    for std in StandardType:
        print(f"  - {std.value}")
    
    # Site 모델 테스트
    print("\n🏢 Site 모델 테스트:")
    site = Site(
        name="테스트 사업장",
        address="서울시 강남구",
        standards=[StandardType.ISO9001, StandardType.ISO14001],
        total_headcount=100,
        part_time_count=10,
        contractor_count=5,
        shift_workers=20
    )
    print(f"  - 사업장명: {site.name}")
    print(f"  - 주소: {site.address}")
    print(f"  - 표준: {[std.value for std in site.standards]}")
    print(f"  - 총 직원수: {site.total_headcount}")
    print(f"  - 파트타임: {site.part_time_count}")
    print(f"  - 외주: {site.contractor_count}")
    print(f"  - 교대근무: {site.shift_workers}")
    
    # IntegrationInputs 테스트
    print("\n🔗 IntegrationInputs 테스트:")
    integration = IntegrationInputs(
        is_integrated=True,
        shared_management_system=True,
        common_processes=True,
        same_audit_team=True
    )
    discount = integration.get_integration_discount()
    print(f"  - 통합심사: {integration.is_integrated}")
    print(f"  - 할인율: {discount*100:.1f}%")
    
    # Options 테스트
    print("\n⚙️ Options 테스트:")
    options = Options(
        stage1=True,
        stage2=True,
        surveillance=True,
        recert=False,
        day_rate=1300000.0,
        vat_rate=0.1
    )
    print(f"  - Stage1: {options.stage1}")
    print(f"  - Stage2: {options.stage2}")
    print(f"  - Surveillance: {options.surveillance}")
    print(f"  - 일당: ₩{options.day_rate:,.0f}")
    print(f"  - VAT: {options.vat_rate*100:.1f}%")
    
    # Organization 테스트
    print("\n🏛️ Organization 테스트:")
    organization = Organization(
        client_name="테스트 회사",
        client_name_en="Test Company Ltd.",
        sites=[site],
        standards=[StandardType.ISO9001, StandardType.ISO14001],
        integration=integration,
        options=options
    )
    print(f"  - 고객사: {organization.client_name}")
    print(f"  - 영문명: {organization.client_name_en}")
    print(f"  - 사업장 수: {len(organization.sites)}")
    print(f"  - 적용 표준: {[std.value for std in organization.standards]}")
    
    print("\n✅ 기본 모델 테스트 완료!")


def test_json_parsing():
    """JSON 파싱 테스트"""
    print("\n📄 JSON 파싱 테스트 시작")
    print("="*40)
    
    # 샘플 JSON 데이터
    sample_data = {
        "client_name": "ACME Corporation",
        "client_name_en": "ACME Corporation Ltd.",
        "standards": ["ISO9001", "ISO14001"],
        "sites": [
            {
                "name": "본사",
                "address": "서울시 강남구 테헤란로 123",
                "standards": ["ISO9001", "ISO14001"],
                "total_headcount": 150,
                "part_time_count": 15,
                "contractor_count": 8,
                "shift_workers": 25,
                "seasonal_factor": 1.0,
                "repetitive_process": False,
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
            "day_rate": 1300000.0,
            "vat_rate": 0.1
        }
    }
    
    try:
        # 표준 변환
        standards = [StandardType(std) for std in sample_data.get('standards', [])]
        print(f"✅ 표준 변환: {[std.value for std in standards]}")
        
        # 사업장 변환
        sites = []
        for site_data in sample_data.get('sites', []):
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
        print(f"✅ 사업장 변환: {len(sites)}개")
        
        # 통합심사 정보
        integration_data = sample_data.get('integration', {})
        integration = IntegrationInputs(
            is_integrated=integration_data.get('is_integrated', False),
            integration_level=integration_data.get('integration_level', 0.0),
            shared_management_system=integration_data.get('shared_management_system', False),
            common_processes=integration_data.get('common_processes', False),
            same_audit_team=integration_data.get('same_audit_team', False)
        )
        print(f"✅ 통합심사 변환: {integration.is_integrated}")
        
        # 옵션
        options_data = sample_data.get('options', {})
        options = Options(
            stage1=options_data.get('stage1', True),
            stage2=options_data.get('stage2', True),
            surveillance=options_data.get('surveillance', True),
            recert=options_data.get('recert', False),
            remote_audit_ratio=options_data.get('remote_audit_ratio', 0.0),
            day_rate=options_data.get('day_rate', 1300000.0),
            vat_rate=options_data.get('vat_rate', 0.1)
        )
        print(f"✅ 옵션 변환: 일당 ₩{options.day_rate:,.0f}")
        
        # Organization 생성
        organization = Organization(
            client_name=sample_data['client_name'],
            client_name_en=sample_data.get('client_name_en'),
            sites=sites,
            standards=standards,
            integration=integration,
            options=options
        )
        print(f"✅ Organization 생성: {organization.client_name}")
        
        print("\n✅ JSON 파싱 테스트 완료!")
        return organization
        
    except Exception as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return None


def test_enp_calculation(organization):
    """ENP 계산 테스트"""
    print("\n🧮 ENP 계산 테스트 시작")
    print("="*40)
    
    for i, site in enumerate(organization.sites, 1):
        print(f"사업장 {i}: {site.name}")
        print(f"  - 총 직원수: {site.total_headcount}")
        print(f"  - 파트타임: {site.part_time_count}")
        print(f"  - 외주: {site.contractor_count}")
        print(f"  - 교대근무: {site.shift_workers}")
        print(f"  - 계절성 가중치: {site.seasonal_factor}")
        print(f"  - 반복공정: {site.repetitive_process}")
        
        # ENP 계산 (간단한 버전)
        base_enp = site.total_headcount + site.contractor_count
        part_time_adjustment = site.part_time_count * 0.5  # 50% 감축
        shift_adjustment = site.shift_workers * 0.5  # 50% 가산
        seasonal_adjustment = site.seasonal_factor
        repetitive_adjustment = 0.9 if site.repetitive_process else 1.0  # 10% 감축
        
        enp = (base_enp - part_time_adjustment + shift_adjustment) * seasonal_adjustment * repetitive_adjustment
        
        print(f"  - 계산된 ENP: {enp:.1f}명")
        print()


def main():
    """메인 함수"""
    print("🚀 ADJ v2.2 견적 계산 엔진 간단 테스트")
    print("="*50)
    
    # 1. 기본 모델 테스트
    test_basic_models()
    
    # 2. JSON 파싱 테스트
    organization = test_json_parsing()
    
    if organization:
        # 3. ENP 계산 테스트
        test_enp_calculation(organization)
    
    print("\n🎉 모든 테스트 완료!")


if __name__ == '__main__':
    main()

