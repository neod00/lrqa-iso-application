"""
LRQA 견적서 템플릿 기반 Word 문서 생성기
Jinja2 템플릿을 사용하여 LRQA_quotation.docx와 동일한 디자인으로 견적서 생성
"""

from docxtpl import DocxTemplate
from datetime import datetime
from typing import Dict, List, Any
import os
from jinja2 import Environment
from models import QuoteResult, ProgramBreakdown, Organization


class LRQAQuotationTemplate:
    """LRQA 견적서 템플릿 기반 생성기"""
    
    def __init__(self):
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates', 'LRQA_quotation.docx')
    
    def generate_quotation_docx(self, result: QuoteResult, output_path: str) -> str:
        """템플릿을 사용하여 견적서 Word 문서 생성"""
        try:
            # 템플릿 로드
            doc = DocxTemplate(self.template_path)
            
            # 템플릿 컨텍스트 데이터 준비
            context = self._prepare_template_context(result)
            
            # Jinja2 환경 설정 (커스텀 필터 추가)
            jinja_env = Environment()
            jinja_env.filters['format_currency'] = self._format_currency
            
            # 템플릿 렌더링
            doc.render(context, jinja_env)
            
            # 문서 저장
            doc.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"템플릿 기반 Word 문서 생성 실패: {str(e)}")
    
    def _format_currency(self, value: float) -> str:
        """통화 형식으로 포맷팅"""
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)
    
    def _prepare_template_context(self, result: QuoteResult) -> Dict[str, Any]:
        """템플릿 렌더링을 위한 컨텍스트 데이터 준비"""
        org = result.organization
        
        # 기본 정보
        context = {
            # 회사 정보
            'client_name': org.client_name,
            'client_name_en': org.client_name_en,
            'client_address': self._get_primary_address(org),
            'contact_person': self._get_contact_person(org),
            'contact_email': self._get_contact_email(org),
            'contact_phone': self._get_contact_phone(org),
            
            # 견적 정보
            'quotation_date': datetime.now().strftime('%Y년 %m월 %d일'),
            'quotation_number': f"LRQA-{datetime.now().strftime('%Y%m%d')}-{hash(org.client_name) % 10000:04d}",
            'valid_until': (datetime.now().replace(month=datetime.now().month + 3)).strftime('%Y년 %m월 %d일'),
            
            # 표준 정보
            'standards': [std.value for std in org.standards],
            'standards_text': ', '.join([std.value for std in org.standards]),
            
            # 개별 표준 확인 변수들
            'has_iso9001': any(std.value == 'ISO9001' for std in org.standards),
            'has_iso14001': any(std.value == 'ISO14001' for std in org.standards),
            'has_iso45001': any(std.value == 'ISO45001' for std in org.standards),
            'iso9001_name': 'ISO 9001 품질경영시스템',
            'iso14001_name': 'ISO 14001 환경경영시스템',
            'iso45001_name': 'ISO 45001 안전보건경영시스템',
            
            # 사업장 정보
            'sites': self._prepare_sites_data(org),
            'total_sites': len(org.sites),
            
            # 직원 정보
            'total_employees': sum(site.total_headcount for site in org.sites),
            'employee_breakdown': self._prepare_employee_breakdown(org),
            
            # 견적 상세
            'quotation_details': self._prepare_quotation_details(result),
            'total_audit_days': result.total_audit_days,
            
            # 최초심사 비용만 (Stage1 + Stage2, VAT 별도)
            'initial_audit_cost': sum((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns),
            'initial_audit_vat': sum((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns) * 0.1,
            
            # 기존 total_cost (모든 비용 포함)
            'total_cost': result.total_cost,
            'vat_amount': result.total_cost * 0.1,  # 10% VAT
            'subtotal': result.total_cost / 1.1,  # VAT 제외 금액
            
            # 독립적인 변수들 (루프 밖에서 사용)
            'surveillance_days': sum(bd.surveillance_days for bd in result.breakdowns),  # 총 Surveillance 일수
            'stage1_days': sum(bd.stage1_days for bd in result.breakdowns),  # 총 Stage1 일수
            'stage2_days': sum(bd.stage2_days for bd in result.breakdowns),  # 총 Stage2 일수
            'surveillance_cost': sum(bd.surveillance_days * 1400000 for bd in result.breakdowns),  # 총 Surveillance 비용
            'stage1_cost': sum(bd.stage1_days * 1400000 for bd in result.breakdowns),  # 총 Stage1 비용
            'stage2_cost': sum(bd.stage2_days * 1400000 for bd in result.breakdowns),  # 총 Stage2 비용
            
            # 개별 표준별 변수들 - Surveillance
            'iso9001_surveillance_days': next((bd.surveillance_days for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_surveillance_days': next((bd.surveillance_days for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_surveillance_days': next((bd.surveillance_days for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            'iso9001_surveillance_cost': next((bd.surveillance_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_surveillance_cost': next((bd.surveillance_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_surveillance_cost': next((bd.surveillance_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            
            # 개별 표준별 변수들 - Stage1
            'iso9001_stage1_days': next((bd.stage1_days for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_stage1_days': next((bd.stage1_days for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_stage1_days': next((bd.stage1_days for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            'iso9001_stage1_cost': next((bd.stage1_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_stage1_cost': next((bd.stage1_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_stage1_cost': next((bd.stage1_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            
            # 개별 표준별 변수들 - Stage2
            'iso9001_stage2_days': next((bd.stage2_days for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_stage2_days': next((bd.stage2_days for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_stage2_days': next((bd.stage2_days for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            'iso9001_stage2_cost': next((bd.stage2_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_stage2_cost': next((bd.stage2_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_stage2_cost': next((bd.stage2_days * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            
            
            # 개별 표준별 Stage1+Stage2 합산값 변수들
            'iso9001_stage1_2_days': next((bd.stage1_days + bd.stage2_days for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_stage1_2_days': next((bd.stage1_days + bd.stage2_days for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_stage1_2_days': next((bd.stage1_days + bd.stage2_days for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            'iso9001_stage1_2_cost': next(((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO9001'), 0),
            'iso14001_stage1_2_cost': next(((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO14001'), 0),
            'iso45001_stage1_2_cost': next(((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns if bd.standard.value == 'ISO45001'), 0),
            
            # 통합심사 정보
            'is_integrated': org.integration.is_integrated,
            'integration_discount': org.integration.get_integration_discount() * 100,
            
            # 원격심사 정보
            'remote_audit_ratio': org.options.remote_audit_ratio * 100,
            'remote_discount': min(org.options.remote_audit_ratio * 10, 10),
            
            # 제경비 (최초심사 비용의 10%)
            'travel_expense': int(sum((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns) * 0.1),
            
            # 제경비 포함 총 비용 (최초심사 + 제경비, VAT 별도)
            'total_cost_with_travel': int(sum((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns) + sum((bd.stage1_days + bd.stage2_days) * 1400000 for bd in result.breakdowns) * 0.1),
            
            # 가정 및 근거
            'assumptions': result.assumptions,
            'justification': result.justification,
            
            # 기타
            'created_at': result.created_at,
            'prepared_by': 'LRQA Korea',
            'prepared_title': '사업개발본부',
        }
        
        return context
    
    def _get_primary_address(self, org: Organization) -> str:
        """주요 주소 정보 반환"""
        if org.sites:
            return org.sites[0].address
        return ""
    
    def _get_contact_person(self, org: Organization) -> str:
        """담당자 정보 반환"""
        # 실제 구현에서는 연락처 정보를 Organization 모델에서 가져와야 함
        return "김아이폰 (대표이사)"
    
    def _get_contact_email(self, org: Organization) -> str:
        """담당자 이메일 반환"""
        return "kim.iphone@iphone-corp.co.kr"
    
    def _get_contact_phone(self, org: Organization) -> str:
        """담당자 전화번호 반환"""
        return "02-1234-5679"
    
    def _prepare_sites_data(self, org: Organization) -> List[Dict[str, Any]]:
        """사업장 데이터 준비"""
        sites_data = []
        for i, site in enumerate(org.sites, 1):
            sites_data.append({
                'number': i,
                'name': site.name,
                'address': site.address,
                'headcount': site.total_headcount,
                'standards': ', '.join([std.value for std in site.standards]),
                'activities': self._get_site_activities(site)
            })
        return sites_data
    
    def _get_site_activities(self, site) -> str:
        """사업장 활동 내용 반환"""
        # 실제 구현에서는 사업장별 활동 정보를 가져와야 함
        activity_map = {
            '본사': '스마트폰 제조 및 개발',
            '부산공장': '스마트폰 부품 제조',
            '대구지점': '고객 서비스 및 영업'
        }
        return activity_map.get(site.name, '제조업')
    
    def _prepare_employee_breakdown(self, org: Organization) -> Dict[str, int]:
        """직원 구성 데이터 준비"""
        total_employees = sum(site.total_headcount for site in org.sites)
        return {
            'total': total_employees,
            'permanent': int(total_employees * 0.88),  # 88% 정규직
            'temporary': int(total_employees * 0.06),  # 6% 비정규직
            'contractors': int(total_employees * 0.06),  # 6% 협력업체
        }
    
    def _prepare_quotation_details(self, result: QuoteResult) -> List[Dict[str, Any]]:
        """견적 상세 데이터 준비"""
        details = []
        
        for bd in result.breakdowns:
            details.append({
                'standard': bd.standard.value,
                'standard_name': self._get_standard_name(bd.standard.value),
                'enp': bd.enp,
                'complexity': bd.complexity.value,
                'stage1_days': bd.stage1_days,
                'stage2_days': bd.stage2_days,
                'surveillance_days': bd.surveillance_days,
                'total_days': bd.total_days,
                'stage1_cost': bd.stage1_days * 1400000,
                'stage2_cost': bd.stage2_days * 1400000,
                'surveillance_cost': bd.surveillance_days * 1400000,
                'total_cost': bd.total_days * 1400000,
            })
        
        return details
    
    def _get_standard_name(self, standard: str) -> str:
        """표준명 한글 변환"""
        name_map = {
            'ISO9001': 'ISO 9001 품질경영시스템',
            'ISO14001': 'ISO 14001 환경경영시스템',
            'ISO45001': 'ISO 45001 안전보건경영시스템'
        }
        return name_map.get(standard, standard)


# 편의 함수
def generate_lrqa_quotation_docx(result: QuoteResult, output_path: str) -> str:
    """LRQA 견적서 Word 문서 생성 (편의 함수)"""
    generator = LRQAQuotationTemplate()
    return generator.generate_quotation_docx(result, output_path)
