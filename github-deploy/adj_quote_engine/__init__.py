"""
ADJ v2.2 기반 ISO 인증심사 견적 계산 엔진

이 패키지는 ADJ v2.2 규칙에 따라 ISO 인증심사 견적을 자동으로 계산하고
Word 문서로 출력하는 기능을 제공합니다.

주요 기능:
- ENP(유효인원수) 기반 심사일수 산정
- MD5/MD1/MD11 기준 테이블 적용
- 통합심사 및 원격심사 감축 적용
- Stage1/Stage2/Surveillance/Recert 일수 계산
- Word 문서 견적서 자동 생성

사용 예시:
    from adj_quote_engine import QuoteEngine
    
    engine = QuoteEngine()
    result = engine.calculate_quote(input_data)
    engine.export_docx(result, "quotation.docx")
"""

__version__ = "1.0.0"
__author__ = "LRQA Korea"

from .models import (
    Site,
    IntegrationInputs, 
    Options,
    Organization,
    ProgramBreakdown,
    QuoteResult
)

from .adj_rules_v22 import QuoteEngine
from .pricing import PricingCalculator
from .quote_docx import export_to_word

__all__ = [
    "Site",
    "IntegrationInputs",
    "Options", 
    "Organization",
    "ProgramBreakdown",
    "QuoteResult",
    "QuoteEngine",
    "PricingCalculator",
    "export_to_word"
]
