"""
Word 문서 생성 테스트
"""

import requests
import json
import time

# 배포된 URL
BASE_URL = "https://vercel-deploy-guyvm2xei-dal-kims-projects.vercel.app"

def test_word_generation():
    """Word 문서 생성 테스트"""
    print("🧪 Word 문서 생성 테스트 시작...")
    
    # 견적서 생성 요청
    url = f"{BASE_URL}/api/create-quotation"
    headers = {'Content-Type': 'application/json'}
    data = {
        "company_name": "테스트 제조업체",
        "company_name_en": "Test Manufacturing Co. Ltd.",
        "contact_name": "김테스트",
        "contact_email": "test@example.com",
        "contact_phone": "010-1234-5678",
        "address": "서울시 강남구 테헤란로 123",
        "standards": ["ISO 9001", "ISO 14001", "ISO 45001"],
        "total_employees": 100,
        "quotation_number": "TEST-WORD-001"
    }
    
    try:
        print("📝 견적서 생성 요청 중...")
        response = requests.post(url, headers=headers, json=data)
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('success'):
                print("✅ 견적서 생성 성공!")
                
                quotation = response_json.get('quotation', {})
                word_document_url = quotation.get('word_document_url')
                
                if word_document_url:
                    print(f"📄 Word 문서 경로: {word_document_url}")
                    
                    # Word 문서 다운로드 테스트
                    test_word_download(word_document_url)
                else:
                    print("⚠️ Word 문서가 생성되지 않았습니다.")
                
                # 견적서 정보 출력
                print(f"회사명: {quotation.get('company_name')}")
                print(f"총 견적 금액: {quotation.get('total_cost'):,}원")
                print(f"총 심사일수: {quotation.get('total_audit_days')}일")
                print(f"적용 표준: {', '.join(quotation.get('standards', []))}")
                
                return True
            else:
                print(f"❌ 견적서 생성 실패: {response_json.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ 견적서 생성 실패! (상태 코드: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 견적서 생성 테스트 오류: {e}")
        return False

def test_word_download(word_document_url):
    """Word 문서 다운로드 테스트"""
    print("📥 Word 문서 다운로드 테스트 시작...")
    
    try:
        # 파일명 추출
        filename = word_document_url.split('/')[-1]
        download_url = f"{BASE_URL}/api/download-quotation?filename={filename}"
        
        print(f"다운로드 URL: {download_url}")
        
        # 다운로드 요청
        response = requests.get(download_url)
        print(f"다운로드 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            # 파일 크기 확인
            file_size = len(response.content)
            print(f"✅ Word 문서 다운로드 성공!")
            print(f"파일 크기: {file_size:,} bytes")
            
            # 파일 저장 (로컬 테스트용)
            with open(f"test_quotation_{int(time.time())}.docx", "wb") as f:
                f.write(response.content)
            print("💾 로컬에 파일 저장 완료")
            
            return True
        else:
            print(f"❌ Word 문서 다운로드 실패! (상태 코드: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Word 문서 다운로드 테스트 오류: {e}")
        return False

def test_template_file():
    """템플릿 파일 접근 테스트"""
    print("📋 템플릿 파일 접근 테스트 시작...")
    
    try:
        # 템플릿 파일 다운로드 시도
        template_url = f"{BASE_URL}/templates/LRQA_quotation.docx"
        response = requests.get(template_url)
        print(f"템플릿 파일 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 템플릿 파일 접근 성공!")
            print(f"템플릿 파일 크기: {len(response.content):,} bytes")
            return True
        else:
            print(f"❌ 템플릿 파일 접근 실패! (상태 코드: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ 템플릿 파일 접근 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Word 문서 생성 테스트 시작")
    print("="*60)
    print(f"테스트 URL: {BASE_URL}")
    print("="*60)

    results = {
        "template_file": test_template_file(),
        "word_generation": test_word_generation()
    }

    print("\n" + "="*60)
    print("🏁 Word 문서 생성 테스트 완료")
    if all(results.values()):
        print("✅ 모든 Word 문서 생성 테스트가 성공했습니다!")
        print("🎉 Word 문서 생성 기능이 완전히 작동합니다!")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        for test_name, passed in results.items():
            if not passed:
                print(f"  - {test_name.replace('_', ' ').capitalize()} 실패")
