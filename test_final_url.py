import requests
import json

# 최종 Vercel 인증 우회 URL 테스트
url = "https://lrqa-iso-application-1ysvzpqdd-dal-kims-projects.vercel.app/generate-quotation?_vercel_share=NVY1htMEJWVYhJXPrhN2lcQyEzGcUXTP"

# 테스트 데이터
test_data = {
    "timestamp": "2025-09-14 21:42:00",
    "applicationData": {
        "법인명(국문)": "김달주식회사",
        "법인명(영문)": "Kimdal Co., Ltd.",
        "담당자명": "김달수",
        "담당자 전화": "02-1234-5679",
        "담당자 이메일": "kimdal@example.com"
    }
}

try:
    print("최종 Vercel 인증 우회 URL 테스트 시작...")
    print(f"URL: {url}")
    print(f"데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(url, json=test_data, timeout=30)
    
    print(f"\n응답 상태 코드: {response.status_code}")
    print(f"응답 헤더: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ API 정상 작동!")
        # Word 파일이면 바이너리로 저장
        if 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in response.headers.get('content-type', ''):
            with open('test_final_quotation.docx', 'wb') as f:
                f.write(response.content)
            print("견적서 파일이 test_final_quotation.docx로 저장되었습니다.")
        else:
            print(f"응답 내용: {response.text}")
    else:
        print(f"❌ API 오류: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 요청 오류: {e}")
except Exception as e:
    print(f"❌ 기타 오류: {e}")
