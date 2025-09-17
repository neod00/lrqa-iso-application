from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from datetime import datetime
from io import BytesIO
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

app = Flask(__name__)
CORS(app)

# Jinja2 필터 정의
def format_currency(value):
    """통화 형식으로 포맷팅"""
    if value is None:
        return "0원"
    try:
        num_value = float(value)
        formatted = f"{num_value:,.0f}"
        return f"{formatted}원"
    except (ValueError, TypeError):
        return f"{value}원"

def format_number(value):
    """숫자 형식으로 포맷팅"""
    if value is None:
        return "0"
    try:
        num_value = float(value)
        return f"{num_value:,.0f}"
    except (ValueError, TypeError):
        return str(value)

# DocxTemplate 클래스를 상속받아서 필터를 미리 등록
class CustomDocxTemplate(DocxTemplate):
    def __init__(self, tpl_path):
        super().__init__(tpl_path)
        # Jinja2 환경에 필터 등록 (안전한 방법)
        try:
            if hasattr(self, 'jinja_env') and self.jinja_env is not None:
                self.jinja_env.filters['format_currency'] = format_currency
                self.jinja_env.filters['format_number'] = format_number
                print("CustomDocxTemplate: 필터 등록 완료")
            else:
                print("CustomDocxTemplate: jinja_env가 없음")
        except Exception as e:
            print(f"CustomDocxTemplate: 필터 등록 실패 - {e}")

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
        
        # 기존 LRQA_quotation.docx 템플릿 사용
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
        
        # 데이터 준비
        client_name = application_data.get('법인명(국문)', '알 수 없음')
        client_name_en = application_data.get('법인명(영문)', 'Unknown')
        client_address = application_data.get('본사주소', '주소 미입력')
        quotation_date = datetime.now().strftime('%Y년 %m월 %d일')
        quotation_number = f"LRQA-{datetime.now().strftime('%Y%m%d')}-{hash(client_name) % 10000:04d}"
        standards = [s.strip() for s in iso_standards.split(',')]
        standards_text = ', '.join(standards)
        
        # ISO 표준 선택 여부 확인
        has_iso9001 = 'ISO 9001' in iso_standards
        has_iso14001 = 'ISO 14001' in iso_standards
        has_iso45001 = 'ISO 45001' in iso_standards
        
        # ISO 표준별 세부 계산
        iso9001_days = 2.0 if has_iso9001 else 0
        iso14001_days = 2.0 if has_iso14001 else 0
        iso45001_days = 2.0 if has_iso45001 else 0
        
        # Stage 1, 2 일수 계산 (간단한 예시)
        iso9001_stage1_days = 1.0 if has_iso9001 else 0
        iso9001_stage2_days = 1.0 if has_iso9001 else 0
        iso9001_stage1_2_days = iso9001_stage1_days + iso9001_stage2_days
        
        iso14001_stage1_days = 1.0 if has_iso14001 else 0
        iso14001_stage2_days = 1.0 if has_iso14001 else 0
        iso14001_stage1_2_days = iso14001_stage1_days + iso14001_stage2_days
        
        iso45001_stage1_days = 1.0 if has_iso45001 else 0
        iso45001_stage2_days = 1.0 if has_iso45001 else 0
        iso45001_stage1_2_days = iso45001_stage1_days + iso45001_stage2_days
        
        # 감사 일수 계산
        iso9001_surveillance_days = 1.0 if has_iso9001 else 0
        iso14001_surveillance_days = 1.0 if has_iso14001 else 0
        iso45001_surveillance_days = 1.0 if has_iso45001 else 0
        
        # 비용 계산
        iso9001_stage1_2_cost = iso9001_stage1_2_days * day_rate
        iso14001_stage1_2_cost = iso14001_stage1_2_days * day_rate
        iso45001_stage1_2_cost = iso45001_stage1_2_days * day_rate
        
        # 여행비 (간단한 계산)
        travel_expense = 500000  # 50만원
        total_cost_with_travel = total_cost + travel_expense
        
        print(f"견적서 생성: {client_name}, {standards}, {total_employees}명")
        print(f"ISO 표준 선택: 9001={has_iso9001}, 14001={has_iso14001}, 45001={has_iso45001}")
        
        # 템플릿 컨텍스트 (모든 필요한 변수 제공)
        context = {
            # 기본 정보
            'client_name': client_name,
            'client_name_en': client_name_en,
            'client_address': client_address,
            'quotation_date': quotation_date,
            'quotation_number': quotation_number,
            'standards': standards,
            'standards_text': standards_text,
            'total_employees': total_employees,
            'total_sites': 1,  # 기본값
            
            # ISO 표준 선택 여부 (조건부 변수)
            'has_iso9001': has_iso9001,
            'has_iso14001': has_iso14001,
            'has_iso45001': has_iso45001,
            
            # 기본 계산값
            'total_cost': int(total_cost),
            'vat_amount': int(vat_amount),
            'final_cost': int(final_cost),
            'total_audit_days': total_days,
            'day_rate': int(day_rate),
            
            # ISO 9001 관련
            'iso9001_stage1_days': iso9001_stage1_days,
            'iso9001_stage2_days': iso9001_stage2_days,
            'iso9001_stage1_2_days': iso9001_stage1_2_days,
            'iso9001_surveillance_days': iso9001_surveillance_days,
            'iso9001_stage1_2_cost': int(iso9001_stage1_2_cost),
            
            # ISO 14001 관련
            'iso14001_stage1_days': iso14001_stage1_days,
            'iso14001_stage2_days': iso14001_stage2_days,
            'iso14001_stage1_2_days': iso14001_stage1_2_days,
            'iso14001_surveillance_days': iso14001_surveillance_days,
            'iso14001_stage1_2_cost': int(iso14001_stage1_2_cost),
            
            # ISO 45001 관련
            'iso45001_stage1_days': iso45001_stage1_days,
            'iso45001_stage2_days': iso45001_stage2_days,
            'iso45001_stage1_2_days': iso45001_stage1_2_days,
            'iso45001_surveillance_days': iso45001_surveillance_days,
            'iso45001_stage1_2_cost': int(iso45001_stage1_2_cost),
            
            # 기타 비용
            'travel_expense': int(travel_expense),
            'total_cost_with_travel': int(total_cost_with_travel),
            
            # 필터 사용 우회를 위한 미리 포맷팅된 값들
            'total_cost_formatted': f"{int(total_cost):,}원",
            'vat_amount_formatted': f"{int(vat_amount):,}원",
            'final_cost_formatted': f"{int(final_cost):,}원",
            'day_rate_formatted': f"{int(day_rate):,}원",
            'total_audit_days_formatted': f"{total_days:.1f}일",
            'iso9001_stage1_2_cost_formatted': f"{int(iso9001_stage1_2_cost):,}원",
            'iso14001_stage1_2_cost_formatted': f"{int(iso14001_stage1_2_cost):,}원",
            'iso45001_stage1_2_cost_formatted': f"{int(iso45001_stage1_2_cost):,}원",
            'travel_expense_formatted': f"{int(travel_expense):,}원",
            'total_cost_with_travel_formatted': f"{int(total_cost_with_travel):,}원"
        }
        
        print(f"컨텍스트: {context}")
        
        # 템플릿 렌더링
        doc.render(context)
        
        print("템플릿 기반 Word 문서 생성 완료")
        
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