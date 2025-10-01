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
# from adj_quote_engine.calculator import QuoteCalculator  # 임시 주석 처리
from adj_quote_engine.quote_template import LRQAQuotationTemplate

app = Flask(__name__)
CORS(app, origins=['*'], allow_headers=['Content-Type'], methods=['GET', 'POST', 'OPTIONS'])  # CORS 허용

def generate_advanced_html_report(gap_result, company_name):
    """Apple 보고서 스타일의 고급 HTML 보고서 생성"""
    
    # 표준명 매핑
    standard_names = {
        'iso9001': 'ISO 9001:2015 (품질경영시스템)',
        'iso14001': 'ISO 14001:2016 (환경경영시스템)', 
        'iso45001': 'ISO 45001:2018 (안전보건경영시스템)'
    }
    
    # 표준 목록 생성
    standards_list = []
    for std in gap_result.get('standards', []):
        if isinstance(std, dict) and 'standard' in std:
            standards_list.append(standard_names.get(std['standard'], std['standard']))
        elif isinstance(std, str):
            standards_list.append(standard_names.get(std, std))
    standards_text = ', '.join(standards_list)
    
    # 갭 분석 섹션 생성
    gap_analysis_html = ""
    if 'standards' in gap_result:
        for std in gap_result['standards']:
            if isinstance(std, dict) and 'standard' in std:
                standard_name = standard_names.get(std['standard'], std['standard'])
                readiness = std.get('readiness', 'Unknown')
                current_score = std.get('currentScore', 0)
                gap = std.get('gap', 0)
                
                gap_analysis_html += f"""
                <div class="gap-category category-{'a' if gap > 20 else 'b' if gap > 10 else 'c'}">
                    <div class="gap-header">
                        {standard_name} - {readiness} (현재 점수: {current_score}/100, 갭: {gap})
                    </div>
                    <div class="gap-content">
                        <div class="gap-item">
                            <div class="gap-item-title">주요 개선 영역</div>
                            <div class="gap-item-description">
                                {' '.join(std.get('criticalGaps', ['분석 중...']))}
                            </div>
                        </div>
                        <div class="gap-item">
                            <div class="gap-item-title">권장사항</div>
                            <div class="gap-item-description">
                                {' '.join(std.get('recommendations', ['분석 중...']))}
                            </div>
                        </div>
                    </div>
                </div>
                """
    
    # 전체 HTML 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - AI 통합 ISO 경영시스템 표준 갭분석 보고서</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            font-size: 14px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 20px auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .header {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            border-bottom: 4px solid #3498db;
            position: relative;
        }}
        
        .logo-container {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }}
        
        .lrqa-logo {{
            height: 50px;
            width: auto;
        }}
        
        .apple-logo {{
            color: #ffffff;
            font-size: 36px;
            font-weight: 300;
        }}
        
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .meta-info {{
            background: #ecf0f1;
            padding: 20px 30px;
            border-bottom: 2px solid #bdc3c7;
        }}
        
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .meta-item {{
            display: flex;
            flex-direction: column;
        }}
        
        .meta-label {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 5px;
            font-weight: 600;
        }}
        
        .meta-value {{
            font-size: 14px;
            font-weight: 500;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
        }}
        
        .gap-category {{
            background: #ffffff;
            border: 2px solid #e74c3c;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .gap-category.category-a {{
            border-color: #e74c3c;
        }}
        
        .gap-category.category-b {{
            border-color: #f39c12;
        }}
        
        .gap-category.category-c {{
            border-color: #f1c40f;
        }}
        
        .gap-header {{
            padding: 15px 20px;
            font-weight: 600;
            color: white;
        }}
        
        .gap-category.category-a .gap-header {{
            background: #e74c3c;
        }}
        
        .gap-category.category-b .gap-header {{
            background: #f39c12;
        }}
        
        .gap-category.category-c .gap-header {{
            background: #f1c40f;
            color: #2c3e50;
        }}
        
        .gap-content {{
            padding: 20px;
        }}
        
        .gap-item {{
            margin-bottom: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        
        .gap-item-title {{
            font-weight: 600;
            margin-bottom: 8px;
            color: #2c3e50;
        }}
        
        .gap-item-description {{
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 10px;
        }}
        
        .apple-insight {{
            background: #e8f4f8;
            border: 2px solid #3498db;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        
        .apple-insight h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px 30px;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .footer-logo {{
            height: 30px;
            width: auto;
        }}
        
        @media print {{
            body {{ font-size: 12px; }}
            .container {{ box-shadow: none; margin: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo-container">
                <img src="../lrqa-logo.png" alt="LRQA 로고" class="lrqa-logo">
                <div class="apple-logo">🍎</div>
            </div>
            <h1>사전평가 갭분석 보고서</h1>
            <div class="subtitle">ISO 경영시스템 표준 갭분석 - {company_name} (AI 통합)</div>
        </div>
        
        <!-- Meta Information -->
        <div class="meta-info">
            <div class="meta-grid">
                <div class="meta-item">
                    <div class="meta-label">고객 조직</div>
                    <div class="meta-value">{company_name}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">평가 표준</div>
                    <div class="meta-value">{standards_text}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">평가 일자</div>
                    <div class="meta-value">{datetime.now().strftime('%Y년 %m월 %d일')}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">LRQA 참조번호</div>
                    <div class="meta-value">GAP-2025-{company_name.replace(' ', '-').upper()}-IMS-001</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">평가팀</div>
                    <div class="meta-value">수석심사원: LRQA 공인심사원</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">고객 담당자</div>
                    <div class="meta-value">최고경영진 / 품질담당자</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <!-- Executive Summary -->
            <div class="section">
                <div class="section-title">1. 경영진 요약</div>
                <p>본 사전평가 갭분석은 {company_name}을 대상으로 {standards_text} 요구사항에 대하여 수행되었습니다. 본 평가는 LRQA의 검증된 6단계 갭분석 방법론과 AI 웹사이트 분석을 통합하여 정식 인증심사 이전에 주의가 필요한 잠재적 영역을 식별하였습니다.</p>
                
                <div class="apple-insight">
                    <h3>🎯 {company_name} 특화 분석</h3>
                    <p><strong>조직 규모:</strong> {gap_result.get('summary', {}).get('totalEmployees', 'N/A')}명 직원</p>
                    <p><strong>핵심 강점:</strong> 기본적인 조직 구조 구축, 품질에 대한 인식 개선 필요, 고객 만족도 향상 의지</p>
                    <p><strong>특별 고려사항:</strong> 기존 우수성을 ISO 공식 요구사항과 체계적 정렬, 시너지를 위한 경영시스템 통합, 비공식적 우수성을 체계적 프로세스로 문서화</p>
                </div>
            </div>
            
            <!-- Gap Analysis -->
            <div class="section">
                <div class="section-title">4. LRQA 카테고리별 갭 분석</div>
                <p>다음의 잠재적 부적합사항들이 LRQA의 검증된 분류 방법론과 AI 웹사이트 분석을 사용하여 식별되었습니다:</p>
                
                {gap_analysis_html}
            </div>
            
            <!-- Recommendations -->
            <div class="section">
                <div class="section-title">7. LRQA 전문가 권고사항</div>
                <div class="recommendations">
                    {' '.join([f'<div class="gap-item"><div class="gap-item-title">{rec}</div></div>' for rec in gap_result.get('recommendations', [])])}
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div>
                <p><strong>LRQA 비즈니스 어슈어런스</strong> | 통합경영시스템 갭분석 보고서 (AI 통합)</p>
                <p>보고서 생성: {datetime.now().strftime('%Y년 %m월 %d일')} | 참조번호: GAP-2025-{company_name.replace(' ', '-').upper()}-IMS-001 | 1/1 페이지</p>
                <p>본 보고서는 www.lrqa.com에서 확인 가능한 LRQA 일반 이용약관에 따라 발행됩니다</p>
            </div>
            <img src="../lrqa-logo-black.png" alt="LRQA 로고" class="footer-logo">
        </div>
    </div>
</body>
</html>"""
    
    return html_content

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
        
        # 2. adj_quote_engine으로 정교한 계산 (임시 주석 처리)
        # calculator = QuoteCalculator()
        # calculated_result = calculator.calculate_quotation(quote_result)
        calculated_result = quote_result  # 임시로 원본 데이터 사용
        
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

@app.route('/api/gap-analysis', methods=['POST'])
def generate_gap_analysis():
    """고급 갭분석 보고서 생성 API"""
    try:
        data = request.json
        form_data = data.get('formData', {})
        selected_standards = data.get('selectedStandards', [])
        
        # 갭분석 데이터 준비
        gap_analysis_data = {
            'companyName': form_data.get('companyNameKo') or form_data.get('companyNameEn') or 'Unknown Company',
            'selectedISOStandards': selected_standards,
            'totalEmployees': int(form_data.get('totalEmployees', 0)),
            'companyWebsite': form_data.get('companyWebsite', ''),
            'contactEmail': form_data.get('contactEmail', ''),
            'contactName': form_data.get('contactName', ''),
            'companyAddress': form_data.get('companyAddress', ''),
            'industry': form_data.get('industry', '')
        }
        
        # 기존 갭분석 엔진 호출
        from adj_quote_engine.gap_analysis import generate_gap_analysis_report
        gap_result = generate_gap_analysis_report(gap_analysis_data)
        
        # 고급 HTML 보고서 생성
        report_html = generate_advanced_html_report(gap_result, gap_analysis_data['companyName'])
        
        return jsonify({
            'success': True,
            'data': {
                'reportHtml': report_html,
                'gapAnalysis': gap_result,
                'companyName': gap_analysis_data['companyName']
            }
        })
        
    except Exception as e:
        print(f"갭분석 생성 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/save-gap-analysis-report', methods=['POST'])
def save_gap_analysis_report():
    """갭분석 보고서를 sample-reports 폴더에 저장하는 API"""
    try:
        data = request.json
        report_html = data['reportHtml']
        company_name = data['companyName']
        
        # sample-reports 폴더 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sample_reports_dir = os.path.join(parent_dir, 'sample-reports')
        
        # sample-reports 폴더가 없으면 생성
        if not os.path.exists(sample_reports_dir):
            os.makedirs(sample_reports_dir)
        
        # 파일명 생성 (Apple_Inc_AI_통합_갭분석보고서_2025.html 형태)
        current_date = datetime.now().strftime('%Y')
        filename = f"{company_name}_AI_통합_갭분석보고서_{current_date}.html"
        file_path = os.path.join(sample_reports_dir, filename)
        
        # HTML 파일 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        print(f"갭분석 보고서 저장 완료: {file_path}")
        
        return jsonify({
            'success': True, 
            'message': '갭분석 보고서가 sample-reports 폴더에 저장되었습니다.',
            'filePath': file_path,
            'filename': filename
        })
        
    except Exception as e:
        print(f"갭분석 보고서 저장 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'message': '갭분석 보고서 저장 중 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    # .env 파일 로드 비활성화
    import os
    os.environ.pop('FLASK_APP', None)
    os.environ.pop('FLASK_ENV', None)
    # dotenv 로딩 비활성화
    import flask.cli
    flask.cli.load_dotenv = lambda *args, **kwargs: None
    app.run(debug=True, host='0.0.0.0', port=5000)
