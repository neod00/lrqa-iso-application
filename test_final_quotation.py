#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 견적서 생성 테스트
"""

import requests
import json
import time
import os

def test_final_quotation():
    """최종 견적서 생성 테스트"""
    
    print("🚀 최종 견적서 생성 테스트")
    print("=" * 60)
    
    # API 서버 시작 대기
    print("⏳ API 서버 시작 대기 중...")
    time.sleep(2)
    
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
            output_path = "final_test_quotation.docx"
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"💾 견적서 파일 저장: {output_path}")
            print(f"📁 파일 크기: {len(response.content):,} bytes")
            
            # 파일 존재 확인
            if os.path.exists(output_path):
                print(f"✅ 파일 생성 확인: {output_path}")
                return True
            else:
                print("❌ 파일이 생성되지 않았습니다.")
                return False
        else:
            print(f"❌ 견적서 생성 실패: {response.status_code}")
            print(f"오류 내용: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패! API 서버가 실행 중인지 확인하세요.")
        print("💡 다음 명령으로 서버를 실행하세요:")
        print("   cd quotation-api")
        print("   python simple_server.py")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def check_template_file():
    """템플릿 파일 확인"""
    print("\n🔍 템플릿 파일 확인")
    print("=" * 30)
    
    template_path = "quotation-api/templates/LRQA_quotation.docx"
    
    if os.path.exists(template_path):
        file_size = os.path.getsize(template_path)
        print(f"✅ 템플릿 파일 존재: {template_path}")
        print(f"📁 파일 크기: {file_size:,} bytes")
        return True
    else:
        print(f"❌ 템플릿 파일 없음: {template_path}")
        return False

def main():
    print("🔧 최종 견적서 생성 테스트")
    print("=" * 60)
    
    # 1. 템플릿 파일 확인
    if not check_template_file():
        print("❌ 템플릿 파일이 없습니다. 먼저 템플릿을 준비하세요.")
        return
    
    # 2. 견적서 생성 테스트
    success = test_final_quotation()
    
    print("\n" + "=" * 60)
    print("📋 테스트 결과")
    print("=" * 60)
    
    if success:
        print("🎉 견적서 생성 성공!")
        print("💡 생성된 견적서를 열어서 변수 치환 상태를 확인하세요.")
        print("   - final_test_quotation.docx 파일을 확인")
        print("   - {{ 변수명 }} 형태가 실제 값으로 치환되었는지 확인")
    else:
        print("❌ 견적서 생성 실패")
        print("💡 다음을 확인하세요:")
        print("   1. API 서버가 실행 중인지 확인")
        print("   2. 템플릿 파일이 올바른지 확인")
        print("   3. 로그에서 오류 메시지 확인")

if __name__ == "__main__":
    main()
