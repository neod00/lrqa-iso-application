import requests
import json

print('=== API 테스트 시작 ===')

# API 테스트
try:
    print('포트 5000으로 API 호출 중...')
    response = requests.post('http://localhost:5000/api/gap-analysis', 
                           json={
                               'formData': {
                                   'companyNameKo': '테스트회사',
                                   'totalEmployees': 100
                               },
                               'selectedStandards': ['iso9001']
                           })
    
    print('Status Code:', response.status_code)
    print('Response Headers:', dict(response.headers))
    print('Response Text:', response.text)
    
    if response.status_code == 200:
        data = response.json()
        print('Success:', data.get('success'))
        if data.get('success'):
            print('Company Name:', data.get('data', {}).get('companyName'))
            print('Report HTML length:', len(data.get('data', {}).get('reportHtml', '')))
    
except Exception as e:
    print('Error:', str(e))