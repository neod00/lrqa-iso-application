"""
견적서 Word 문서 출력 (템플릿 기반)

이 모듈은 LRQA 견적서 템플릿을 사용하여 견적 결과를 Word 문서(.docx)로 출력합니다.
Jinja2 템플릿을 사용하여 LRQA_quotation.docx와 동일한 디자인으로 생성됩니다.
"""

from typing import Optional
from .quote_template import generate_lrqa_quotation_docx
from .models import QuoteResult


def export_to_word(result: QuoteResult, output_path: str) -> str:
    """
    견적 결과를 Word 문서로 내보내기
    
    Args:
        result: 견적 결과 객체
        output_path: 출력 파일 경로
        
    Returns:
        str: 생성된 파일 경로
        
    Raises:
        Exception: Word 문서 생성 실패 시
    """
    try:
        return generate_lrqa_quotation_docx(result, output_path)
    except Exception as e:
        raise Exception(f"Word 문서 생성 실패: {str(e)}")


# 하위 호환성을 위한 별칭
def generate_quotation_docx(result: QuoteResult, output_path: str) -> str:
    """견적서 Word 문서 생성 (하위 호환성)"""
    return export_to_word(result, output_path)