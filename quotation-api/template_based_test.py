import os
os.environ['FLASK_SKIP_DOTENV'] = '1'  # .env 파일 로딩 비활성화

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import tempfile
from datetime import datetime
from io import BytesIO
from docxtpl import DocxTemplate
import sys

# adj_quote_engine 모듈 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'adj_quote_engine'))

from adj_quote_engine.models import (
    QuoteResult, Organization, Site, StandardType, 
    IntegrationInputs, Options, ProgramBreakdown, ComplexityLevel
)
from adj_quote_engine.calculator import QuoteCalculator

app = Flask(__name__)
CORS(app)

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

def create_template_based_quotation_docx(application_data):
    """LRQA_quotation.docx 템플릿을 사용한 견적서 생성"""
    
    try:
        # 1. 신청서 데이터를 QuoteResult 객체로 변환
        quote_result = convert_application_to_quote_result(application_data)
        
        # 2. adj_quote_engine으로 정교한 계산
        calculator = QuoteCalculator()
        calculated_result = calculator.calculate_quotation(quote_result)
        
        # 3. LRQA 템플릿 로드
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'LRQA_quotation.docx')
        doc = DocxTemplate(template_path)
        
        # 4. 템플릿 컨텍스트 데이터 준비
        context = {
            'company_name': calculated_result.organization.client_name,
            'company_name_en': calculated_result.organization.client_name_en,
            'contact_name': calculated_result.organization.contact_name,
            'contact_email': calculated_result.organization.contact_email,
            'contact_phone': calculated_result.organization.contact_phone,
            'quotation_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'quotation_number': f"LRQA-{datetime.now().strftime('%Y%m%d')}-{hash(calculated_result.organization.client_name) % 10000:04d}",
            'standards': [standard.value for standard in calculated_result.organization.standards],
            'total_employees': calculated_result.organization.sites[0].total_headcount,
            'total_cost': calculated_result.total_cost,
            'vat_amount': calculated_result.vat_amount,
            'final_cost': calculated_result.final_cost,
            'audit_days': calculated_result.total_audit_days,
            'day_rate': calculated_result.organization.options.day_rate
        }
        
        # 5. 템플릿 렌더링
        doc.render(context)
        
        # 6. 바이트 버퍼로 변환
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"템플릿 기반 견적서 생성 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

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
        
        # LRQA 템플릿을 사용한 견적서 생성
        docx_buffer = create_template_based_quotation_docx(application_data)
        
        # 파일명 생성
        filename = f"LRQA_견적서_{application_data.get('법인명(국문)', 'Unknown')}_{datetime.now().strftime('%Y%m%d')}.docx"
        
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
    print("Flask 서버 시작 중...")
    print("헬스 체크: http://localhost:5000/health")
    print("견적서 생성: http://localhost:5000/generate-quotation")
    print("LRQA_quotation.docx 템플릿 사용")
    app.run(debug=False, host='127.0.0.1', port=5000)
