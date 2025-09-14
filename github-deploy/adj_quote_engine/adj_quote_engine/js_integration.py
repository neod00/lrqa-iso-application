"""
JavaScript 견적 시스템과의 연동 모듈

이 모듈은 기존 JavaScript 견적 시스템과 Python ADJ v2.2 엔진을 연동합니다.
JavaScript에서 전달받은 신청서 데이터를 Python 엔진으로 처리하고 결과를 반환합니다.
"""

import json
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime

from .models import Organization, Site, IntegrationInputs, Options, StandardType
from .adj_rules_v22 import quote_engine
from .pricing import pricing_calculator
from .quote_docx import docx_exporter


class JSIntegrationManager:
    """JavaScript 연동 관리자"""
    
    def __init__(self, python_path: str = "python"):
        """
        Args:
            python_path: Python 실행 파일 경로
        """
        self.python_path = python_path
        self.temp_dir = tempfile.gettempdir()
    
    def convert_js_to_python_data(self, js_data: Dict[str, Any]) -> Dict[str, Any]:
        """JavaScript 데이터를 Python 엔진 형식으로 변환"""
        try:
            # 기본 정보
            python_data = {
                "client_name": js_data.get('companyNameKo', js_data.get('companyName', 'Unknown')),
                "client_name_en": js_data.get('companyNameEn', ''),
                "standards": self._extract_standards(js_data),
                "sites": self._extract_sites(js_data),
                "integration": self._extract_integration(js_data),
                "options": self._extract_options(js_data)
            }
            
            return python_data
            
        except Exception as e:
            raise ValueError(f"JavaScript 데이터 변환 실패: {e}")
    
    def _extract_standards(self, js_data: Dict[str, Any]) -> list:
        """ISO 표준 추출"""
        standards = []
        
        # JavaScript에서 ISO 표준 정보 추출
        iso_standards = js_data.get('isoStandards', '')
        if isinstance(iso_standards, str):
            iso_standards = iso_standards.split(',')
        
        # 표준 매핑
        standard_mapping = {
            'iso9001': 'ISO9001',
            'iso14001': 'ISO14001', 
            'iso45001': 'ISO45001',
            'iso27001': 'ISO27001',
            'iso22000': 'ISO22000',
            'iso13485': 'ISO13485'
        }
        
        for std in iso_standards:
            std = std.strip().lower()
            if std in standard_mapping:
                standards.append(standard_mapping[std])
        
        return standards if standards else ['ISO9001']  # 기본값
    
    def _extract_sites(self, js_data: Dict[str, Any]) -> list:
        """사업장 정보 추출"""
        sites = []
        
        # 단일 사업장으로 가정 (향후 다중 사업장 지원 가능)
        site = {
            "name": "본사",
            "address": js_data.get('headOfficeAddress', ''),
            "standards": self._extract_standards(js_data),
            "total_headcount": self._safe_int(js_data.get('employee_총직원수', 0)),
            "part_time_count": self._safe_int(js_data.get('employee_비정규직수', 0)),
            "contractor_count": 0,  # JavaScript에서 제공하지 않음
            "shift_workers": 0,     # JavaScript에서 제공하지 않음
            "seasonal_factor": 1.0, # 기본값
            "repetitive_process": False,  # 기본값
            "remote_audit_ratio": 0.0    # 기본값
        }
        
        sites.append(site)
        return sites
    
    def _extract_integration(self, js_data: Dict[str, Any]) -> dict:
        """통합심사 정보 추출"""
        return {
            "is_integrated": js_data.get('standardIntegration', '').lower() == 'yes',
            "integration_level": 0.8 if js_data.get('standardIntegration', '').lower() == 'yes' else 0.0,
            "shared_management_system": True,  # 기본값
            "common_processes": True,          # 기본값
            "same_audit_team": True           # 기본값
        }
    
    def _extract_options(self, js_data: Dict[str, Any]) -> dict:
        """옵션 정보 추출"""
        return {
            "stage1": True,
            "stage2": True,
            "surveillance": True,
            "recert": False,
            "remote_audit_ratio": 0.0,
            "day_rate": 1300000.0,  # 기본 단가
            "vat_rate": 0.1         # 기본 VAT
        }
    
    def _safe_int(self, value: Any) -> int:
        """안전한 정수 변환"""
        try:
            return int(value) if value else 0
        except (ValueError, TypeError):
            return 0
    
    def calculate_quote_from_js(self, js_data: Dict[str, Any]) -> Dict[str, Any]:
        """JavaScript 데이터로부터 견적 계산"""
        try:
            # JavaScript 데이터를 Python 형식으로 변환
            python_data = self.convert_js_to_python_data(js_data)
            
            # Organization 객체 생성
            organization = self._create_organization_from_data(python_data)
            
            # 견적 계산
            result = quote_engine.calculate_quote(organization)
            result = pricing_calculator.calculate_quote_pricing(result)
            
            # JavaScript 형식으로 결과 변환
            return self._convert_result_to_js_format(result)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "견적 계산 중 오류가 발생했습니다."
            }
    
    def _create_organization_from_data(self, data: Dict[str, Any]) -> Organization:
        """데이터로부터 Organization 객체 생성"""
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
    
    def _convert_result_to_js_format(self, result) -> Dict[str, Any]:
        """Python 결과를 JavaScript 형식으로 변환"""
        try:
            # 표준별 breakdown 변환
            breakdowns = []
            for bd in result.breakdowns:
                breakdowns.append({
                    "standard": bd.standard.value,
                    "enp": bd.enp,
                    "complexity": bd.complexity.value,
                    "stage1_days": bd.stage1_days,
                    "stage2_days": bd.stage2_days,
                    "surveillance_days": bd.surveillance_days,
                    "recert_days": bd.recert_days,
                    "total_days": bd.total_days
                })
            
            return {
                "success": True,
                "data": {
                    "client_name": result.organization.client_name,
                    "standards": [std.value for std in result.organization.standards],
                    "total_audit_days": result.total_audit_days,
                    "subtotal_cost": result.subtotal_cost,
                    "vat_amount": result.vat_amount,
                    "total_cost": result.total_cost,
                    "day_rate": result.organization.options.day_rate,
                    "vat_rate": result.organization.options.vat_rate,
                    "breakdowns": breakdowns,
                    "assumptions": result.assumptions,
                    "justification": result.justification,
                    "created_at": result.created_at
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "결과 변환 중 오류가 발생했습니다."
            }
    
    def generate_word_document(self, js_data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Word 문서 생성"""
        try:
            # JavaScript 데이터로부터 견적 계산
            quote_result = self.calculate_quote_from_js(js_data)
            
            if not quote_result.get('success', False):
                return quote_result
            
            # Python 데이터로 변환
            python_data = self.convert_js_to_python_data(js_data)
            organization = self._create_organization_from_data(python_data)
            
            # 견적 계산
            result = quote_engine.calculate_quote(organization)
            result = pricing_calculator.calculate_quote_pricing(result)
            
            # Word 문서 생성
            success = docx_exporter.export_docx(result, output_path)
            
            if success:
                return {
                    "success": True,
                    "message": f"Word 문서가 생성되었습니다: {output_path}",
                    "file_path": output_path,
                    "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else 0
                }
            else:
                return {
                    "success": False,
                    "error": "Word 문서 생성 실패",
                    "message": "Word 문서 생성 중 오류가 발생했습니다."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Word 문서 생성 중 오류가 발생했습니다."
            }


# 전역 인스턴스
js_integration = JSIntegrationManager()
