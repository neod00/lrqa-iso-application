#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실제 견적서 생성 테스트
"""

import requests
import json
import time

def test_quotation_generation():
    """실제 견적서 생성 테스트"""
    
    # API 서버가 시작될 때까지 잠시 대기
    print("⏳ API 서버 시작 대기 중...")
    time.sleep(3)
    
    # 테스트 데이터
    test_data = {
        "applicationData": {
            "법인명(국문)": "테스트 화학공장",
            "법인명(영문)": "Test Chemical Factory",
            "본사주소": "서울시 강남구 테헤란로 123",
            "총직원수": 150,
            "비정규직수": 20,
            "협력업체직원수": 30,
            "교대근무자수": 10,
            "ISO표준": "ISO 9001, ISO 14001, ISO 45001"
        }
    }
    
    try:
        print("🚀 견적서 생성 테스트 시작")
        print(f"📊 테스트 데이터: {test_data['applicationData']['법인명(국문)']}")
        
        # 견적서 생성 API 호출
        response = requests.post(
            "http://127.0.0.1:5000/generate-quotation",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ 견적서 생성 성공!")
            
            # 생성된 파일 저장
            with open("test_generated_quotation.docx", "wb") as f:
                f.write(response.content)
            
            print("💾 견적서 파일 저장: test_generated_quotation.docx")
            print(f"📁 파일 크기: {len(response.content):,} bytes")
            
            return True
        else:
            print(f"❌ 견적서 생성 실패: {response.status_code}")
            print(f"오류 내용: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패! API 서버가 실행 중인지 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_core_brain_api():
    """핵심두뇌 API 테스트"""
    try:
        print("\n🧠 핵심두뇌 API 테스트")
        
        test_data = {
            "client_name": "테스트 화학공장",
            "sites": [{
                "name": "본사",
                "address": "서울시 강남구 테헤란로 123",
                "standards": ["ISO9001", "ISO14001", "ISO45001"],
                "total_headcount": 150,
                "business_sector": "MANUFACTURING",
                "management_system_maturity": "MEDIUM"
            }],
            "standards": ["ISO9001", "ISO14001", "ISO45001"],
            "options": {
                "stage1": True,
                "stage2": True,
                "surveillance": True,
                "recert": True
            }
        }
        
        response = requests.post(
            "http://127.0.0.1:5001/calculate-audit-days",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 핵심두뇌 API 성공!")
            print(f"📊 총 심사일수: {result.get('total_audit_days', 'N/A')}일")
            return True
        else:
            print(f"❌ 핵심두뇌 API 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 핵심두뇌 API 오류: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 견적서 생성 시스템 테스트")
    print("=" * 60)
    
    # 핵심두뇌 API 테스트
    core_brain_ok = test_core_brain_api()
    
    # 견적서 생성 테스트
    quotation_ok = test_quotation_generation()
    
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약")
    print("=" * 60)
    print(f"핵심두뇌 API: {'✅ 성공' if core_brain_ok else '❌ 실패'}")
    print(f"견적서 생성: {'✅ 성공' if quotation_ok else '❌ 실패'}")
    
    if quotation_ok:
        print("\n💡 생성된 견적서를 열어서 변수 치환 상태를 확인하세요!")
        print("   - test_generated_quotation.docx 파일을 확인")
        print("   - {{ 변수명 }} 형태가 실제 값으로 치환되었는지 확인")
