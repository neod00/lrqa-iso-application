#!/usr/bin/env python3
"""
아이폰주식회사 전체 프로세스 테스트
신청서 작성부터 견적서 생성까지 MCP 테스트
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

def load_iphone_company_data():
    """아이폰주식회사 데이터 로드"""
    data = {
        "client_name": "아이폰 주식회사",
        "client_name_en": "iPhone Corporation Ltd.",
        "standards": ["ISO9001", "ISO14001", "ISO45001"],
        "sites": [
            {
                "name": "본사",
                "address": "서울시 광진구 중곡동 45",
                "standards": ["ISO9001", "ISO14001", "ISO45001"],
                "total_headcount": 590,
                "part_time_count": 50,
                "contractor_count": 30,
                "shift_workers": 100,
                "seasonal_factor": 1.0,
                "repetitive_process": True,
                "remote_audit_ratio": 0.0
            },
            {
                "name": "부산공장",
                "address": "부산시 해운대구 센텀중앙로 123",
                "standards": ["ISO9001", "ISO14001", "ISO45001"],
                "total_headcount": 200,
                "part_time_count": 20,
                "contractor_count": 15,
                "shift_workers": 80,
                "seasonal_factor": 1.2,
                "repetitive_process": True,
                "remote_audit_ratio": 0.0
            },
            {
                "name": "대구지점",
                "address": "대구시 수성구 동대구로 456",
                "standards": ["ISO9001"],
                "total_headcount": 50,
                "part_time_count": 5,
                "contractor_count": 3,
                "shift_workers": 0,
                "seasonal_factor": 1.0,
                "repetitive_process": False,
                "remote_audit_ratio": 0.3
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
    return data

def create_md_tables():
    """MD 테이블 생성"""
    tables = []
    
    # ISO 9001 테이블 (QMS)
    qms_data = [
        (1, 10, ComplexityLevel.SMALL, 2.0),
        (11, 25, ComplexityLevel.SMALL, 3.0),
        (26, 45, ComplexityLevel.SMALL, 4.0),
        (46, 65, ComplexityLevel.SMALL, 5.0),
        (66, 85, ComplexityLevel.SMALL, 6.0),
        (86, 125, ComplexityLevel.SMALL, 7.0),
        (126, 175, ComplexityLevel.SMALL, 8.0),
        (176, 275, ComplexityLevel.SMALL, 9.0),
        (276, 425, ComplexityLevel.SMALL, 10.0),
        (426, 625, ComplexityLevel.SMALL, 11.0),
        (626, 875, ComplexityLevel.SMALL, 12.0),
        (876, 1175, ComplexityLevel.SMALL, 13.0),
        (1176, 1550, ComplexityLevel.SMALL, 14.0),
        (1551, 2025, ComplexityLevel.SMALL, 15.0),
        (2026, 2675, ComplexityLevel.SMALL, 16.0),
        (2676, 3500, ComplexityLevel.SMALL, 17.0),
        (3501, 4625, ComplexityLevel.SMALL, 18.0),
        (4626, 6100, ComplexityLevel.SMALL, 19.0),
        (6101, 8075, ComplexityLevel.SMALL, 20.0),
        (8076, 10700, ComplexityLevel.SMALL, 21.0),
        (10701, 14200, ComplexityLevel.SMALL, 22.0),
        (14201, 18800, ComplexityLevel.SMALL, 23.0),
        (18801, 25000, ComplexityLevel.SMALL, 24.0),
    ]
    
    for enp_min, enp_max, complexity, stage2_days in qms_data:
        tables.append(MandayTable(enp_min, enp_max, complexity, stage2_days, StandardType.ISO9001))
    
    # ISO 14001 테이블 (EMS)
    ems_data = [
        (1, 10, ComplexityLevel.LOW, 2.0),
        (11, 25, ComplexityLevel.LOW, 3.0),
        (26, 45, ComplexityLevel.LOW, 4.0),
        (46, 65, ComplexityLevel.LOW, 5.0),
        (66, 85, ComplexityLevel.LOW, 6.0),
        (86, 125, ComplexityLevel.LOW, 7.0),
        (126, 175, ComplexityLevel.LOW, 8.0),
        (176, 275, ComplexityLevel.LOW, 9.0),
        (276, 425, ComplexityLevel.LOW, 10.0),
        (426, 625, ComplexityLevel.LOW, 11.0),
        (626, 875, ComplexityLevel.LOW, 12.0),
        (876, 1175, ComplexityLevel.LOW, 13.0),
        (1176, 1550, ComplexityLevel.LOW, 14.0),
        (1551, 2025, ComplexityLevel.LOW, 15.0),
        (2026, 2675, ComplexityLevel.LOW, 16.0),
        (2676, 3500, ComplexityLevel.LOW, 17.0),
        (3501, 4625, ComplexityLevel.LOW, 18.0),
        (4626, 6100, ComplexityLevel.LOW, 19.0),
        (6101, 8075, ComplexityLevel.LOW, 20.0),
        (8076, 10700, ComplexityLevel.LOW, 21.0),
        (10701, 14200, ComplexityLevel.LOW, 22.0),
        (14201, 18800, ComplexityLevel.LOW, 23.0),
        (18801, 25000, ComplexityLevel.LOW, 24.0),
    ]
    
    for enp_min, enp_max, complexity, stage2_days in ems_data:
        tables.append(MandayTable(enp_min, enp_max, complexity, stage2_days, StandardType.ISO14001))
    
    # ISO 45001 테이블 (OHSMS)
    ohsms_data = [
        (1, 10, ComplexityLevel.LOW, 2.0),
        (11, 25, ComplexityLevel.LOW, 3.0),
        (26, 45, ComplexityLevel.LOW, 4.0),
        (46, 65, ComplexityLevel.LOW, 5.0),
        (66, 85, ComplexityLevel.LOW, 6.0),
        (86, 125, ComplexityLevel.LOW, 7.0),
        (126, 175, ComplexityLevel.LOW, 8.0),
        (176, 275, ComplexityLevel.LOW, 9.0),
        (276, 425, ComplexityLevel.LOW, 10.0),
        (426, 625, ComplexityLevel.LOW, 11.0),
        (626, 875, ComplexityLevel.LOW, 12.0),
        (876, 1175, ComplexityLevel.LOW, 13.0),
        (1176, 1550, ComplexityLevel.LOW, 14.0),
        (1551, 2025, ComplexityLevel.LOW, 15.0),
        (2026, 2675, ComplexityLevel.LOW, 16.0),
        (2676, 3500, ComplexityLevel.LOW, 17.0),
        (3501, 4625, ComplexityLevel.LOW, 18.0),
        (4626, 6100, ComplexityLevel.LOW, 19.0),
        (6101, 8075, ComplexityLevel.LOW, 20.0),
        (8076, 10700, ComplexityLevel.LOW, 21.0),
        (10701, 14200, ComplexityLevel.LOW, 22.0),
        (14201, 18800, ComplexityLevel.LOW, 23.0),
        (18801, 25000, ComplexityLevel.LOW, 24.0),
    ]
    
    for enp_min, enp_max, complexity, stage2_days in ohsms_data:
        tables.append(MandayTable(enp_min, enp_max, complexity, stage2_days, StandardType.ISO45001))
    
    return tables

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

def simulate_application_process():
    """신청서 작성 프로세스 시뮬레이션"""
    print("📝 신청서 작성 프로세스 시뮬레이션")
    print("="*60)
    
    # 1단계: 회사 정보 입력
    print("1️⃣ 회사 정보 입력")
    print("-" * 30)
    print("✅ 회사명: 아이폰 주식회사")
    print("✅ 영문명: iPhone Corporation Ltd.")
    print("✅ 본사 주소: 서울시 광진구 중곡동 45")
    print("✅ 웹사이트: https://www.iphone-corp.com")
    print("✅ 사업자등록번호: 123-45-67890")
    print("✅ 대표 전화번호: 02-1234-5678")
    print("✅ 대표 이메일: contact@iphone-corp.com")
    print()
    
    # 2단계: ISO 표준 선택
    print("2️⃣ ISO 표준 선택")
    print("-" * 30)
    print("✅ ISO 9001:2015 (품질경영시스템)")
    print("✅ ISO 14001:2015 (환경경영시스템)")
    print("✅ ISO 45001:2018 (직업건강안전경영시스템)")
    print("✅ 통합심사 진행: 예")
    print()
    
    # 3단계: 사업장 정보 입력
    print("3️⃣ 사업장 정보 입력")
    print("-" * 30)
    print("✅ 본사 (서울시 광진구)")
    print("   - 총 직원수: 590명")
    print("   - 파트타임: 50명")
    print("   - 외주: 30명")
    print("   - 교대근무: 100명")
    print("   - 반복공정: 예")
    print()
    print("✅ 부산공장 (부산시 해운대구)")
    print("   - 총 직원수: 200명")
    print("   - 파트타임: 20명")
    print("   - 외주: 15명")
    print("   - 교대근무: 80명")
    print("   - 계절성 가중치: 1.2")
    print("   - 반복공정: 예")
    print()
    print("✅ 대구지점 (대구시 수성구)")
    print("   - 총 직원수: 50명")
    print("   - 파트타임: 5명")
    print("   - 외주: 3명")
    print("   - 교대근무: 0명")
    print("   - 원격심사 비율: 30%")
    print("   - 적용 표준: ISO 9001만")
    print()
    
    # 4단계: 담당자 정보 입력
    print("4️⃣ 담당자 정보 입력")
    print("-" * 30)
    print("✅ 담당자: 김아이폰")
    print("✅ 부서: 품질경영팀")
    print("✅ 직급: 팀장")
    print("✅ 이메일: kim.iphone@iphone-corp.com")
    print("✅ 전화번호: 02-1234-5679")
    print("✅ 휴대폰: 010-1234-5678")
    print()
    
    # 5단계: 통합심사 정보
    print("5️⃣ 통합심사 정보")
    print("-" * 30)
    print("✅ 통합심사 진행: 예")
    print("✅ 공통 경영시스템: 예")
    print("✅ 공통 프로세스: 예")
    print("✅ 동일 심사팀: 예")
    print("✅ 통합 수준: 80%")
    print()
    
    # 6단계: 심사 옵션 선택
    print("6️⃣ 심사 옵션 선택")
    print("-" * 30)
    print("✅ 1단계 심사: 예")
    print("✅ 2단계 심사: 예")
    print("✅ 감시심사: 예")
    print("✅ 갱신심사: 아니오")
    print("✅ 원격심사: 아니오")
    print()
    
    # 7단계: 데이터 수집 동의
    print("7️⃣ 데이터 수집 동의")
    print("-" * 30)
    print("✅ LRQA 데이터 프로세스 동의: 예")
    print("✅ 서명: 김아이폰")
    print("✅ 날짜: 2025-01-10")
    print()
    
    print("✅ 신청서 작성 완료!")
    print()

def main():
    """메인 함수"""
    print("🚀 아이폰주식회사 전체 프로세스 MCP 테스트")
    print("="*70)
    
    # 1. 신청서 작성 프로세스 시뮬레이션
    simulate_application_process()
    
    # 2. 데이터 로드
    print("📄 신청서 데이터 로딩...")
    sample_data = load_iphone_company_data()
    
    # 3. MD 테이블 생성
    print("📊 MD 테이블 생성...")
    md_tables = create_md_tables()
    print(f"✅ MD 테이블 로드: {len(md_tables)}개 항목")
    
    # 4. Organization 객체 생성
    print("🔧 Organization 객체 생성...")
    
    # 표준 변환
    standards = [StandardType(std) for std in sample_data.get('standards', [])]
    
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
    
    # 통합심사 정보
    integration_data = sample_data.get('integration', {})
    integration = IntegrationInputs(
        is_integrated=integration_data.get('is_integrated', False),
        integration_level=integration_data.get('integration_level', 0.0),
        shared_management_system=integration_data.get('shared_management_system', False),
        common_processes=integration_data.get('common_processes', False),
        same_audit_team=integration_data.get('same_audit_team', False)
    )
    
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
    
    organization = Organization(
        client_name=sample_data['client_name'],
        client_name_en=sample_data.get('client_name_en'),
        sites=sites,
        standards=standards,
        integration=integration,
        options=options
    )
    
    print(f"✅ 고객사: {organization.client_name}")
    print(f"✅ 적용 표준: {[std.value for std in organization.standards]}")
    print(f"✅ 사업장 수: {len(organization.sites)}")
    
    # 5. 사업장별 ENP 계산
    print(f"\n👥 사업장별 ENP 계산:")
    print("-" * 50)
    
    site_enps = []
    for i, site in enumerate(organization.sites, 1):
        enp = calculate_enp(site)
        site_enps.append(enp)
        print(f"사업장 {i}: {site.name}")
        print(f"  - 총 직원수: {site.total_headcount}")
        print(f"  - 파트타임: {site.part_time_count}")
        print(f"  - 외주: {site.contractor_count}")
        print(f"  - 교대근무: {site.shift_workers}")
        print(f"  - 계절성 가중치: {site.seasonal_factor}")
        print(f"  - 반복공정: {site.repetitive_process}")
        print(f"  - 원격심사 비율: {site.remote_audit_ratio*100:.1f}%")
        print(f"  - 계산된 ENP: {enp:.1f}명")
        print()
    
    # 6. 표준별 심사일수 계산
    print(f"📊 표준별 심사일수 계산:")
    print("-" * 50)
    
    breakdowns = []
    total_days = 0.0
    
    for standard in organization.standards:
        # 모든 사업장의 ENP 합계
        total_enp = sum(site_enps)
        
        breakdown = calculate_audit_days(total_enp, standard, md_tables, options)
        breakdowns.append(breakdown)
        total_days += breakdown.total_days
        
        print(f"{standard.value}:")
        print(f"  - 복잡도: {breakdown.complexity.value}")
        print(f"  - 총 ENP: {breakdown.enp}명")
        print(f"  - Stage1: {breakdown.stage1_days}일")
        print(f"  - Stage2: {breakdown.stage2_days}일")
        print(f"  - Surveillance: {breakdown.surveillance_days}일")
        print(f"  - Recert: {breakdown.recert_days}일")
        print(f"  - 총계: {breakdown.total_days}일")
        print()
    
    # 7. 할인 계산
    integration_discount = integration.get_integration_discount()
    remote_discount = min(options.remote_audit_ratio * 0.1, 0.1)
    total_discount = min(integration_discount + remote_discount, 0.15)
    
    print(f"💰 할인 계산:")
    print(f"  - 통합심사 할인: {integration_discount*100:.1f}%")
    print(f"  - 원격심사 할인: {remote_discount*100:.1f}%")
    print(f"  - 총 할인: {total_discount*100:.1f}%")
    
    # 8. 비용 계산
    subtotal_cost = total_days * options.day_rate
    vat_amount = subtotal_cost * options.vat_rate
    total_cost = subtotal_cost + vat_amount
    
    print(f"\n💵 최종 견적서:")
    print("="*70)
    print(f"고객사: {organization.client_name}")
    print(f"영문명: {organization.client_name_en}")
    print(f"적용 표준: {', '.join([std.value for std in organization.standards])}")
    print(f"사업장 수: {len(organization.sites)}개")
    print(f"총 ENP: {sum(site_enps):.1f}명")
    print(f"총 심사일수: {total_days} mandays")
    print(f"1 manday 단가: ₩{options.day_rate:,.0f}")
    print(f"서브토탈: ₩{subtotal_cost:,.0f}")
    print(f"VAT ({options.vat_rate*100:.1f}%): ₩{vat_amount:,.0f}")
    print(f"총 견적 금액: ₩{total_cost:,.0f}")
    print("="*70)
    
    # 9. 견적 결과 생성
    result = QuoteResult(
        organization=organization,
        breakdowns=breakdowns,
        total_audit_days=total_days,
        subtotal_cost=subtotal_cost,
        vat_amount=vat_amount,
        total_cost=total_cost,
        created_at=datetime.now().isoformat()
    )
    
    print(f"\n🎉 전체 프로세스 완료!")
    print(f"📄 견적서가 성공적으로 생성되었습니다!")
    print(f"📧 이메일로 견적서가 발송됩니다: kim.iphone@iphone-corp.com")
    
    return result

if __name__ == '__main__':
    main()

