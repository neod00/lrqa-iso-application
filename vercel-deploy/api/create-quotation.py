#!/usr/bin/env python3
"""
Vercel Python API: 견적서 생성
jinja2와 DocxTemplate을 사용하여 Word 문서 생성
"""

import json
import os
import sys
from pathlib import Path
from docxtpl import DocxTemplate
from datetime import datetime
import traceback

# adj_quote_engine 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'adj_quote_engine'))

def handler(request):
    """Vercel Python 함수 핸들러"""
    
    # CORS 헤더 설정
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # OPTIONS 요청 처리 (CORS preflight)
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # POST 요청만 허용
    if request.get('method') != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # 요청 데이터 파싱
        body = request.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        if not body or len(body) == 0:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        # 견적서 데이터 생성
        quotation_data = create_quotation_data(body)
        
        # Word 문서 생성
        word_document_buffer = generate_word_document(quotation_data, body.get('quotation_number', 'default'))
        
        # 응답 데이터 구성
        response_data = {
            'success': True,
            'message': '견적서가 성공적으로 생성되었습니다.',
            'quotation': {
                'quotation_number': quotation_data['company_name'] + '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                'company_name': quotation_data['company_name'],
                'total_cost': quotation_data['total_cost'],
                'total_audit_days': quotation_data['total_audit_days'],
                'standards': quotation_data['standards'],
                'breakdowns': quotation_data['breakdowns'],
                'word_document_buffer': word_document_buffer.hex(),  # bytes를 hex 문자열로 변환
                'created_at': datetime.now().isoformat()
            }
        }
        
        # Word 문서를 직접 반환
        headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # 파일명을 URL 인코딩하여 한글 문제 해결
        fileName = f"quotation_{quotation_data['company_name']}_{datetime.now().strftime('%Y-%m-%d')}.docx"
        headers['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{fileName}'
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': word_document_buffer
        }
        
    except Exception as error:
        print(f'Error creating quotation: {error}')
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': '견적서 생성 중 오류가 발생했습니다.',
                'message': str(error)
            })
        }

def create_quotation_data(application_data):
    """견적서 데이터를 생성합니다."""
    
    # 기본 견적서 데이터
    quotation_data = {
        'company_name': application_data.get('applicationData', {}).get('법인명(국문)', 'Unknown Company'),
        'client_name': application_data.get('applicationData', {}).get('법인명(국문)', 'Unknown Company'),
        'client_address': application_data.get('applicationData', {}).get('본사주소', '서울시 강남구'),
        'standards': [application_data.get('applicationData', {}).get('ISO표준', 'ISO9001')],
        'total_employees': int(application_data.get('applicationData', {}).get('총직원수', 30)),
        'quotation_date': datetime.now().strftime('%Y-%m-%d'),
        'quotation_number': f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'total_sites': 1,
        'has_iso14001': 'iso14001' in application_data.get('applicationData', {}).get('ISO표준', '').lower(),
        'has_iso45001': 'iso45001' in application_data.get('applicationData', {}).get('ISO표준', '').lower(),
    }
    
    # 표준 텍스트 생성
    standards = quotation_data['standards']
    if len(standards) == 1:
        quotation_data['standards_text'] = standards[0]
    else:
        quotation_data['standards_text'] = ', '.join(standards[:-1]) + f' 및 {standards[-1]}'
    
    # 기본 견적 계산 (간단한 로직)
    base_days = 3  # 기본 3일
    if quotation_data['total_employees'] > 50:
        base_days += 1
    if quotation_data['total_employees'] > 100:
        base_days += 1
    
    quotation_data['total_audit_days'] = base_days
    quotation_data['total_cost'] = base_days * 1400000  # 일당 140만원
    quotation_data['total_cost_with_travel'] = quotation_data['total_cost'] + (quotation_data['total_cost'] * 0.1)
    quotation_data['travel_expense'] = quotation_data['total_cost'] * 0.1
    
    # ISO별 세부 정보
    quotation_data['iso9001_days'] = base_days
    quotation_data['iso9001_cost'] = quotation_data['total_cost']
    quotation_data['iso14001_days'] = 0
    quotation_data['iso14001_cost'] = 0
    quotation_data['iso45001_days'] = 0
    quotation_data['iso45001_cost'] = 0
    
    if quotation_data['has_iso14001']:
        quotation_data['iso14001_days'] = base_days
        quotation_data['iso14001_cost'] = quotation_data['total_cost']
        quotation_data['total_audit_days'] += base_days
        quotation_data['total_cost'] += quotation_data['total_cost']
    
    if quotation_data['has_iso45001']:
        quotation_data['iso45001_days'] = base_days
        quotation_data['iso45001_cost'] = quotation_data['total_cost']
        quotation_data['total_audit_days'] += base_days
        quotation_data['total_cost'] += quotation_data['total_cost']
    
    # 포맷된 값들
    quotation_data['total_audit_days_formatted'] = f"{quotation_data['total_audit_days']}일"
    quotation_data['total_cost_formatted'] = f"{quotation_data['total_cost']:,}원"
    quotation_data['total_cost_with_travel_formatted'] = f"{quotation_data['total_cost_with_travel']:,}원"
    quotation_data['travel_expense_formatted'] = f"{quotation_data['travel_expense']:,}원"
    quotation_data['iso9001_days_formatted'] = f"{quotation_data['iso9001_days']}일"
    quotation_data['iso9001_cost_formatted'] = f"{quotation_data['iso9001_cost']:,}원"
    
    return quotation_data

def generate_word_document(quotation_data, quotation_number):
    """Word 문서를 생성합니다."""
    
    # 템플릿 파일 경로
    template_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'templates', 'LRQA_quotation.docx')
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
    
    print(f"템플릿 파일 로드: {template_path}")
    
    # DocxTemplate으로 템플릿 로드
    doc = DocxTemplate(template_path)
    
    # 템플릿 데이터 준비
    template_data = {
        # 기본 정보
        'client_name': quotation_data['client_name'],
        'client_address': quotation_data['client_address'],
        'standards_text': quotation_data['standards_text'],
        'quotation_date': quotation_data['quotation_date'],
        'quotation_number': quotation_data['quotation_number'],
        'total_sites': quotation_data['total_sites'],
        'total_employees': quotation_data['total_employees'],
        
        # 견적 정보
        'total_audit_days': quotation_data['total_audit_days'],
        'total_audit_days_formatted': quotation_data['total_audit_days_formatted'],
        'total_cost': quotation_data['total_cost'],
        'total_cost_formatted': quotation_data['total_cost_formatted'],
        'total_cost_with_travel': quotation_data['total_cost_with_travel'],
        'total_cost_with_travel_formatted': quotation_data['total_cost_with_travel_formatted'],
        'travel_expense': quotation_data['travel_expense'],
        'travel_expense_formatted': quotation_data['travel_expense_formatted'],
        
        # ISO별 정보
        'has_iso9001': 'ISO9001' in quotation_data['standards'],
        'has_iso14001': quotation_data['has_iso14001'],
        'has_iso45001': quotation_data['has_iso45001'],
        
        'iso9001_days': quotation_data['iso9001_days'],
        'iso9001_days_formatted': quotation_data['iso9001_days_formatted'],
        'iso9001_cost': quotation_data['iso9001_cost'],
        'iso9001_cost_formatted': quotation_data['iso9001_cost_formatted'],
        
        'iso14001_days': quotation_data['iso14001_days'],
        'iso14001_cost': quotation_data['iso14001_cost'],
        
        'iso45001_days': quotation_data['iso45001_days'],
        'iso45001_cost': quotation_data['iso45001_cost'],
        
        # 기타
        'created_at': datetime.now().isoformat(),
        'year': datetime.now().year
    }
    
    print(f"템플릿 데이터 키 개수: {len(template_data)}")
    print(f"has_iso14001: {template_data['has_iso14001']}")
    print(f"standards_text: {template_data['standards_text']}")
    
    # 템플릿 렌더링
    doc.render(template_data)
    
    # Word 문서를 bytes로 변환
    word_buffer = doc.get_docx()
    
    print(f"Word 문서 생성 완료: {len(word_buffer)} bytes")
    
    return word_buffer

# Vercel에서 실행될 때 호출되는 함수
def main(request):
    return handler(request)
