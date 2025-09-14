"""
JavaScript API 테스트
"""

import requests
import json

# 배포된 URL
BASE_URL = "https://vercel-deploy-dlvhxoeci-dal-kims-projects.vercel.app"

def test_submit_application():
    """신청서 제출 API 테스트"""
    print("🧪 신청서 제출 API 테스트 시작...")
    url = f"{BASE_URL}/api/submit-application"
    headers = {'Content-Type': 'application/json'}
    data = {
        "company_name": "테스트 제조업체",
        "company_name_en": "Test Manufacturing Co.",
        "contact_name": "김테스트",
        "contact_email": "test@example.com",
        "contact_phone": "010-1234-5678",
        "address": "서울시 강남구 테헤란로 123",
        "standards": ["ISO 9001", "ISO 14001"],
        "total_employees": 50,
        "sites": [{
            "name": "본사",
            "address": "서울시 강남구",
            "total_headcount": 50,
            "standards": ["ISO 9001", "ISO 14001"]
        }],
        "integration": {
            "is_integrated": False,
            "integration_level": 0.0,
            "shared_management_system": False,
            "common_processes": False,
            "same_audit_team": False
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
        response = requests.post(url, headers=headers, json=data)
        print(f"상태 코드: {response.status_code}")
        response_json = response.json()
        if response.status_code == 200 and response_json.get('success'):
            print("✅ 신청서 제출 API 테스트 성공!")
            print(f"신청서 ID: {response_json.get('application_id')}")
            return True
        else:
            print(f"❌ 신청서 제출 API 테스트 오류: {response_json.get('error', response.text)}")
            return False
    except Exception as e:
        print(f"❌ 신청서 제출 API 테스트 오류: {e}")
        return False

def test_create_quotation():
    """견적서 생성 API 테스트"""
    print("🧪 견적서 생성 API 테스트 시작...")
    url = f"{BASE_URL}/api/create-quotation"
    headers = {'Content-Type': 'application/json'}
    data = {
        "company_name": "테스트 제조업체",
        "company_name_en": "Test Manufacturing Co.",
        "contact_name": "김테스트",
        "contact_email": "test@example.com",
        "contact_phone": "010-1234-5678",
        "address": "서울시 강남구 테헤란로 123",
        "standards": ["ISO 9001", "ISO 14001"],
        "total_employees": 50,
        "quotation_number": "TEST-001"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"상태 코드: {response.status_code}")
        response_json = response.json()
        if response.status_code == 200 and response_json.get('success'):
            print("✅ 견적서 생성 API 테스트 성공!")
            quotation = response_json.get('quotation', {})
            print(f"회사명: {quotation.get('company_name')}")
            print(f"총 견적 금액: {quotation.get('total_cost'):,}원")
            print(f"총 심사일수: {quotation.get('total_audit_days')}일")
            print(f"Word 문서: {quotation.get('word_document_url')}")
            return True
        else:
            print(f"❌ 견적서 생성 API 테스트 오류: {response_json.get('error', response.text)}")
            return False
    except Exception as e:
        print(f"❌ 견적서 생성 API 테스트 오류: {e}")
        return False

def test_send_email():
    """이메일 전송 API 테스트"""
    print("🧪 이메일 전송 API 테스트 시작...")
    url = f"{BASE_URL}/api/send-email"
    headers = {'Content-Type': 'application/json'}
    data = {
        "recipient_email": "test@example.com",
        "quotation": {
            "company_name": "테스트 제조업체",
            "quotation_number": "TEST-001",
            "total_cost": 5000000,
            "standards": ["ISO 9001", "ISO 14001"],
            "total_audit_days": 4
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"상태 코드: {response.status_code}")
        response_json = response.json()
        if response.status_code == 200 and response_json.get('success'):
            print("✅ 이메일 전송 API 테스트 성공!")
            print(f"이메일 ID: {response_json.get('email_id')}")
            print(f"수신자: {response_json.get('recipient')}")
            return True
        else:
            print(f"❌ 이메일 전송 API 테스트 오류: {response_json.get('error', response.text)}")
            return False
    except Exception as e:
        print(f"❌ 이메일 전송 API 테스트 오류: {e}")
        return False

def test_main_page():
    """메인 페이지 접근 테스트"""
    print("🧪 메인 페이지 접근 테스트 시작...")
    try:
        response = requests.get(BASE_URL)
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            print("✅ 메인 페이지 접근 성공!")
            print(f"페이지 크기: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ 메인 페이지 접근 실패! (상태 코드: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ 메인 페이지 접근 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 JavaScript API 테스트 시작")
    print("="*50)
    print(f"테스트 URL: {BASE_URL}")
    print("="*50)

    results = {
        "main_page": test_main_page(),
        "submit_application": test_submit_application(),
        "create_quotation": test_create_quotation(),
        "send_email": test_send_email()
    }

    print("\n" + "="*50)
    print("🏁 JavaScript API 테스트 완료")
    if all(results.values()):
        print("✅ 모든 API 테스트가 성공했습니다!")
        print("🎉 JavaScript API 전환이 성공적으로 완료되었습니다!")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        for test_name, passed in results.items():
            if not passed:
                print(f"  - {test_name.replace('_', ' ').capitalize()} 실패")
