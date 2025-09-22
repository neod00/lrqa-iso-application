#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 핵심두뇌 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'adj_quote_engine'))
from adj_quote_engine.models import Organization, Site, StandardType, Options
from adj_quote_engine.adj_rules_v22 import QuoteEngine

def calculate_audit_days_simple(client_name, sites_data, standards):
    """핵심두뇌를 사용한 심사일수 계산 (간단한 함수 형태)"""
    
    # Site 객체 생성
    sites = []
    for site_data in sites_data:
        site = Site(
            name=site_data.get('name', 'Unknown'),
            address=site_data.get('address', ''),
            standards=[StandardType[s] for s in site_data.get('standards', ['ISO9001'])],
            total_headcount=site_data.get('total_headcount', 0),
            business_sector=site_data.get('business_sector', 'MANUFACTURING'),
            management_system_maturity=site_data.get('management_system_maturity', 'MEDIUM')
        )
        sites.append(site)
    
    # Organization 객체 생성
    organization = Organization(
        client_name=client_name,
        sites=sites,
        standards=[StandardType[s] for s in standards],
        options=Options(stage1=True, stage2=True, surveillance=True, recert=True)
    )
    
    # 핵심두뇌로 계산
    engine = QuoteEngine('standard')
    result = engine.calculate_quote(organization)
    
    return result

if __name__ == '__main__':
    print('=== 핵심두뇌 심사일수 계산 테스트 ===')
    
    # 테스트 데이터
    test_data = {
        'client_name': '1000명 화학공장',
        'sites_data': [
            {
                'name': '울산 화학공장',
                'address': '울산광역시',
                'standards': ['ISO9001', 'ISO14001', 'ISO45001'],
                'total_headcount': 1000,
                'business_sector': 'CHEMICALS',
                'management_system_maturity': 'HIGH'
            }
        ],
        'standards': ['ISO9001', 'ISO14001', 'ISO45001']
    }
    
    # 심사일수 계산
    result = calculate_audit_days_simple(
        test_data['client_name'],
        test_data['sites_data'],
        test_data['standards']
    )
    
    # 결과 출력
    print(f'고객사: {result.organization.client_name}')
    print(f'총 심사일수: {result.total_audit_days}일')
    print()
    
    for i, breakdown in enumerate(result.breakdowns):
        print(f'표준 {i+1}: {breakdown.standard.value}')
        print(f'  ENP: {breakdown.enp}명')
        print(f'  최초심사: {breakdown.stage1_days + breakdown.stage2_days}일')
        print(f'  사후심사: {breakdown.surveillance_days}일')
        print(f'  갱신심사: {breakdown.recert_days}일')
        print()
    
    print('✅ 핵심두뇌가 성공적으로 작동합니다!')
    
    # API 형태로 결과 반환 (JSON 형태)
    response = {
        'success': True,
        'client_name': result.organization.client_name,
        'total_audit_days': result.total_audit_days,
        'breakdowns': []
    }
    
    for breakdown in result.breakdowns:
        breakdown_data = {
            'standard': breakdown.standard.value,
            'enp': breakdown.enp,
            'stage1_days': breakdown.stage1_days,
            'stage2_days': breakdown.stage2_days,
            'surveillance_days': breakdown.surveillance_days,
            'recert_days': breakdown.recert_days,
            'total_initial_days': breakdown.stage1_days + breakdown.stage2_days
        }
        response['breakdowns'].append(breakdown_data)
    
    response['assumptions'] = result.assumptions
    
    print('\n=== API 형태 응답 (JSON) ===')
    import json
    print(json.dumps(response, ensure_ascii=False, indent=2))
