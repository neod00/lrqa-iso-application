"""
간단한 API 테스트
"""

import requests
import json

def test_simple_api():
    """간단한 API 테스트"""
    url = "https://vercel-deploy-hasnqlrh7-dal-kims-projects.vercel.app/api/test-simple"
    headers = {'Content-Type': 'application/json'}
    data = {"test": "data", "message": "Hello from test"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        
        if response.status_code == 200:
            print("✅ 간단한 API 테스트 성공!")
            return True
        else:
            print("❌ 간단한 API 테스트 실패!")
            return False
            
    except Exception as e:
        print(f"❌ API 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("🧪 간단한 API 테스트 시작...")
    test_simple_api()

