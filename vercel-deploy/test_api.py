#!/usr/bin/env python3
"""
API 엔드포인트 테스트 스크립트
로컬 개발 서버에서 API 기능을 테스트합니다.
"""

import requests
import json
import time

# 로컬 개발 서버 URL
BASE_URL = "http://localhost:3000"

def test_submit_application():
    """신청서 제출 API 테스트"""
    print("🧪 신청서 제출 API 테스트 시작...")
    
    test_data = {
        "company_name": "테스트제조업체",
        "company_name_en": "Test Manufacturing Co.",
        "contact_name": "홍길동",
        "contact_email": "hong@test.com",
        "contact_phone": "010-1234-5678",
        "address": "서울시 강남구 테헤란로 123",
        "standards": ["ISO 9001", "ISO 14001"],
        "total_employees": 50,
        "site_count": 1,
        "part_time_count": 5,
        "contractor_count": 10,
        "shift_workers": 8,
        "is_integrated": True,
        "shared_management_system": True,
        "common_processes": True,
        "stage1": True,
        "stage2": True,
        "surveillance": True,
        "remote_audit_ratio": 0.2
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/submit-application",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("✅ 신청서 제출 API 테스트 성공!")
            return response.json()
        else:
            print("❌ 신청서 제출 API 테스트 실패!")
            return None
            
    except Exception as e:
        print(f"❌ 신청서 제출 API 테스트 오류: {str(e)}")
        return None

def test_create_quotation():
    """견적서 생성 API 테스트"""
    print("\n🧪 견적서 생성 API 테스트 시작...")
    
    test_data = {
        "company_name": "테스트제조업체",
        "company_name_en": "Test Manufacturing Co.",
        "contact_name": "홍길동",
        "contact_email": "hong@test.com",
        "contact_phone": "010-1234-5678",
        "address": "서울시 강남구 테헤란로 123",
        "standards": ["ISO 9001", "ISO 14001"],
        "total_employees": 50,
        "sites": [{
            "name": "본사",
            "address": "서울시 강남구 테헤란로 123",
            "total_headcount": 50,
            "part_time_count": 5,
            "contractor_count": 10,
            "shift_workers": 8,
            "standards": ["ISO 9001", "ISO 14001"]
        }],
        "integration": {
            "is_integrated": True,
            "shared_management_system": True,
            "common_processes": True,
            "same_audit_team": False
        },
        "options": {
            "stage1": True,
            "stage2": True,
            "surveillance": True,
            "recert": False,
            "remote_audit_ratio": 0.2,
            "day_rate": 1300000,
            "vat_rate": 0.1
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/create-quotation",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("✅ 견적서 생성 API 테스트 성공!")
            return response.json()
        else:
            print("❌ 견적서 생성 API 테스트 실패!")
            return None
            
    except Exception as e:
        print(f"❌ 견적서 생성 API 테스트 오류: {str(e)}")
        return None

def test_send_email(quotation_data):
    """이메일 전송 API 테스트"""
    print("\n🧪 이메일 전송 API 테스트 시작...")
    
    test_data = {
        "recipient_email": "hong@test.com",
        "quotation": quotation_data.get('quotation', {})
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/send-email",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("✅ 이메일 전송 API 테스트 성공!")
            return response.json()
        else:
            print("❌ 이메일 전송 API 테스트 실패!")
            return None
            
    except Exception as e:
        print(f"❌ 이메일 전송 API 테스트 오류: {str(e)}")
        return None

def main():
    """메인 테스트 함수"""
    print("🚀 Vercel API 테스트 시작")
    print("=" * 50)
    
    # 서버 시작 대기
    print("⏳ 로컬 개발 서버 시작 대기 중...")
    time.sleep(5)
    
    # 1. 신청서 제출 테스트
    application_result = test_submit_application()
    
    # 2. 견적서 생성 테스트
    quotation_result = test_create_quotation()
    
    # 3. 이메일 전송 테스트 (견적서 데이터가 있는 경우)
    if quotation_result and quotation_result.get('success'):
        test_send_email(quotation_result)
    
    print("\n" + "=" * 50)
    print("🏁 API 테스트 완료")
    
    # 결과 요약
    if application_result and quotation_result:
        print("✅ 모든 API 테스트가 성공적으로 완료되었습니다!")
        print(f"📊 견적 금액: ₩{quotation_result['quotation']['total_cost']:,}")
        print(f"📅 총 심사일수: {quotation_result['quotation']['total_audit_days']}일")
    else:
        print("❌ 일부 API 테스트가 실패했습니다.")

if __name__ == "__main__":
    main()

