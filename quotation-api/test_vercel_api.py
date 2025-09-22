#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_vercel_api():
    """Vercel에 배포된 핵심두뇌 API 테스트"""
    
    # Vercel API URL
    api_url = "https://lrqa-iso-application-hqhk5q4qp-dal-kims-projects.vercel.app"
    
    # 테스트 데이터 (API 형식에 맞게 수정)
    test_data = {
        "client_name": "1000명 화학공장",
        "sites": [{
            "name": "울산공장",
            "address": "울산광역시",
            "standards": ["ISO9001", "ISO14001", "ISO45001"],
            "total_headcount": 1000,
            "part_time_count": 0,
            "contractor_count": 0,
            "shift_workers": 0,
            "seasonal_factor": 1.0,
            "site_type": "PERMANENT",
            "is_headquarters": True,
            "is_sampled": True,
            "sampling_priority": 1,
            "complexity_score": 5.0,
            "risk_level": "MEDIUM",
            "business_sector": "CHEMICAL",
            "geographical_region": "DOMESTIC",
            "management_system_maturity": "MEDIUM",
            "repetitive_process": False,
            "remote_audit_ratio": 0.0
        }],
        "standards": ["ISO9001", "ISO14001", "ISO45001"],
        "options": {
            "stage1": True,
            "stage2": True,
            "surveillance": True,
            "recert": True
        }
    }
    
    print("=== Vercel 핵심두뇌 API 테스트 ===")
    print(f"API URL: {api_url}")
    print(f"테스트 데이터: {test_data['client_name']}")
    
    try:
        # Health check
        print("\n1. Health Check...")
        health_response = requests.get(f"{api_url}/health")
        print(f"Status: {health_response.status_code}")
        print(f"Response: {health_response.json()}")
        
        # 견적 계산 API 테스트
        print("\n2. 견적 계산 API 테스트...")
        quote_response = requests.post(
            f"{api_url}/calculate-audit-days",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        print(f"Status: {quote_response.status_code}")
        
        if quote_response.status_code == 200:
            result = quote_response.json()
            print("✅ API 호출 성공!")
            print(f"고객사: {result.get('client_name', 'N/A')}")
            print(f"총 심사일수: {result.get('total_audit_days', 'N/A')}일")
            
            if 'breakdowns' in result:
                print("\n표준별 상세:")
                for breakdown in result['breakdowns']:
                    print(f"  {breakdown['standard']}: {breakdown['total_initial_days']}일")
            
            if 'assumptions' in result:
                print("\n가정사항:")
                for assumption in result['assumptions'][:3]:  # 처음 3개만 출력
                    print(f"  • {assumption}")
        else:
            print("❌ API 호출 실패!")
            print(f"Error: {quote_response.text}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_vercel_api()
