"""
JavaScript API 테스트
"""

import requests
import json

def test_js_api():
    """JavaScript API 테스트"""
    url = "https://vercel-deploy-9fglv93e2-dal-kims-projects.vercel.app/api/test-js"
    headers = {'Content-Type': 'application/json'}
    data = {"test": "data", "message": "Hello from JavaScript test"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        
        if response.status_code == 200:
            print("✅ JavaScript API 테스트 성공!")
            return True
        else:
            print("❌ JavaScript API 테스트 실패!")
            return False
            
    except Exception as e:
        print(f"❌ API 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("🧪 JavaScript API 테스트 시작...")
    test_js_api()

