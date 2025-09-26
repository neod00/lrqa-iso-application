#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_quotation_integration():
    """견적서 생성 통합 테스트"""
    
    # 테스트 데이터
    test_data = {
        "applicationData": {
            "법인명(국문)": "테스트 화학공장",
            "법인명(영문)": "Test Chemical Factory",
            "본사주소": "울산광역시 남구",
            "총직원수": "1000",
            "비정규직수": "100",
            "협력업체직원수": "50",
            "교대근무자수": "200",
            "ISO표준": "ISO 9001, ISO 14001, ISO 45001",
            "담당자명": "홍길동",
            "담당자이메일": "test@example.com",
            "담당자전화": "010-1234-5678"
        }
    }
    
    print("=== 견적서 생성 통합 테스트 ===")
    print(f"테스트 데이터: {test_data['applicationData']['법인명(국문)']}")
    
    try:
        # 견적서 생성 API 호출
        print("\n1. 견적서 생성 API 호출...")
        response = requests.post(
            'http://127.0.0.1:5000/generate-quotation',
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 견적서 생성 성공!")
            
            # 응답이 파일인지 확인
            content_type = response.headers.get('content-type', '')
            if 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
                print("✅ Word 문서 생성 성공!")
                
                # 파일 저장
                filename = f"test_quotation_{test_data['applicationData']['법인명(국문)']}.docx"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"✅ 파일 저장: {filename}")
                
            else:
                print("❌ 예상치 못한 응답 형식")
                print(f"Content-Type: {content_type}")
                print(f"Response: {response.text[:200]}...")
        else:
            print("❌ 견적서 생성 실패!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패! 견적서 생성 서버가 실행 중인지 확인하세요.")
        print("실행 명령: python simple_server.py")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

def test_core_brain_api():
    """핵심두뇌 API 직접 테스트"""
    
    print("\n=== 핵심두뇌 API 직접 테스트 ===")
    
    test_data = {
        "client_name": "테스트 화학공장",
        "sites": [{
            "name": "울산공장",
            "address": "울산광역시 남구",
            "standards": ["ISO9001", "ISO14001", "ISO45001"],
            "total_headcount": 1000,
            "part_time_count": 100,
            "contractor_count": 50,
            "shift_workers": 200,
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
    
    try:
        response = requests.post(
            'http://127.0.0.1:5001/calculate-audit-days',
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 핵심두뇌 API 성공!")
            print(f"총 심사일수: {result.get('total_audit_days', 'N/A')}일")
            
            if 'breakdowns' in result:
                print("\n표준별 상세:")
                for breakdown in result['breakdowns']:
                    print(f"  {breakdown['standard']}: {breakdown['total_initial_days']}일")
        else:
            print("❌ 핵심두뇌 API 실패!")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 핵심두뇌 API 연결 실패! API 서버가 실행 중인지 확인하세요.")
        print("실행 명령: python audit_days_api.py")
    except Exception as e:
        print(f"❌ 핵심두뇌 API 테스트 중 오류: {e}")

if __name__ == "__main__":
    # 먼저 핵심두뇌 API 테스트
    test_core_brain_api()
    
    # 그 다음 견적서 생성 통합 테스트
    test_quotation_integration()
