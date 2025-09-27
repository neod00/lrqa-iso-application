from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from datetime import datetime
from io import BytesIO
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import requests
import json

app = Flask(__name__)
CORS(app)

# 핵심두뇌 API 설정
CORE_BRAIN_API_URL = "http://127.0.0.1:5001"

def call_core_brain_api(application_data):
    """핵심두뇌 API를 호출하여 정확한 계산 결과를 가져옵니다."""
    try:
        # 신청서 데이터를 핵심두뇌 API 형식으로 변환
        api_data = convert_application_to_api_format(application_data)
        
        print(f"핵심두뇌 API 호출: {api_data['client_name']}")
        
        # 핵심두뇌 API 호출
        response = requests.post(
            f"{CORE_BRAIN_API_URL}/calculate-audit-days",
            headers={"Content-Type": "application/json"},
            json=api_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"핵심두뇌 API 성공: {result.get('total_audit_days', 'N/A')}일")
            return result
        else:
            print(f"핵심두뇌 API 오류: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"핵심두뇌 API 연결 오류: {e}")
        return None
    except Exception as e:
        print(f"핵심두뇌 API 처리 오류: {e}")
        return None

def convert_application_to_api_format(application_data):
    """신청서 데이터를 핵심두뇌 API 형식으로 변환합니다."""
    # ISO 표준 파싱
    iso_standards = application_data.get('ISO표준', 'ISO 9001')
    standards_list = [s.strip() for s in iso_standards.split(',')]
    
    # 핵심두뇌 API 형식으로 변환
    api_data = {
        "client_name": application_data.get('법인명(국문)', 'Unknown'),
        "sites": [{
            "name": application_data.get('법인명(국문)', '본사'),
            "address": application_data.get('본사주소', '서울시 강남구'),
            "standards": standards_list,
            "total_headcount": int(application_data.get('총직원수', 30)),
            "part_time_count": int(application_data.get('비정규직수', 0)),
            "contractor_count": int(application_data.get('협력업체직원수', 0)),
            "shift_workers": int(application_data.get('교대근무자수', 0)),
            "seasonal_factor": 1.0,
            "site_type": "PERMANENT",
            "is_headquarters": True,
            "is_sampled": True,
            "sampling_priority": 1,
            "complexity_score": 5.0,
            "risk_level": "MEDIUM",
            "business_sector": "MANUFACTURING",
            "geographical_region": "DOMESTIC",
            "management_system_maturity": "MEDIUM",
            "repetitive_process": False,
            "remote_audit_ratio": 0.0
        }],
        "standards": standards_list,
        "options": {
            "stage1": True,
            "stage2": True,
            "surveillance": True,
            "recert": True
        }
    }
    
    return api_data

# Jinja2 필터 및 함수 정의
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

def format_date(value, format_str='%Y년 %m월 %d일'):
    """날짜 형식으로 포맷팅"""
    if value is None:
        return ""
    try:
        if isinstance(value, str):
            # 문자열인 경우 datetime으로 파싱 시도
            from datetime import datetime
            if len(value) == 8 and value.isdigit():  # YYYYMMDD 형식
                dt = datetime.strptime(value, '%Y%m%d')
            else:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            dt = value
        return dt.strftime(format_str)
    except (ValueError, TypeError, AttributeError):
        return str(value)

def format_boolean(value, true_text="예", false_text="아니오"):
    """불린 값을 한글로 변환"""
    if value is None:
        return false_text
    return true_text if bool(value) else false_text

def safe_divide(dividend, divisor, default=0):
    """안전한 나눗셈 (0으로 나누기 방지)"""
    try:
        if divisor == 0 or divisor is None:
            return default
        return float(dividend) / float(divisor)
    except (ValueError, TypeError):
        return default

# DocxTemplate 클래스를 상속받아서 필터와 함수를 미리 등록
class CustomDocxTemplate(DocxTemplate):
    def __init__(self, tpl_path):
        super().__init__(tpl_path)
        # Jinja2 환경에 필터와 함수 등록
        try:
            if hasattr(self, 'jinja_env') and self.jinja_env is not None:
                # 필터 등록
                self.jinja_env.filters.update({
                    'format_currency': format_currency,
                    'format_number': format_number,
                    'format_date': format_date,
                    'format_boolean': format_boolean,
                    'safe_divide': safe_divide
                })
                
                # 전역 함수 등록
                self.jinja_env.globals.update({
                    'format_currency': format_currency,
                    'format_number': format_number,
                    'format_date': format_date,
                    'format_boolean': format_boolean,
                    'safe_divide': safe_divide
                })
                
                print("CustomDocxTemplate: Jinja2 필터 및 함수 등록 완료")
            else:
                print("CustomDocxTemplate: jinja_env가 없음")
        except Exception as e:
            print(f"CustomDocxTemplate: 필터 등록 실패 - {e}")
    
    def render_with_error_handling(self, context):
        """오류 처리가 포함된 템플릿 렌더링"""
        try:
            # 컨텍스트 검증
            self._validate_context(context)
            
            # 템플릿 렌더링
            self.render(context)
            print("템플릿 렌더링 성공")
            return True
            
        except Exception as e:
            print(f"템플릿 렌더링 오류: {e}")
            print(f"컨텍스트 키들: {list(context.keys()) if context else 'None'}")
            
            # 누락된 변수 찾기
            self._find_missing_variables(context)
            return False
    
    def _validate_context(self, context):
        """컨텍스트 유효성 검사"""
        required_vars = [
            'client_name', 'quotation_date', 'quotation_number',
            'total_audit_days', 'total_cost'
        ]
        
        missing_vars = [var for var in required_vars if var not in context or context[var] is None]
        if missing_vars:
            print(f"경고: 필수 변수가 누락되었습니다: {missing_vars}")
    
    def _find_missing_variables(self, context):
        """템플릿에서 사용되는 변수와 컨텍스트 변수 비교"""
        try:
            # 템플릿 소스에서 변수 추출 (간단한 정규식)
            import re
            template_source = str(self.jinja_env.get_template('document.xml').source)
            template_vars = set(re.findall(r'\{\{\s*([^}]+)\s*\}\}', template_source))
            context_vars = set(context.keys()) if context else set()
            
            missing_in_context = template_vars - context_vars
            extra_in_context = context_vars - template_vars
            
            if missing_in_context:
                print(f"템플릿에 있지만 컨텍스트에 없는 변수: {missing_in_context}")
            if extra_in_context:
                print(f"컨텍스트에 있지만 템플릿에 없는 변수: {extra_in_context}")
                
        except Exception as e:
            print(f"변수 비교 중 오류: {e}")

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
        
        # CustomDocxTemplate 사용 (Jinja2 필터 및 함수 포함)
        doc = CustomDocxTemplate(template_path)
        
        # 핵심두뇌 API 호출하여 정확한 계산 결과 가져오기
        core_brain_result = call_core_brain_api(application_data)
        
        if core_brain_result is None:
            print("핵심두뇌 API 호출 실패, 폴백 계산 사용")
            # 폴백: 간단한 계산
            total_employees = int(application_data.get('총직원수', 30))
            iso_standards = application_data.get('ISO표준', 'ISO 9001')
            standard_count = len([s for s in ['ISO 9001', 'ISO 14001', 'ISO 45001'] if s in iso_standards])
            
            base_days = max(2, total_employees // 20) * standard_count
            total_days = base_days + (standard_count - 1) * 0.5
            
            day_rate = 1400000.0
            total_cost = total_days * day_rate
            vat_amount = total_cost * 0.1
            final_cost = total_cost + vat_amount
            
            # 폴백용 breakdowns 생성
            breakdowns = []
            standards_list = [s.strip() for s in iso_standards.split(',')]
            for standard in standards_list:
                # 표준명 정규화 (소문자 -> 대문자)
                std_lower = standard.lower()
                if '9001' in std_lower:
                    normalized_standard = 'ISO9001'
                elif '14001' in std_lower:
                    normalized_standard = 'ISO14001'
                elif '45001' in std_lower:
                    normalized_standard = 'ISO45001'
                else:
                    normalized_standard = 'ISO9001'  # 기본값
                
                breakdowns.append({
                    'standard': normalized_standard,
                    'stage1_days': 1.0,
                    'stage2_days': 1.0,
                    'surveillance_days': 1.0,
                    'recert_days': 1.0,
                    'total_initial_days': 2.0
                })
        else:
            # 핵심두뇌 API 결과 사용
            total_days = core_brain_result.get('total_audit_days', 0)
            breakdowns = core_brain_result.get('breakdowns', [])
            
            # 비용 계산 (핵심두뇌는 일수만 계산하므로 비용은 별도 계산)
            day_rate = 1400000.0
            total_cost = total_days * day_rate
            vat_amount = total_cost * 0.1
            final_cost = total_cost + vat_amount
            
            print(f"핵심두뇌 결과 사용: {total_days}일, {len(breakdowns)}개 표준")
        
        # 데이터 준비
        client_name = application_data.get('법인명(국문)', '알 수 없음')
        client_name_en = application_data.get('법인명(영문)', 'Unknown')
        client_address = application_data.get('본사주소', '주소 미입력')
        quotation_date = datetime.now().strftime('%Y년 %m월 %d일')
        quotation_number = f"LRQA-{datetime.now().strftime('%Y%m%d')}-{hash(client_name) % 10000:04d}"
        standards = [s.strip() for s in iso_standards.split(',')]
        standards_text = ', '.join(standards)
        
        # 핵심두뇌 API 결과에서 표준별 데이터 추출
        iso9001_breakdown = None
        iso14001_breakdown = None
        iso45001_breakdown = None
        
        for breakdown in breakdowns:
            standard = breakdown.get('standard', '').upper()
            if '9001' in standard:
                iso9001_breakdown = breakdown
            elif '14001' in standard:
                iso14001_breakdown = breakdown
            elif '45001' in standard:
                iso45001_breakdown = breakdown
        
        # ISO 표준 선택 여부 확인
        has_iso9001 = iso9001_breakdown is not None
        has_iso14001 = iso14001_breakdown is not None
        has_iso45001 = iso45001_breakdown is not None
        
        # 핵심두뇌 API 결과에서 일수 추출
        iso9001_stage1_days = iso9001_breakdown.get('stage1_days', 0) if iso9001_breakdown else 0
        iso9001_stage2_days = iso9001_breakdown.get('stage2_days', 0) if iso9001_breakdown else 0
        iso9001_stage1_2_days = iso9001_stage1_days + iso9001_stage2_days
        iso9001_surveillance_days = iso9001_breakdown.get('surveillance_days', 0) if iso9001_breakdown else 0
        
        iso14001_stage1_days = iso14001_breakdown.get('stage1_days', 0) if iso14001_breakdown else 0
        iso14001_stage2_days = iso14001_breakdown.get('stage2_days', 0) if iso14001_breakdown else 0
        iso14001_stage1_2_days = iso14001_stage1_days + iso14001_stage2_days
        iso14001_surveillance_days = iso14001_breakdown.get('surveillance_days', 0) if iso14001_breakdown else 0
        
        iso45001_stage1_days = iso45001_breakdown.get('stage1_days', 0) if iso45001_breakdown else 0
        iso45001_stage2_days = iso45001_breakdown.get('stage2_days', 0) if iso45001_breakdown else 0
        iso45001_stage1_2_days = iso45001_stage1_days + iso45001_stage2_days
        iso45001_surveillance_days = iso45001_breakdown.get('surveillance_days', 0) if iso45001_breakdown else 0
        
        # 비용 계산 (핵심두뇌 일수 기반)
        iso9001_stage1_2_cost = iso9001_stage1_2_days * day_rate
        iso14001_stage1_2_cost = iso14001_stage1_2_days * day_rate
        iso45001_stage1_2_cost = iso45001_stage1_2_days * day_rate
        
        # 여행비 (간단한 계산)
        travel_expense = 500000  # 50만원
        total_cost_with_travel = total_cost + travel_expense
        
        # 디버깅 정보
        total_employees = int(application_data.get('총직원수', 30))
        print(f"견적서 생성: {client_name}, {standards}, {total_employees}명")
        print(f"ISO 표준 선택: 9001={has_iso9001}, 14001={has_iso14001}, 45001={has_iso45001}")
        print(f"핵심두뇌 일수: 9001={iso9001_stage1_2_days}일, 14001={iso14001_stage1_2_days}일, 45001={iso45001_stage1_2_days}일")
        print(f"총 심사일수: {total_days}일, 총 비용: {total_cost:,.0f}원")
        
        # Jinja2 템플릿 컨텍스트 (원시 데이터 제공, 필터는 템플릿에서 사용)
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
            
            # 기본 계산값 (원시 데이터)
            'total_cost': total_cost,
            'vat_amount': vat_amount,
            'final_cost': final_cost,
            'total_audit_days': total_days,
            'day_rate': day_rate,
            
            # ISO 9001 관련 (원시 데이터)
            'iso9001_stage1_days': iso9001_stage1_days,
            'iso9001_stage2_days': iso9001_stage2_days,
            'iso9001_stage1_2_days': iso9001_stage1_2_days,
            'iso9001_surveillance_days': iso9001_surveillance_days,
            'iso9001_stage1_2_cost': iso9001_stage1_2_cost,
            
            # ISO 14001 관련 (원시 데이터)
            'iso14001_stage1_days': iso14001_stage1_days,
            'iso14001_stage2_days': iso14001_stage2_days,
            'iso14001_stage1_2_days': iso14001_stage1_2_days,
            'iso14001_surveillance_days': iso14001_surveillance_days,
            'iso14001_stage1_2_cost': iso14001_stage1_2_cost,
            
            # ISO 45001 관련 (원시 데이터)
            'iso45001_stage1_days': iso45001_stage1_days,
            'iso45001_stage2_days': iso45001_stage2_days,
            'iso45001_stage1_2_days': iso45001_stage1_2_days,
            'iso45001_surveillance_days': iso45001_surveillance_days,
            'iso45001_stage1_2_cost': iso45001_stage1_2_cost,
            
            # 기타 비용 (원시 데이터)
            'travel_expense': travel_expense,
            'total_cost_with_travel': total_cost_with_travel,
            
            # Jinja2 템플릿에서 사용할 수 있는 추가 데이터
            'breakdowns': core_brain_result.get('breakdowns', []) if core_brain_result else [],
            'assumptions': core_brain_result.get('assumptions', []) if core_brain_result else [],
            
            # 디버깅용 메타데이터
            'debug_info': {
                'api_success': core_brain_result is not None,
                'calculation_method': 'core_brain' if core_brain_result else 'fallback',
                'generated_at': datetime.now().isoformat()
            }
        }
        
        print(f"Jinja2 컨텍스트 생성 완료: {len(context)}개 변수")
        print(f"디버깅 정보: {context['debug_info']}")
        
        # Jinja2 오류 처리가 포함된 템플릿 렌더링
        if not doc.render_with_error_handling(context):
            return jsonify({'error': '템플릿 렌더링 중 오류가 발생했습니다. 로그를 확인해주세요.'}), 500
        
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
    import os
    os.environ.pop('FLASK_ENV', None)  # FLASK_ENV 환경변수 제거
    app.run(debug=False, host='127.0.0.1', port=5000, load_dotenv=False)