"""
명령행 실행 진입점

이 모듈은 ADJ v2.2 견적 계산 엔진의 CLI 인터페이스를 제공합니다.
JSON 신청서 파일을 입력받아 견적을 계산하고 Word 문서로 출력합니다.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any
from datetime import datetime

from .models import (
    Organization, Site, IntegrationInputs, Options, 
    StandardType, QuoteResult
)
from .adj_rules_v22 import quote_engine
from .pricing import pricing_calculator
from .quote_docx import export_to_word


def load_json_input(file_path: str) -> Dict[str, Any]:
    """JSON 입력 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: JSON 파싱 오류: {e}")
        sys.exit(1)


def parse_organization(data: Dict[str, Any]) -> Organization:
    """JSON 데이터를 Organization 객체로 변환"""
    try:
        # 표준 변환
        standards = [StandardType(std) for std in data.get('standards', [])]
        
        # 사업장 변환
        sites = []
        for site_data in data.get('sites', []):
            site_standards = [StandardType(std) for std in site_data.get('standards', [])]
            site = Site(
                name=site_data['name'],
                address=site_data.get('address', ''),
                standards=site_standards,
                total_headcount=site_data.get('total_headcount', 0),
                part_time_count=site_data.get('part_time_count', 0),
                contractor_count=site_data.get('contractor_count', 0),
                shift_workers=site_data.get('shift_workers', 0),
                seasonal_factor=site_data.get('seasonal_factor', 1.0),
                repetitive_process=site_data.get('repetitive_process', False),
                remote_audit_ratio=site_data.get('remote_audit_ratio', 0.0)
            )
            sites.append(site)
        
        # 통합심사 정보
        integration_data = data.get('integration', {})
        integration = IntegrationInputs(
            is_integrated=integration_data.get('is_integrated', False),
            integration_level=integration_data.get('integration_level', 0.0),
            shared_management_system=integration_data.get('shared_management_system', False),
            common_processes=integration_data.get('common_processes', False),
            same_audit_team=integration_data.get('same_audit_team', False)
        )
        
        # 옵션
        options_data = data.get('options', {})
        options = Options(
            stage1=options_data.get('stage1', True),
            stage2=options_data.get('stage2', True),
            surveillance=options_data.get('surveillance', True),
            recert=options_data.get('recert', False),
            remote_audit_ratio=options_data.get('remote_audit_ratio', 0.0),
            day_rate=options_data.get('day_rate', 1300000.0),
            vat_rate=options_data.get('vat_rate', 0.1)
        )
        
        return Organization(
            client_name=data['client_name'],
            client_name_en=data.get('client_name_en'),
            sites=sites,
            standards=standards,
            integration=integration,
            options=options
        )
        
    except KeyError as e:
        print(f"Error: 필수 필드가 누락되었습니다: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: 잘못된 값입니다: {e}")
        sys.exit(1)


def print_quote_summary(result: QuoteResult):
    """견적 요약 출력"""
    print("\n" + "="*60)
    print("ISO 인증심사 견적서 요약")
    print("="*60)
    print(f"고객사: {result.organization.client_name}")
    print(f"적용 표준: {', '.join([std.value for std in result.organization.standards])}")
    print(f"사업장 수: {len(result.organization.sites)}개")
    print(f"총 심사일수: {result.total_audit_days} mandays")
    print(f"1 manday 단가: ₩{result.organization.options.day_rate:,.0f}")
    print(f"서브토탈: ₩{result.subtotal_cost:,.0f}")
    print(f"VAT ({result.organization.options.vat_rate*100:.1f}%): ₩{result.vat_amount:,.0f}")
    print(f"총 견적 금액: ₩{result.total_cost:,.0f}")
    print("="*60)
    
    # 표준별 breakdown
    print("\n표준별 심사일수:")
    print("-" * 40)
    for breakdown in result.breakdowns:
        print(f"{breakdown.standard.value}:")
        print(f"  ENP: {breakdown.enp}명")
        print(f"  복잡도: {breakdown.complexity.value}")
        print(f"  Stage1: {breakdown.stage1_days}일")
        print(f"  Stage2: {breakdown.stage2_days}일")
        print(f"  Surveillance: {breakdown.surveillance_days}일")
        print(f"  Recert: {breakdown.recert_days}일")
        print(f"  총계: {breakdown.total_days}일")
        print()


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='ADJ v2.2 기반 ISO 인증심사 견적 계산기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python -m adj_quote_engine.cli --input sample.json --output quotation.docx
  python -m adj_quote_engine.cli --input sample.json --output quotation.docx --day-rate 1500000
  python -m adj_quote_engine.cli --input sample.json --output quotation.docx --vat-rate 0.1

JSON 입력 파일 형식:
{
  "client_name": "ACME Corp",
  "client_name_en": "ACME Corporation",
  "standards": ["ISO9001", "ISO14001"],
  "sites": [
    {
      "name": "본사",
      "address": "서울시 강남구",
      "standards": ["ISO9001", "ISO14001"],
      "total_headcount": 120,
      "part_time_count": 10,
      "contractor_count": 5,
      "shift_workers": 20,
      "seasonal_factor": 1.0,
      "repetitive_process": false,
      "remote_audit_ratio": 0.0
    }
  ],
  "integration": {
    "is_integrated": true,
    "shared_management_system": true,
    "common_processes": true,
    "same_audit_team": true
  },
  "options": {
    "stage1": true,
    "stage2": true,
    "surveillance": true,
    "recert": false,
    "day_rate": 1300000,
    "vat_rate": 0.1
  }
}
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='입력 JSON 파일 경로'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='출력 Word 문서 경로'
    )
    
    parser.add_argument(
        '--day-rate',
        type=float,
        default=1300000.0,
        help='1 manday 단가 (기본: 1,300,000 KRW)'
    )
    
    parser.add_argument(
        '--vat-rate',
        type=float,
        default=0.1,
        help='VAT 비율 (기본: 0.1 = 10%)'
    )
    
    parser.add_argument(
        '--template',
        help='Word 템플릿 파일 경로 (선택사항)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 출력'
    )
    
    args = parser.parse_args()
    
    # 입력 파일 로드
    if args.verbose:
        print(f"입력 파일 로딩: {args.input}")
    
    data = load_json_input(args.input)
    
    # Organization 객체 생성
    if args.verbose:
        print("데이터 파싱 중...")
    
    organization = parse_organization(data)
    
    # 옵션 오버라이드
    organization.options.day_rate = args.day_rate
    organization.options.vat_rate = args.vat_rate
    
    # 견적 계산
    if args.verbose:
        print("견적 계산 중...")
    
    result = quote_engine.calculate_quote(organization)
    
    # 비용 계산
    result = pricing_calculator.calculate_quote_pricing(result)
    
    # 콘솔 출력
    print_quote_summary(result)
    
    # Word 문서 생성
    if args.verbose:
        print(f"Word 문서 생성 중: {args.output}")
    
    success = export_to_word(result, args.output)
    
    if success:
        print(f"\n견적서가 성공적으로 생성되었습니다: {args.output}")
        
        # 파일 크기 출력
        if os.path.exists(args.output):
            file_size = os.path.getsize(args.output)
            print(f"파일 크기: {file_size:,} bytes")
    else:
        print("Error: Word 문서 생성에 실패했습니다.")
        sys.exit(1)


if __name__ == '__main__':
    main()
