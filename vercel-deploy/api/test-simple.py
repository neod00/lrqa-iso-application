"""
간단한 테스트 API
BaseHTTPRequestHandler 없이 작동하는지 테스트
"""

import json

def handler(request):
    """Vercel Functions 핸들러"""
    # CORS 헤더 설정
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # OPTIONS 요청 처리 (CORS preflight)
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # POST 요청만 허용
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # 요청 데이터 파싱
        if hasattr(request, 'get_json'):
            body = request.get_json()
        elif hasattr(request, 'body'):
            body = json.loads(request.body) if request.body else {}
        else:
            body = {}
        
        # 간단한 응답
        response_data = {
            'success': True,
            'message': 'API가 정상적으로 작동합니다.',
            'received_data': body,
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': 'API 오류가 발생했습니다.',
                'message': str(e)
            }, ensure_ascii=False)
        }

# Vercel Functions 진입점
def main(request):
    return handler(request)

