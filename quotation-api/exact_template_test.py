import os
os.environ['FLASK_SKIP_DOTENV'] = '1'  # .env 파일 로딩 비활성화

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import tempfile
from datetime import datetime
from io import BytesIO
import sys

# adj_quote_engine 모듈 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'adj_quote_engine'))

from adj_quote_engine.models import (
    QuoteResult, Organization, Site, StandardType, 
    IntegrationInputs, Options, ProgramBreakdown, ComplexityLevel
)
from adj_quote_engine.pricing import PricingCalculator
from adj_quote_engine.quote_template import LRQAQuotationTemplate

app = Flask(__name__)
CORS(app)

def convert_application_to_quote_result(application_data):
    """Google Sheets 데이터를 QuoteResult 객체로 변환 (기존 방식 그대로)"""
    
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

def create_exact_template_quotation_docx(application_data):
    """기존 adj_quote_engine 방식 그대로 템플릿 사용"""
    
    try:
        # 1. 신청서 데이터를 QuoteResult 객체로 변환
        quote_result = convert_application_to_quote_result(application_data)
        
        # 2. PricingCalculator로 비용 계산
        pricing_calc = PricingCalculator(day_rate=1400000.0, vat_rate=0.1)
        
        # 3. 간단한 심사일수 계산 (기존 로직)
        total_employees = quote_result.organization.sites[0].total_headcount
        standard_count = len(quote_result.organization.standards)
        
        # 기본 심사일수 계산
        base_days = max(2, total_employees // 20) * standard_count
        total_days = base_days + (standard_count - 1) * 0.5  # 다중 표준 할인
        
        # 4. 비용 계산
        cost_result = pricing_calc.calc_cost(total_days)
        
        # 5. QuoteResult에 계산 결과 설정
        quote_result.total_audit_days = total_days
        quote_result.total_cost = cost_result['subtotal']
        quote_result.vat_amount = cost_result['vat']
        quote_result.final_cost = cost_result['total']
        
        # 6. ProgramBreakdown 생성
        breakdown = ProgramBreakdown(
            standard=quote_result.organization.standards[0],
            complexity=ComplexityLevel.MEDIUM,
            stage1_days=total_days * 0.6,
            stage2_days=total_days * 0.4,
            surveillance_days=total_days * 0.3,
            recertification_days=total_days * 0.8
        )
        quote_result.breakdowns = [breakdown]
        
        # 7. LRQA 템플릿 사용 (기존 방식 그대로)
        template_generator = LRQAQuotationTemplate()
        
        # 8. 임시 파일로 저장 후 메모리로 로드
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # 9. 템플릿으로 견적서 생성
        template_generator.generate_quotation_docx(quote_result, temp_path)
        
        # 10. 생성된 파일을 메모리로 로드
        with open(temp_path, 'rb') as f:
            docx_data = f.read()
        
        # 11. 임시 파일 삭제
        os.unlink(temp_path)
        
        # 12. BytesIO로 변환
        buffer = BytesIO(docx_data)
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
        
        # 기존 adj_quote_engine 방식 그대로 템플릿 사용
        docx_buffer = create_exact_template_quotation_docx(application_data)
        
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
    print("기존 adj_quote_engine 방식 그대로 사용")
    app.run(debug=False, host='127.0.0.1', port=5000)
