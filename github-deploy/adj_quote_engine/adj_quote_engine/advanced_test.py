#!/usr/bin/env python3
"""
ADJ v2.2 견적 계산 엔진 고급 테스트
MD 테이블과 실제 견적 계산 테스트
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

def test_md_tables():
    """MD 테이블 테스트"""
    print("📊 MD 테이블 테스트 시작")
    print("="*40)
    
    # MD 테이블 데이터 (간단한 버전)
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
    
    print(f"✅ MD 테이블 로드: {len(md_tables)}개 항목")
    
    # ENP별 테이블 조회 테스트
    test_enps = [50, 100, 200, 500, 1000]
    
    for enp in test_enps:
        print(f"\nENP {enp}명 테스트:")
        
        for std in [StandardType.ISO9001, StandardType.ISO14001, StandardType.ISO45001]:
            # 해당 표준과 ENP에 맞는 테이블 찾기
            matching_tables = [t for t in md_tables if t.standard_type == std and t.enp_min <= enp <= t.enp_max]
            
            if matching_tables:
                table = matching_tables[0]
                print(f"  {std.value}: {table.complexity.value} 복잡도, Stage2 {table.stage2_days}일")
            else:
                print(f"  {std.value}: 해당하는 테이블 없음")
    
    print("\n✅ MD 테이블 테스트 완료!")
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


def test_quote_calculation():
    """견적 계산 테스트"""
    print("\n🧮 견적 계산 테스트 시작")
    print("="*40)
    
    # MD 테이블 로드
    md_tables = test_md_tables()
    
    # 테스트 데이터 생성
    site = Site(
        name="테스트 본사",
        address="서울시 강남구",
        standards=[StandardType.ISO9001, StandardType.ISO14001, StandardType.ISO45001],
        total_headcount=150,
        part_time_count=15,
        contractor_count=8,
        shift_workers=25,
        seasonal_factor=1.0,
        repetitive_process=False,
        remote_audit_ratio=0.0
    )
    
    integration = IntegrationInputs(
        is_integrated=True,
        shared_management_system=True,
        common_processes=True,
        same_audit_team=True
    )
    
    options = Options(
        stage1=True,
        stage2=True,
        surveillance=True,
        recert=False,
        day_rate=1300000.0,
        vat_rate=0.1
    )
    
    organization = Organization(
        client_name="테스트 회사",
        client_name_en="Test Company Ltd.",
        sites=[site],
        standards=[StandardType.ISO9001, StandardType.ISO14001, StandardType.ISO45001],
        integration=integration,
        options=options
    )
    
    print(f"🏢 고객사: {organization.client_name}")
    print(f"📋 적용 표준: {[std.value for std in organization.standards]}")
    print(f"🏭 사업장 수: {len(organization.sites)}")
    
    # ENP 계산
    enp = calculate_enp(site)
    print(f"👥 계산된 ENP: {enp:.1f}명")
    
    # 표준별 심사일수 계산
    breakdowns = []
    total_days = 0.0
    
    print(f"\n📊 표준별 심사일수 계산:")
    print("-" * 50)
    
    for standard in organization.standards:
        breakdown = calculate_audit_days(enp, standard, md_tables, options)
        breakdowns.append(breakdown)
        total_days += breakdown.total_days
        
        print(f"{standard.value}:")
        print(f"  - 복잡도: {breakdown.complexity.value}")
        print(f"  - ENP: {breakdown.enp}명")
        print(f"  - Stage1: {breakdown.stage1_days}일")
        print(f"  - Stage2: {breakdown.stage2_days}일")
        print(f"  - Surveillance: {breakdown.surveillance_days}일")
        print(f"  - Recert: {breakdown.recert_days}일")
        print(f"  - 총계: {breakdown.total_days}일")
        print()
    
    # 할인 계산
    integration_discount = integration.get_integration_discount()
    remote_discount = min(options.remote_audit_ratio * 0.1, 0.1)
    total_discount = min(integration_discount + remote_discount, 0.15)
    
    print(f"💰 할인 계산:")
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
        breakdowns=breakdowns,
        total_audit_days=total_days,
        subtotal_cost=subtotal_cost,
        vat_amount=vat_amount,
        total_cost=total_cost,
        created_at=datetime.now().isoformat()
    )
    
    print(f"\n✅ 견적 계산 완료!")
    return result


def main():
    """메인 함수"""
    print("🚀 ADJ v2.2 견적 계산 엔진 고급 테스트")
    print("="*60)
    
    # 견적 계산 테스트
    result = test_quote_calculation()
    
    print(f"\n🎉 모든 테스트 완료!")
    print(f"📄 견적서가 성공적으로 생성되었습니다!")


if __name__ == '__main__':
    main()

