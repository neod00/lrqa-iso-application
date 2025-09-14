from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from datetime import datetime
from io import BytesIO
from docxtpl import DocxTemplate
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

@app.route('/generate-quotation', methods=['POST'])
def generate_quotation():
    try:
        data = request.json
        application_data = data['applicationData']
        
        print(f"견적서 생성 요청: {application_data.get('법인명(국문)', 'Unknown')}")
        
        # 템플릿 로드
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'LRQA_quotation.docx')
        print(f"템플릿 경로: {template_path}")
        
        if not os.path.exists(template_path):
            return jsonify({'error': f'템플릿 파일을 찾을 수 없습니다: {template_path}'}), 404
        
        doc = DocxTemplate(template_path)
        
        # 간단한 계산
        total_employees = int(application_data.get('총직원수', 30))
        iso_standards = application_data.get('ISO표준', 'ISO 9001')
        standard_count = len([s for s in ['ISO 9001', 'ISO 14001', 'ISO 45001'] if s in iso_standards])
        
        base_days = max(2, total_employees // 20) * standard_count
        total_days = base_days + (standard_count - 1) * 0.5
        
        day_rate = 1400000.0
        total_cost = total_days * day_rate
        vat_amount = total_cost * 0.1
        final_cost = total_cost + vat_amount
        
        # 템플릿 컨텍스트
        context = {
            'client_name': application_data.get('법인명(국문)', '알 수 없음'),
            'client_name_en': application_data.get('법인명(영문)', 'Unknown'),
            'quotation_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'quotation_number': f"LRQA-{datetime.now().strftime('%Y%m%d')}-{hash(application_data.get('법인명(국문)', 'Unknown')) % 10000:04d}",
            'standards': [s.strip() for s in iso_standards.split(',')],
            'total_employees': total_employees,
            'total_cost': int(total_cost),
            'vat_amount': int(vat_amount),
            'final_cost': int(final_cost),
            'total_audit_days': total_days,
            'day_rate': int(day_rate)
        }
        
        print(f"컨텍스트: {context}")
        
        # 템플릿 렌더링
        doc.render(context)
        
        # 바이트 버퍼로 변환
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        filename = f"LRQA_견적서_{application_data.get('법인명(국문)', 'Unknown')}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        print(f"오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'message': '견적서 생성 중 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    print("간단한 Flask 서버 시작...")
    print("포트: 5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
