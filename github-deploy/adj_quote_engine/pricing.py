"""
비용 산출 로직

이 모듈은 심사일수와 단가를 기반으로 견적 비용을 계산합니다.
맨데이 × 단가 + VAT 공식으로 계산하며, 서브토탈, VAT, 총액을 분리 출력합니다.
"""

from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP
from .models import QuoteResult, Organization, Options


class PricingCalculator:
    """비용 계산기"""
    
    def __init__(self, day_rate: float = 1300000.0, vat_rate: float = 0.1):
        """
        Args:
            day_rate: 1 manday 단가 (기본 1,300,000 KRW)
            vat_rate: VAT 비율 (기본 0.1 = 10%)
        """
        self.day_rate = day_rate
        self.vat_rate = vat_rate
    
    def calc_cost(self, days: float, day_rate: Optional[float] = None, 
                  vat_rate: Optional[float] = None) -> Dict[str, float]:
        """
        비용 계산
        
        Args:
            days: 심사일수
            day_rate: 1 manday 단가 (None이면 기본값 사용)
            vat_rate: VAT 비율 (None이면 기본값 사용)
            
        Returns:
            Dict containing subtotal, vat_amount, total_cost
        """
        if day_rate is None:
            day_rate = self.day_rate
        if vat_rate is None:
            vat_rate = self.vat_rate
        
        # 서브토탈 계산 (맨데이 × 단가)
        subtotal = days * day_rate
        
        # VAT 계산
        vat_amount = subtotal * vat_rate
        
        # 총액 계산
        total_cost = subtotal + vat_amount
        
        return {
            'subtotal': float(subtotal),
            'vat_amount': float(vat_amount),
            'total_cost': float(total_cost),
            'days': days,
            'day_rate': day_rate,
            'vat_rate': vat_rate
        }
    
    def calculate_quote_pricing(self, result: QuoteResult) -> QuoteResult:
        """견적 결과에 비용 정보 추가"""
        options = result.organization.options
        
        # 총 비용 계산
        pricing = self.calc_cost(
            days=result.total_audit_days,
            day_rate=options.day_rate,
            vat_rate=options.vat_rate
        )
        
        # 결과에 비용 정보 업데이트
        result.subtotal_cost = pricing['subtotal']
        result.vat_amount = pricing['vat_amount']
        result.total_cost = pricing['total_cost']
        
        return result
    
    def calculate_breakdown_pricing(self, breakdowns: list, 
                                  day_rate: float, vat_rate: float) -> list:
        """표준별 breakdown 비용 계산"""
        priced_breakdowns = []
        
        for breakdown in breakdowns:
            # 각 breakdown의 총 일수
            total_days = breakdown.total_days
            
            # 비용 계산
            pricing = self.calc_cost(total_days, day_rate, vat_rate)
            
            # breakdown에 비용 정보 추가
            breakdown_dict = {
                'standard': breakdown.standard.value,
                'stage1_days': breakdown.stage1_days,
                'stage2_days': breakdown.stage2_days,
                'surveillance_days': breakdown.surveillance_days,
                'recert_days': breakdown.recert_days,
                'total_days': breakdown.total_days,
                'subtotal_cost': pricing['subtotal'],
                'vat_amount': pricing['vat_amount'],
                'total_cost': pricing['total_cost'],
                'complexity': breakdown.complexity.value,
                'enp': breakdown.enp
            }
            
            priced_breakdowns.append(breakdown_dict)
        
        return priced_breakdowns
    
    def format_currency(self, amount: float, currency: str = "KRW") -> str:
        """통화 형식으로 포맷팅"""
        if currency == "KRW":
            return f"₩{amount:,.0f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    
    def generate_pricing_summary(self, result: QuoteResult) -> Dict[str, str]:
        """가격 요약 정보 생성"""
        return {
            'total_days': f"{result.total_audit_days} mandays",
            'day_rate': self.format_currency(result.organization.options.day_rate),
            'subtotal': self.format_currency(result.subtotal_cost),
            'vat_rate': f"{result.organization.options.vat_rate * 100:.1f}%",
            'vat_amount': self.format_currency(result.vat_amount),
            'total_cost': self.format_currency(result.total_cost)
        }
    
    def apply_discount(self, base_cost: float, discount_rate: float) -> Dict[str, float]:
        """할인 적용"""
        if discount_rate < 0 or discount_rate > 1:
            raise ValueError("할인율은 0~1 사이여야 합니다")
        
        discount_amount = base_cost * discount_rate
        discounted_cost = base_cost - discount_amount
        
        return {
            'original_cost': base_cost,
            'discount_rate': discount_rate,
            'discount_amount': discount_amount,
            'final_cost': discounted_cost
        }
    
    def calculate_volume_discount(self, total_days: float) -> float:
        """볼륨 할인 계산"""
        if total_days >= 50:
            return 0.15  # 15% 할인
        elif total_days >= 30:
            return 0.10  # 10% 할인
        elif total_days >= 20:
            return 0.05  # 5% 할인
        else:
            return 0.0   # 할인 없음
    
    def calculate_loyalty_discount(self, is_existing_client: bool, 
                                 years_as_client: int = 0) -> float:
        """로열티 할인 계산"""
        if not is_existing_client:
            return 0.0
        
        if years_as_client >= 5:
            return 0.10  # 10% 할인
        elif years_as_client >= 3:
            return 0.05  # 5% 할인
        elif years_as_client >= 1:
            return 0.02  # 2% 할인
        else:
            return 0.0   # 할인 없음


# 전역 인스턴스
pricing_calculator = PricingCalculator()
