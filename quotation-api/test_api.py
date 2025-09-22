import requests
import json

# API 테스트 데이터
test_data = {
    'client_name': '1000명 화학공장',
    'sites': [
        {
            'name': '울산 화학공장',
            'address': '울산광역시',
            'standards': ['ISO9001', 'ISO14001', 'ISO45001'],
            'total_headcount': 1000,
            'business_sector': 'CHEMICALS',
            'management_system_maturity': 'HIGH'
        }
    ],
    'standards': ['ISO9001', 'ISO14001', 'ISO45001'],
    'options': {
        'stage1': True,
        'stage2': True,
        'surveillance': True,
        'recert': True
    }
}

print('=== 핵심두뇌 API 테스트 ===')

# Health Check
try:
    response = requests.get('http://127.0.0.1:5001/health')
    print(f'Health Check: {response.json()}')
    print()
except Exception as e:
    print(f'Health Check 실패: {e}')
    print('서버가 아직 시작되지 않았습니다. 잠시 후 다시 시도해주세요.')
    exit()

# 심사일수 계산
try:
    response = requests.post('http://127.0.0.1:5001/calculate-audit-days', json=test_data)
    result = response.json()
    
    print(f'고객사: {result["client_name"]}')
    print(f'총 심사일수: {result["total_audit_days"]}일')
    print()
    
    for i, breakdown in enumerate(result["breakdowns"]):
        print(f'표준 {i+1}: {breakdown["standard"]}')
        print(f'  ENP: {breakdown["enp"]}명')
        print(f'  최초심사: {breakdown["total_initial_days"]}일')
        print(f'  사후심사: {breakdown["surveillance_days"]}일')
        print(f'  갱신심사: {breakdown["recert_days"]}일')
        print()

    print('✅ 핵심두뇌 API가 성공적으로 작동합니다!')
    
except Exception as e:
    print(f'API 테스트 실패: {e}')
    print('서버가 시작될 때까지 잠시 기다려주세요.')
