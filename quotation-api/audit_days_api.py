from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# 핵심두뇌 import
sys.path.append(os.path.join(os.path.dirname(__file__), 'adj_quote_engine'))
from adj_quote_engine.models import Organization, Site, StandardType, Options, SiteType, MultiSiteConfiguration
from adj_quote_engine.adj_rules_v22 import QuoteEngine

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': '핵심두뇌 API 서버가 실행 중입니다'})

@app.route('/calculate-audit-days', methods=['POST'])
def calculate_audit_days():
    """핵심두뇌를 사용한 심사일수 계산 API"""
    try:
        data = request.json
        print(f"심사일수 계산 요청: {data.get('client_name', 'Unknown')}")
        
        # 요청 데이터 파싱
        client_name = data.get('client_name', 'Unknown')
        sites_data = data.get('sites', [])
        standards = data.get('standards', ['ISO9001'])
        options = data.get('options', {})
        
        # Site 객체 생성
        sites = []
        for site_data in sites_data:
            site = Site(
                name=site_data.get('name', 'Unknown'),
                address=site_data.get('address', ''),
                standards=[StandardType[s] for s in site_data.get('standards', ['ISO9001'])],
                total_headcount=site_data.get('total_headcount', 0),
                business_sector=site_data.get('business_sector', 'MANUFACTURING'),
                management_system_maturity=site_data.get('management_system_maturity', 'MEDIUM')
            )
            sites.append(site)
        
        # Organization 객체 생성
        organization = Organization(
            client_name=client_name,
            sites=sites,
            standards=[StandardType[s] for s in standards],
            options=Options(
                stage1=options.get('stage1', True),
                stage2=options.get('stage2', True),
                surveillance=options.get('surveillance', True),
                recert=options.get('recert', True)
            )
        )
        
        # 핵심두뇌로 계산
        engine = QuoteEngine('standard')
        result = engine.calculate_quote(organization)
        
        # 결과 반환
        response = {
            'success': True,
            'client_name': client_name,
            'total_audit_days': result.total_audit_days,
            'breakdowns': []
        }
        
        for breakdown in result.breakdowns:
            breakdown_data = {
                'standard': breakdown.standard.value,
                'enp': breakdown.enp,
                'stage1_days': breakdown.stage1_days,
                'stage2_days': breakdown.stage2_days,
                'surveillance_days': breakdown.surveillance_days,
                'recert_days': breakdown.recert_days,
                'total_initial_days': breakdown.stage1_days + breakdown.stage2_days
            }
            response['breakdowns'].append(breakdown_data)
        
        response['assumptions'] = result.assumptions
        
        return jsonify(response)
        
    except Exception as e:
        print(f"오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'message': '심사일수 계산 중 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    print("핵심두뇌 API 서버 시작...")
    print("포트: 5001")
    app.run(debug=True, host='127.0.0.1', port=5001)
