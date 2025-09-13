"""
ADJ v2.2 핵심 규칙 구현

이 모듈은 ADJ v2.2의 핵심 계산 규칙을 구현합니다:
- ENP(유효인원수) 계산
- 표준별 Stage1/2/SV/Recert 계산
- 통합심사 및 원격심사 감축 적용
- 라운딩 규칙 적용
"""

from typing import List, Dict, Optional
from datetime import datetime
from .models import (
    Site, Organization, ProgramBreakdown, QuoteResult, 
    CalculationContext, StandardType, ComplexityLevel
)
from .md_tables import manday_manager


class QuoteEngine:
    """ADJ v2.2 견적 계산 엔진"""
    
    def __init__(self):
        self.md_manager = manday_manager
    
    def calculate_quote(self, organization: Organization) -> QuoteResult:
        """견적 계산 메인 함수"""
        context = CalculationContext(organization=organization)
        context.calculate_total_discount()
        
        # 표준별 breakdown 계산
        breakdowns = self.build_breakdowns(organization, context)
        
        # 총계 계산 (소수점 둘째자리까지 계산 후 0.5일 단위로 라운딩)
        total_days = sum(bd.total_days for bd in breakdowns)
        total_days = round(total_days, 2)  # 소수점 둘째자리까지
        total_days = self.md_manager.round_to_half_day(total_days)  # 0.5일 단위로 라운딩
        
        # 견적 결과 생성
        result = QuoteResult(
            organization=organization,
            breakdowns=breakdowns,
            total_audit_days=total_days,
            created_at=datetime.now().isoformat()
        )
        
        # 가정 및 근거 생성
        result.assumptions = self.generate_assumptions(organization, breakdowns)
        result.justification = self.generate_justification(organization, breakdowns)
        
        return result
    
    def calc_enp_for_site(self, site: Site) -> int:
        """사업장별 ENP(유효인원수) 계산"""
        # 정규직 + 외주 인력 포함
        base_count = site.total_headcount + site.contractor_count
        
        # 파트타임 50% 감축
        adjusted_count = base_count - (site.part_time_count * 0.5)
        
        # 반복공정 10% 감축
        if site.repetitive_process:
            adjusted_count *= 0.9
        
        # 계절성 가중치 적용 (>=1.0)
        adjusted_count *= site.seasonal_factor
        
        # 교대근무자 50% 가산
        adjusted_count += site.shift_workers * 0.5
        
        return max(1, int(round(adjusted_count)))
    
    def program_breakdown_for_standard(self, organization: Organization, 
                                     standard: StandardType) -> ProgramBreakdown:
        """표준별 Stage1/2/SV/Recert 계산"""
        # 해당 표준을 적용하는 사업장들 찾기
        relevant_sites = [site for site in organization.sites 
                         if standard in site.standards]
        
        if not relevant_sites:
            return ProgramBreakdown(standard=standard)
        
        # 전체 ENP 계산 (모든 관련 사업장 합계)
        total_enp = sum(self.calc_enp_for_site(site) for site in relevant_sites)
        
        # 표준별 복잡도 요인 평가
        environmental_impact = self._evaluate_environmental_impact(relevant_sites, standard)
        safety_risk = self._evaluate_safety_risk(relevant_sites, standard)
        
        # 복잡도 레벨 결정
        complexity = self.md_manager.get_complexity_level(
            total_enp, standard, environmental_impact, safety_risk
        )
        
        # IAF MD5: Stage1+Stage2 총합 일수 조회 (표준별)
        total_stage_days = self.md_manager.get_stage2_days(total_enp, complexity, standard)
        
        # 원격심사 감축 적용 (통합심사는 별도 로직에서 처리)
        if organization.options.remote_audit_ratio > 0:
            remote_discount = min(organization.options.remote_audit_ratio * 0.1, 0.1)
            total_stage_days *= (1 - remote_discount)
        
        # 소수점 둘째자리까지 계산 후 0.5일 단위 라운딩 (사사오입)
        total_stage_days = round(total_stage_days, 2)  # 소수점 둘째자리까지
        total_stage_days = self.md_manager.round_to_half_day(total_stage_days)  # 0.5일 단위로 라운딩
        
        # IAF MD5: Stage1+Stage2 총합에서 각 Stage별 일수 계산
        stage_days = self.md_manager.calculate_stage_days(
            total_stage_days,
            stage1=organization.options.stage1,
            surveillance=organization.options.surveillance,
            recert=organization.options.recert
        )
        
        # 가정 문구 생성
        assumptions = self._generate_standard_assumptions(
            standard, total_enp, complexity, relevant_sites, organization
        )
        
        return ProgramBreakdown(
            standard=standard,
            stage1_days=stage_days['stage1'],
            stage2_days=stage_days['stage2'],
            surveillance_days=stage_days['surveillance'],
            recert_days=stage_days['recert'],
            complexity=complexity,
            enp=total_enp,
            assumptions=assumptions
        )
    
    def build_breakdowns(self, organization: Organization, 
                        context: CalculationContext) -> List[ProgramBreakdown]:
        """모든 표준별 breakdown 계산"""
        breakdowns = []
        
        for standard in organization.standards:
            breakdown = self.program_breakdown_for_standard(organization, standard)
            breakdowns.append(breakdown)
        
        # 통합심사 시 전체 심사일수 감소 적용 (IAF MD5 표준)
        if organization.integration.is_integrated and len(breakdowns) > 1:
            breakdowns = self._apply_integrated_audit_reduction(breakdowns, organization)
        
        return breakdowns
    
    def _apply_integrated_audit_reduction(self, breakdowns: List[ProgramBreakdown], 
                                        organization: Organization) -> List[ProgramBreakdown]:
        """통합심사 시 전체 심사일수 감소 적용 (IAF MD5 표준)"""
        if len(breakdowns) < 2:
            return breakdowns
        
        # IAF MD5 표준: 통합심사 시 중복 심사 시간 제거
        # 2개 표준: 15% 감소, 3개 표준: 25% 감소
        num_standards = len(breakdowns)
        if num_standards == 2:
            reduction_factor = 0.15  # 15% 감소
        elif num_standards == 3:
            reduction_factor = 0.25  # 25% 감소
        else:
            reduction_factor = 0.30  # 4개 이상: 30% 감소
        
        # 각 breakdown에 감소 적용
        for breakdown in breakdowns:
            # Stage1+Stage2 총합에서 감소 적용
            total_stage = breakdown.stage1_days + breakdown.stage2_days
            reduced_total = total_stage * (1 - reduction_factor)
            
            # 감소된 총합을 0.5일 단위로 라운딩
            reduced_total = self.md_manager.round_to_half_day(reduced_total)
            
            # Stage1과 Stage2 비율 유지하면서 재계산
            if total_stage > 0:
                stage1_ratio = breakdown.stage1_days / total_stage
                stage2_ratio = breakdown.stage2_days / total_stage
                
                breakdown.stage1_days = self.md_manager.round_to_half_day(reduced_total * stage1_ratio)
                breakdown.stage2_days = self.md_manager.round_to_half_day(reduced_total * stage2_ratio)
            
            # Surveillance와 Recert도 동일한 비율로 감소
            breakdown.surveillance_days = self.md_manager.round_to_half_day(
                breakdown.surveillance_days * (1 - reduction_factor)
            )
            breakdown.recert_days = self.md_manager.round_to_half_day(
                breakdown.recert_days * (1 - reduction_factor)
            )
        
        return breakdowns
    
    def summarize_days(self, breakdowns: List[ProgramBreakdown]) -> Dict[str, float]:
        """총 심사일수 요약"""
        summary = {
            'stage1': sum(bd.stage1_days for bd in breakdowns),
            'stage2': sum(bd.stage2_days for bd in breakdowns),
            'surveillance': sum(bd.surveillance_days for bd in breakdowns),
            'recert': sum(bd.recert_days for bd in breakdowns),
            'total': sum(bd.total_days for bd in breakdowns)
        }
        
        return summary
    
    def generate_assumptions(self, organization: Organization, 
                           breakdowns: List[ProgramBreakdown]) -> List[str]:
        """가정 문구 생성"""
        assumptions = []
        
        # 기본 가정
        assumptions.append(f"고객사: {organization.client_name}")
        assumptions.append(f"적용 표준: {', '.join([std.value for std in organization.standards])}")
        assumptions.append(f"사업장 수: {len(organization.sites)}개")
        
        # ENP 관련 가정
        total_enp = sum(bd.enp for bd in breakdowns)
        assumptions.append(f"총 유효인원수(ENP): {total_enp}명")
        
        # 통합심사 가정
        if organization.integration.is_integrated:
            discount = organization.integration.get_integration_discount()
            assumptions.append(f"통합심사 적용: {discount*100:.1f}% 감축")
        
        # 원격심사 가정
        if organization.options.remote_audit_ratio > 0:
            assumptions.append(f"원격심사 비율: {organization.options.remote_audit_ratio*100:.1f}%")
        
        # 복잡도 가정
        complexities = set(bd.complexity for bd in breakdowns)
        if len(complexities) == 1:
            complexity_name = list(complexities)[0].value
            assumptions.append(f"복잡도 레벨: {complexity_name}")
        else:
            assumptions.append(f"복잡도 레벨: 혼합 ({', '.join([c.value for c in complexities])})")
        
        return assumptions
    
    def generate_justification(self, organization: Organization, 
                             breakdowns: List[ProgramBreakdown]) -> List[str]:
        """근거 문구 생성"""
        justification = []
        
        # ENP 산정 근거
        justification.append("ENP 산정 근거:")
        for site in organization.sites:
            enp = self.calc_enp_for_site(site)
            justification.append(f"- {site.name}: {enp}명 (정규직 {site.total_headcount}명, 외주 {site.contractor_count}명, 파트타임 {site.part_time_count}명)")
        
        # IAF MD5 테이블 적용 근거
        justification.append("IAF MD5 테이블 적용:")
        for bd in breakdowns:
            total_stage = bd.stage1_days + bd.stage2_days
            justification.append(f"- {bd.standard.value}: ENP {bd.enp}명, {bd.complexity.value} 복잡도, Stage1+Stage2 {total_stage}일")
        
        # 할인 적용 근거
        if organization.integration.get_integration_discount() > 0:
            justification.append(f"통합심사 할인: {organization.integration.get_integration_discount()*100:.1f}%")
        
        if organization.options.remote_audit_ratio > 0:
            justification.append(f"원격심사 할인: {organization.options.remote_audit_ratio*100:.1f}%")
        
        return justification
    
    def _generate_standard_assumptions(self, standard: StandardType, 
                                     enp: int, complexity: ComplexityLevel,
                                     sites: List[Site], 
                                     organization: Organization) -> List[str]:
        """표준별 가정 문구 생성"""
        assumptions = []
        
        assumptions.append(f"{standard.value} 적용 사업장: {len(sites)}개")
        assumptions.append(f"ENP: {enp}명")
        assumptions.append(f"복잡도: {complexity.value}")
        
        # 사업장별 상세 정보
        for site in sites:
            site_enp = self.calc_enp_for_site(site)
            assumptions.append(f"- {site.name}: ENP {site_enp}명")
        
        return assumptions
    
    def _evaluate_environmental_impact(self, sites: List[Site], standard: StandardType) -> str:
        """ISO 14001 환경 영향도 평가"""
        if standard != StandardType.ISO14001:
            return "MEDIUM"  # 기본값
        
        # 환경 영향도 평가 로직 (예시)
        # 실제로는 사업장의 업종, 규모, 환경 영향 등을 종합적으로 평가
        total_enp = sum(self.calc_enp_for_site(site) for site in sites)
        
        # 간단한 평가 로직 (실제로는 더 복잡한 평가 필요)
        if total_enp >= 1000:
            return "HIGH"      # 대규모 사업장
        elif total_enp >= 200:
            return "MEDIUM"    # 중규모 사업장
        elif total_enp >= 50:
            return "LOW"       # 소규모 사업장
        else:
            return "LIMITED"   # 초소규모 사업장
    
    def _evaluate_safety_risk(self, sites: List[Site], standard: StandardType) -> str:
        """ISO 45001 안전보건 위험도 평가"""
        if standard != StandardType.ISO45001:
            return "MEDIUM"  # 기본값
        
        # 안전보건 위험도 평가 로직 (예시)
        # 실제로는 사업장의 업종, 위험요소, 과거 사고 이력 등을 종합적으로 평가
        total_enp = sum(self.calc_enp_for_site(site) for site in sites)
        
        # 간단한 평가 로직 (실제로는 더 복잡한 평가 필요)
        if total_enp >= 1000:
            return "HIGH"      # 대규모 사업장 (높은 위험)
        elif total_enp >= 200:
            return "MEDIUM"    # 중규모 사업장 (중간 위험)
        else:
            return "LOW"       # 소규모 사업장 (낮은 위험)


# 전역 인스턴스
quote_engine = QuoteEngine()
