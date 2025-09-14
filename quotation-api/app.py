from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import tempfile
import os
import sys
from datetime import datetime
import random
from io import BytesIO

# adj_quote_engine 모듈 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'adj_quote_engine'))

from adj_quote_engine.models import (
    QuoteResult, Organization, Site, StandardType, 
    IntegrationInputs, Options, ProgramBreakdown, ComplexityLevel
)
from adj_quote_engine.calculator import QuoteCalculator
from adj_quote_engine.quote_template import LRQAQuotationTemplate

app = Flask(__name__)
CORS(app)  # CORS 허용

def convert_application_to_quote_result(application_data):
    """Google Sheets 데이터를 QuoteResult 객체로 변환"""
    
    # 1. 표준 타입 변환
    standards = []
    if 'ISO표준' in application_data:
        iso_standards = application_data['ISO표준']
        if 'ISO 9001' in iso_standards or 'ISO9001' in iso_standards:
            standards.append(StandardType.ISO9001)
        if 'ISO 14001' in iso_standards or 'ISO14001' in iso_standards:
            standards.append(StandardType.ISO14001)
        if 'ISO 45001' in iso_standards or 'ISO45001' in iso_standards:
            standards.append(StandardType.ISO45001)
    
    # 기본값 설정
    if not standards:
        standards.append(StandardType.ISO9001)
    
    # 2. 사업장 정보 생성
    site = Site(
        name=application_data.get('법인명(국문)', '본사'),
        address=application_data.get('본사주소', '서울시 강남구'),
        standards=standards,
        total_headcount=int(application_data.get('총직원수', 30)),
        part_time_count=int(application_data.get('비정규직수', 0)),
        contractor_count=int(application_data.get('협력업체직원수', 0)),
        shift_workers=int(application_data.get('교대근무자수', 0)),
        remote_audit_ratio=float(application_data.get('원격심사비율', 0.0))
    )
    
    # 3. 통합심사 정보
    integration = IntegrationInputs(
        is_integrated=application_data.get('다중표준시스템', '아니오') == '예',
        shared_management_system=application_data.get('공통경영시스템', '아니오') == '예',
        common_processes=application_data.get('공통프로세스', '아니오') == '예',
        same_audit_team=application_data.get('동일심사팀', '아니오') == '예'
    )
    
    # 4. 조직 정보 생성
    organization = Organization(
        client_name=application_data.get('법인명(국문)', '알 수 없음'),
        client_name_en=application_data.get('법인명(영문)', 'Unknown'),
        contact_name=application_data.get('담당자명', '알 수 없음'),
        contact_email=application_data.get('담당자이메일', 'unknown@example.com'),
        contact_phone=application_data.get('담당자전화', '010-0000-0000'),
        standards=standards,
        sites=[site],
        integration=integration,
        options=Options(
            remote_audit_ratio=float(application_data.get('원격심사비율', 0.0)),
            day_rate=1400000.0,  # 1 manday 단가
            vat_rate=0.1
        )
    )
    
    # 5. QuoteResult 생성
    quote_result = QuoteResult(organization=organization)
    
    return quote_result

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({'status': 'healthy', 'message': 'Quotation API is running'})

@app.route('/generate-quotation', methods=['POST'])
def generate_quotation():
    """견적서 생성 API"""
    try:
        data = request.json
        application_data = data['applicationData']
        
        print(f"견적서 생성 요청: {application_data.get('법인명(국문)', 'Unknown')}")
        
        # 1. 신청서 데이터를 QuoteResult 객체로 변환
        quote_result = convert_application_to_quote_result(application_data)
        
        # 2. adj_quote_engine으로 정교한 계산
        calculator = QuoteCalculator()
        calculated_result = calculator.calculate_quotation(quote_result)
        
        # 3. LRQA 템플릿으로 Word 문서 생성
        template_generator = LRQAQuotationTemplate()
        docx_buffer = template_generator.generate_quotation_docx(calculated_result)
        
        # 4. Word 파일 반환
        filename = f"LRQA_견적서_{quote_result.organization.client_name}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        return send_file(
            docx_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'message': '견적서 생성 중 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
