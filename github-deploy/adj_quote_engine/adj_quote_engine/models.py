"""
ADJ v2.2 견적 계산 엔진 데이터 모델

이 모듈은 견적 계산에 필요한 모든 데이터 구조를 정의합니다.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class StandardType(Enum):
    """ISO 표준 타입"""
    ISO9001 = "ISO9001"
    ISO14001 = "ISO14001" 
    ISO45001 = "ISO45001"
    ISO27001 = "ISO27001"
    ISO22000 = "ISO22000"
    ISO13485 = "ISO13485"


class ComplexityLevel(Enum):
    """복잡도 레벨"""
    SMALL = "S"      # Small
    MEDIUM = "M"     # Medium  
    LARGE = "L"      # Large
    HIGH = "H"       # High (ISO 14001, 45001)
    LOW = "LOW"      # Low (ISO 14001, 45001)
    LIMITED = "LIM"  # Limited (ISO 14001)


class StageType(Enum):
    """심사 단계"""
    STAGE1 = "Stage1"           # 1단계 심사
    STAGE2 = "Stage2"           # 2단계 심사
    SURVEILLANCE = "Surveillance"  # 감시심사
    RECERT = "Recert"           # 갱신심사


@dataclass
class Site:
    """사업장별 입력 정보"""
    name: str
    address: str
    standards: List[StandardType]
    total_headcount: int = 0
    part_time_count: int = 0
    contractor_count: int = 0
    shift_workers: int = 0
    seasonal_factor: float = 1.0
    repetitive_process: bool = False
    remote_audit_ratio: float = 0.0
    
    def __post_init__(self):
        """데이터 검증"""
        if self.total_headcount < 0:
            raise ValueError("총 직원수는 0 이상이어야 합니다")
        if not 0 <= self.remote_audit_ratio <= 1.0:
            raise ValueError("원격심사 비율은 0~1 사이여야 합니다")
        if self.seasonal_factor < 1.0:
            raise ValueError("계절성 가중치는 1.0 이상이어야 합니다")


@dataclass
class IntegrationInputs:
    """통합심사 입력 정보"""
    is_integrated: bool = False
    integration_level: float = 0.0  # 0.0 ~ 1.0 (통합 정도)
    shared_management_system: bool = False
    common_processes: bool = False
    same_audit_team: bool = False
    
    def get_integration_discount(self) -> float:
        """통합심사 할인율 계산 (최대 10%)"""
        if not self.is_integrated:
            return 0.0
        
        discount = 0.0
        if self.shared_management_system:
            discount += 0.03
        if self.common_processes:
            discount += 0.04
        if self.same_audit_team:
            discount += 0.03
            
        return min(discount, 0.10)  # 최대 10%


@dataclass
class Options:
    """심사 옵션"""
    stage1: bool = True
    stage2: bool = True
    surveillance: bool = True
    recert: bool = False
    remote_audit_ratio: float = 0.0
    day_rate: float = 1300000.0  # 1 manday 단가 (KRW)
    vat_rate: float = 0.1        # VAT 비율 (10%)
    
    def __post_init__(self):
        """데이터 검증"""
        if not 0 <= self.remote_audit_ratio <= 1.0:
            raise ValueError("원격심사 비율은 0~1 사이여야 합니다")
        if self.day_rate <= 0:
            raise ValueError("일당은 0보다 커야 합니다")
        if not 0 <= self.vat_rate <= 1.0:
            raise ValueError("VAT 비율은 0~1 사이여야 합니다")


@dataclass
class Organization:
    """전체 고객사 정보"""
    client_name: str
    client_name_en: Optional[str] = None
    sites: List[Site] = field(default_factory=list)
    standards: List[StandardType] = field(default_factory=list)
    integration: IntegrationInputs = field(default_factory=IntegrationInputs)
    options: Options = field(default_factory=Options)
    
    def __post_init__(self):
        """데이터 검증 및 표준 추출"""
        if not self.sites:
            raise ValueError("최소 1개 사업장이 필요합니다")
        
        # 모든 사업장의 표준을 수집
        all_standards = set()
        for site in self.sites:
            all_standards.update(site.standards)
        
        if not self.standards:
            self.standards = list(all_standards)
        
        # 사업장별 표준 검증
        for site in self.sites:
            if not site.standards:
                raise ValueError(f"사업장 '{site.name}'에 표준이 지정되지 않았습니다")


@dataclass
class ProgramBreakdown:
    """표준별 Stage1/Stage2/SV/Recert breakdown"""
    standard: StandardType
    stage1_days: float = 0.0
    stage2_days: float = 0.0
    surveillance_days: float = 0.0
    recert_days: float = 0.0
    total_days: float = 0.0
    complexity: ComplexityLevel = ComplexityLevel.SMALL
    enp: int = 0
    assumptions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """총 일수 계산"""
        self.total_days = (
            self.stage1_days + 
            self.stage2_days + 
            self.surveillance_days + 
            self.recert_days
        )


@dataclass
class QuoteResult:
    """최종 견적 결과"""
    organization: Organization
    breakdowns: List[ProgramBreakdown] = field(default_factory=list)
    total_audit_days: float = 0.0
    subtotal_cost: float = 0.0
    vat_amount: float = 0.0
    total_cost: float = 0.0
    assumptions: List[str] = field(default_factory=list)
    justification: List[str] = field(default_factory=list)
    created_at: str = ""
    
    def __post_init__(self):
        """총계 계산"""
        self.total_audit_days = sum(bd.total_days for bd in self.breakdowns)
        self.subtotal_cost = self.total_audit_days * self.organization.options.day_rate
        self.vat_amount = self.subtotal_cost * self.organization.options.vat_rate
        self.total_cost = self.subtotal_cost + self.vat_amount


@dataclass
class MandayTable:
    """MD 테이블 데이터"""
    enp_min: int
    enp_max: int
    complexity: ComplexityLevel
    stage2_days: float
    standard_type: Optional[StandardType] = None
    
    def __post_init__(self):
        """데이터 검증"""
        if self.enp_min > self.enp_max:
            raise ValueError("최소 ENP는 최대 ENP보다 작거나 같아야 합니다")
        if self.stage2_days <= 0:
            raise ValueError("Stage2 일수는 0보다 커야 합니다")


@dataclass
class CalculationContext:
    """계산 컨텍스트"""
    organization: Organization
    manday_tables: List[MandayTable] = field(default_factory=list)
    integration_discount: float = 0.0
    remote_discount: float = 0.0
    total_discount: float = 0.0
    
    def calculate_total_discount(self):
        """총 할인율 계산"""
        self.integration_discount = self.organization.integration.get_integration_discount()
        self.remote_discount = min(self.organization.options.remote_audit_ratio * 0.1, 0.1)
        self.total_discount = min(self.integration_discount + self.remote_discount, 0.15)  # 최대 15%
