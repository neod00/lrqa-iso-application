import os
os.environ['FLASK_SKIP_DOTENV'] = '1'  # .env 파일 로딩 비활성화

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import tempfile
from datetime import datetime
from io import BytesIO
from docxtpl import DocxTemplate

app = Flask(__name__)
CORS(app)

def create_template_based_quotation_docx(application_data):
    """LRQA_quotation.docx 템플릿을 사용한 견적서 생성"""
    
    try:
        # 1. LRQA 템플릿 로드
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'LRQA_quotation.docx')
        print(f"템플릿 경로: {template_path}")
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
        
        doc = DocxTemplate(template_path)
        
        # 2. 간단한 견적 계산
        total_employees = int(application_data.get('총직원수', 30))
        iso_standards = application_data.get('ISO표준', 'ISO 9001')
        standard_count = len([s for s in ['ISO 9001', 'ISO 14001', 'ISO 45001'] if s in iso_standards])
        
        # 기본 심사일수 계산 (간단한 공식)
        base_days = max(2, total_employees // 20) * standard_count
        total_days = base_days + (standard_count - 1) * 0.5  # 다중 표준 할인
        
        day_rate = 1400000.0
        total_cost = total_days * day_rate
        vat_amount = total_cost * 0.1
        final_cost = total_cost + vat_amount
        
        # 3. 템플릿 컨텍스트 데이터 준비
        context = {
            'company_name': application_data.get('법인명(국문)', '알 수 없음'),
            'company_name_en': application_data.get('법인명(영문)', 'Unknown'),
            'contact_name': application_data.get('담당자명', '알 수 없음'),
            'contact_email': application_data.get('담당자이메일', 'unknown@example.com'),
            'contact_phone': application_data.get('담당자전화', '010-0000-0000'),
            'quotation_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'quotation_number': f"LRQA-{datetime.now().strftime('%Y%m%d')}-{hash(application_data.get('법인명(국문)', 'Unknown')) % 10000:04d}",
            'standards': [s.strip() for s in iso_standards.split(',')],
            'total_employees': total_employees,
            'total_cost': int(total_cost),
            'vat_amount': int(vat_amount),
            'final_cost': int(final_cost),
            'audit_days': total_days,
            'day_rate': int(day_rate)
        }
        
        print(f"템플릿 컨텍스트: {context}")
        
        # 4. 템플릿 렌더링
        doc.render(context)
        
        # 5. 바이트 버퍼로 변환
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
