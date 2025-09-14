"""
근거 및 가정 문안 자동 생성

이 모듈은 견적 계산의 근거와 가정을 자동으로 생성합니다.
ENP 산정 근거, 원격심사 적용 여부, 통합심사 감축 상한, 라운딩 규칙 등을 포함합니다.
"""

from typing import List, Dict, Any
from .models import Organization, ProgramBreakdown, QuoteResult, StandardType, ComplexityLevel


class JustificationGenerator:
    """근거 및 가정 문안 생성기"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, str]:
        """문안 템플릿 초기화"""
        return {
            'enp_calculation': """
ENP(유효인원수) 산정 근거:
- 정규직 직원수: {regular_count}명
- 외주 인력: {contractor_count}명  
- 파트타임 직원: {part_time_count}명 (50% 감축 적용)
- 교대근무자: {shift_workers}명 (50% 가산 적용)
- 반복공정 여부: {repetitive_process} ({repetitive_discount}% 감축)
- 계절성 가중치: {seasonal_factor}
- 최종 ENP: {final_enp}명
            """,
            
            'md_table_application': """
MD 테이블 적용 근거:
- 적용 표준: {standard}
- ENP: {enp}명
- 복잡도 레벨: {complexity}
- Stage2 기준일수: {stage2_days}일
- MD5/MD1/MD11 기준 적용
            """,
            
            'stage_calculation': """
Stage별 일수 계산:
- Stage1: Stage2 × 30% = {stage1_days}일
- Stage2: {stage2_days}일 (기준)
- Surveillance: Stage2 × 60% = {surveillance_days}일  
- Recert: Stage2 × 100% = {recert_days}일
- 총 심사일수: {total_days}일
            """,
            
            'integration_discount': """
통합심사 감축 적용:
- 통합심사 여부: {is_integrated}
- 공통 경영시스템: {shared_management}
- 공통 프로세스: {common_processes}
- 동일 심사팀: {same_audit_team}
- 적용 감축율: {discount_rate}%
            """,
            
            'remote_audit': """
원격심사 적용:
- 원격심사 비율: {remote_ratio}%
- 적용 감축율: {discount_rate}% (최대 10%)
- 보수적 접근법 적용
            """,
            
            'rounding_rules': """
라운딩 규칙:
- 0.5일 단위 라운딩 적용
- 최소 0.5일, 최대 12.5일
- 소수점 둘째 자리에서 반올림
            """,
            
            'assumptions': """
가정사항:
- 모든 사업장이 동일한 표준 적용
- 심사팀 구성 및 이동시간 고려
- 고객사 협조 및 준비 완료 가정
- 표준 요구사항 변경 없음 가정
- 계약 기간 내 완료 가정
            """
        }
    
    def generate_enp_justification(self, organization: Organization) -> str:
        """ENP 산정 근거 생성"""
        total_regular = sum(site.total_headcount for site in organization.sites)
        total_contractor = sum(site.contractor_count for site in organization.sites)
        total_part_time = sum(site.part_time_count for site in organization.sites)
        total_shift = sum(site.shift_workers for site in organization.sites)
        
        repetitive_sites = [site for site in organization.sites if site.repetitive_process]
        repetitive_discount = 10 if repetitive_sites else 0
        
        avg_seasonal = sum(site.seasonal_factor for site in organization.sites) / len(organization.sites)
        
        # 전체 ENP 계산 (단순화)
        total_enp = sum(
            site.total_headcount + site.contractor_count - (site.part_time_count * 0.5) + (site.shift_workers * 0.5)
            for site in organization.sites
        )
        
        if repetitive_sites:
            total_enp *= 0.9
        
        total_enp *= avg_seasonal
        
        return self.templates['enp_calculation'].format(
            regular_count=total_regular,
            contractor_count=total_contractor,
            part_time_count=total_part_time,
            shift_workers=total_shift,
            repetitive_process="예" if repetitive_sites else "아니오",
            repetitive_discount=repetitive_discount,
            seasonal_factor=f"{avg_seasonal:.1f}",
            final_enp=int(total_enp)
        )
    
    def generate_md_table_justification(self, breakdown: ProgramBreakdown) -> str:
        """MD 테이블 적용 근거 생성"""
        return self.templates['md_table_application'].format(
            standard=breakdown.standard.value,
            enp=breakdown.enp,
            complexity=breakdown.complexity.value,
            stage2_days=breakdown.stage2_days
        )
    
    def generate_stage_justification(self, breakdown: ProgramBreakdown) -> str:
        """Stage별 일수 계산 근거 생성"""
        return self.templates['stage_calculation'].format(
            stage1_days=breakdown.stage1_days,
            stage2_days=breakdown.stage2_days,
            surveillance_days=breakdown.surveillance_days,
            recert_days=breakdown.recert_days,
            total_days=breakdown.total_days
        )
    
    def generate_integration_justification(self, organization: Organization) -> str:
        """통합심사 감축 근거 생성"""
        integration = organization.integration
        discount_rate = integration.get_integration_discount() * 100
        
        return self.templates['integration_discount'].format(
            is_integrated="예" if integration.is_integrated else "아니오",
            shared_management="예" if integration.shared_management_system else "아니오",
            common_processes="예" if integration.common_processes else "아니오",
            same_audit_team="예" if integration.same_audit_team else "아니오",
            discount_rate=f"{discount_rate:.1f}"
        )
    
    def generate_remote_audit_justification(self, organization: Organization) -> str:
        """원격심사 적용 근거 생성"""
        remote_ratio = organization.options.remote_audit_ratio * 100
        discount_rate = min(remote_ratio * 0.1, 10)
        
        return self.templates['remote_audit'].format(
            remote_ratio=f"{remote_ratio:.1f}",
            discount_rate=f"{discount_rate:.1f}"
        )
    
    def generate_rounding_justification(self) -> str:
        """라운딩 규칙 근거 생성"""
        return self.templates['rounding_rules']
    
    def generate_assumptions(self, organization: Organization) -> str:
        """가정사항 생성"""
        return self.templates['assumptions']
    
    def generate_comprehensive_justification(self, result: QuoteResult) -> List[str]:
        """종합적인 근거 문안 생성"""
        justification = []
        
        # 1. ENP 산정 근거
        justification.append(self.generate_enp_justification(result.organization))
        
        # 2. 표준별 MD 테이블 적용 근거
        for breakdown in result.breakdowns:
            justification.append(self.generate_md_table_justification(breakdown))
            justification.append(self.generate_stage_justification(breakdown))
        
        # 3. 통합심사 감축 근거
        if result.organization.integration.is_integrated:
            justification.append(self.generate_integration_justification(result.organization))
        
        # 4. 원격심사 적용 근거
        if result.organization.options.remote_audit_ratio > 0:
            justification.append(self.generate_remote_audit_justification(result.organization))
        
        # 5. 라운딩 규칙
        justification.append(self.generate_rounding_justification())
        
        # 6. 가정사항
        justification.append(self.generate_assumptions(result.organization))
        
        return justification
    
    def generate_summary_justification(self, result: QuoteResult) -> str:
        """요약 근거 생성"""
        summary = f"""
견적 계산 요약:

1. 고객사: {result.organization.client_name}
2. 적용 표준: {', '.join([std.value for std in result.organization.standards])}
3. 사업장 수: {len(result.organization.sites)}개
4. 총 심사일수: {result.total_audit_days} mandays
5. 총 견적 금액: ₩{result.total_cost:,.0f}

계산 근거:
- ADJ v2.2 규칙 적용
- IAF MD 표준 기반
- ENP 산정: {sum(bd.enp for bd in result.breakdowns)}명
- 통합심사: {'적용' if result.organization.integration.is_integrated else '미적용'}
- 원격심사: {result.organization.options.remote_audit_ratio*100:.1f}%
        """
        
        return summary.strip()
    
    def generate_technical_notes(self, result: QuoteResult) -> List[str]:
        """기술적 주의사항 생성"""
        notes = []
        
        # ENP 관련 주의사항
        if any(site.repetitive_process for site in result.organization.sites):
            notes.append("반복공정 사업장에 대해 10% ENP 감축이 적용되었습니다.")
        
        if any(site.seasonal_factor > 1.0 for site in result.organization.sites):
            notes.append("계절성 사업장에 대해 가중치가 적용되었습니다.")
        
        # 통합심사 주의사항
        if result.organization.integration.is_integrated:
            notes.append("통합심사 감축은 최대 10%를 초과할 수 없습니다.")
        
        # 원격심사 주의사항
        if result.organization.options.remote_audit_ratio > 0:
            notes.append("원격심사 비율에 따른 보수적 감축이 적용되었습니다.")
        
        # 복잡도 주의사항
        complexities = set(bd.complexity for bd in result.breakdowns)
        if ComplexityLevel.LARGE in complexities:
            notes.append("대형 복잡도 사업장에 대해 추가 검토가 필요할 수 있습니다.")
        
        return notes


# 전역 인스턴스
justification_generator = JustificationGenerator()
