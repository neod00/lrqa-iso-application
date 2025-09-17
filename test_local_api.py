import requests
import json

# 로컬 API 테스트
url = "http://localhost:5000/generate-quotation"

# 테스트 데이터
test_data = {
    "timestamp": "2025-09-14 21:42:00",
    "applicationData": {
        "법인명(국문)": "테스트회사",
        "법인명(영문)": "Test Company",
        "담당자명": "홍길동",
        "담당자 전화": "02-1234-5678",
        "담당자 이메일": "test@example.com"
    }
}

try:
    print("로컬 API 테스트 시작...")
    print(f"URL: {url}")
    print(f"데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(url, json=test_data, timeout=30)
    
    print(f"\n응답 상태 코드: {response.status_code}")
    print(f"응답 헤더: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ 로컬 API 정상 작동!")
        # Word 파일이면 바이너리로 저장
        if 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in response.headers.get('content-type', ''):
            with open('test_local_quotation.docx', 'wb') as f:
                f.write(response.content)
            print("견적서 파일이 test_local_quotation.docx로 저장되었습니다.")
        else:
            print(f"응답 내용: {response.text}")
    else:
        print(f"❌ API 오류: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ 연결 오류: 로컬 서버가 실행되지 않았습니다. {e}")
except requests.exceptions.RequestException as e:
    print(f"❌ 요청 오류: {e}")
except Exception as e:
    print(f"❌ 기타 오류: {e}")
