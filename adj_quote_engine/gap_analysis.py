#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 갭분석 엔진 - Apple 보고서 스타일
기존 시스템과 호환되면서 고급 기능을 제공
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

def calculate_complexity(total_employees: int) -> str:
    """조직 복잡도 계산"""
    if total_employees < 50:
        return "Low"
    elif total_employees < 200:
        return "Medium"
    elif total_employees < 1000:
        return "High"
    else:
        return "Very High"

def analyze_standard(standard: str, total_employees: int, complexity: str) -> Dict[str, Any]:
    """개별 표준에 대한 갭분석 수행"""
    
    # 표준별 기본 정보
    standard_info = {
        'iso9001': {
            'name': 'ISO 9001:2015 (품질경영시스템)',
            'base_score': 30,
            'complexity_multiplier': {'Low': 0.8, 'Medium': 1.0, 'High': 1.2, 'Very High': 1.5}
        },
        'iso14001': {
            'name': 'ISO 14001:2016 (환경경영시스템)',
            'base_score': 25,
            'complexity_multiplier': {'Low': 0.7, 'Medium': 0.9, 'High': 1.1, 'Very High': 1.3}
        },
        'iso45001': {
            'name': 'ISO 45001:2018 (안전보건경영시스템)',
            'base_score': 20,
            'complexity_multiplier': {'Low': 0.6, 'Medium': 0.8, 'High': 1.0, 'Very High': 1.2}
        }
    }
    
    info = standard_info.get(standard, {
        'name': standard,
        'base_score': 25,
        'complexity_multiplier': {'Low': 0.8, 'Medium': 1.0, 'High': 1.2, 'Very High': 1.5}
    })
    
    # 현재 점수 계산 (조직 규모와 복잡도 고려)
    base_score = info['base_score']
    multiplier = info['complexity_multiplier'].get(complexity, 1.0)
    current_score = min(95, int(base_score * multiplier))
    
    # 갭 계산 (100점 만점 기준)
    gap = 100 - current_score
    
    # 준비도 평가
    if current_score >= 80:
        readiness = "준비완료"
    elif current_score >= 60:
        readiness = "부분준비"
    elif current_score >= 40:
        readiness = "기본준비"
    else:
        readiness = "준비필요"
    
    # 표준별 특화 갭 분석
    critical_gaps = generate_critical_gaps(standard, current_score, total_employees)
    recommendations = generate_standard_recommendations(standard, current_score, total_employees)
    
    return {
        'standard': standard,
        'name': info['name'],
        'currentScore': current_score,
        'gap': gap,
        'readiness': readiness,
        'criticalGaps': critical_gaps,
        'recommendations': recommendations,
        'complexity': complexity
    }

def generate_critical_gaps(standard: str, current_score: int, total_employees: int) -> List[str]:
    """표준별 주요 갭 영역 생성"""
    
    gaps_by_standard = {
        'iso9001': [
            "경영진 리더십 및 정책 수립",
            "품질목표 및 성과측정 체계",
            "프로세스 관리 및 문서화",
            "고객만족도 측정 및 개선",
            "내부심사 및 경영검토 체계"
        ],
        'iso14001': [
            "환경정책 및 목표 설정",
            "환경영향 평가 및 관리",
            "법적 요구사항 준수 체계",
            "환경교육 및 인식 제고",
            "비상상황 대응 계획"
        ],
        'iso45001': [
            "안전보건정책 및 목표",
            "위험성 평가 및 관리",
            "안전보건 교육 및 훈련",
            "사고조사 및 재발방지",
            "근로자 참여 및 협의"
        ]
    }
    
    base_gaps = gaps_by_standard.get(standard, [
        "경영시스템 정책 수립",
        "목표 설정 및 성과측정",
        "프로세스 문서화",
        "교육 및 인식 제고",
        "지속적 개선 체계"
    ])
    
    # 점수에 따라 갭 우선순위 조정
    if current_score >= 70:
        return base_gaps[:2]  # 상위 2개만
    elif current_score >= 50:
        return base_gaps[:3]  # 상위 3개
    else:
        return base_gaps[:4]  # 상위 4개

def generate_standard_recommendations(standard: str, current_score: int, total_employees: int) -> List[str]:
    """표준별 권장사항 생성"""
    
    recommendations_by_standard = {
        'iso9001': [
            "경영진이 품질경영시스템의 중요성을 인식하고 리더십을 발휘할 수 있도록 교육 실시",
            "고객 요구사항을 체계적으로 파악하고 만족도를 측정할 수 있는 프로세스 구축",
            "품질목표를 설정하고 정기적으로 검토하여 지속적 개선을 추진",
            "내부심사원을 양성하여 자체 품질시스템을 점검할 수 있는 역량 강화"
        ],
        'iso14001': [
            "환경정책을 수립하고 모든 직원이 이해할 수 있도록 교육 및 홍보 강화",
            "환경영향을 평가하고 중요 환경영향에 대한 관리방안을 수립",
            "환경 관련 법적 요구사항을 파악하고 준수할 수 있는 체계 구축",
            "환경사고 발생 시 신속하게 대응할 수 있는 비상계획 수립 및 훈련 실시"
        ],
        'iso45001': [
            "안전보건정책을 수립하고 모든 근로자가 안전을 최우선으로 생각하도록 인식 제고",
            "작업장의 위험성을 평가하고 위험요인을 제거하거나 최소화할 수 있는 방안 수립",
            "근로자에게 안전보건 교육을 정기적으로 실시하고 훈련 효과를 측정",
            "사고 발생 시 원인을 분석하고 재발방지 대책을 수립하여 안전문화 정착"
        ]
    }
    
    base_recommendations = recommendations_by_standard.get(standard, [
        "경영진이 해당 경영시스템의 중요성을 인식하고 리더십을 발휘할 수 있도록 교육 실시",
        "시스템 요구사항을 체계적으로 파악하고 성과를 측정할 수 있는 프로세스 구축",
        "목표를 설정하고 정기적으로 검토하여 지속적 개선을 추진",
        "내부심사원을 양성하여 자체 시스템을 점검할 수 있는 역량 강화"
    ])
    
    # 점수에 따라 권장사항 조정
    if current_score >= 70:
        return base_recommendations[:2]  # 상위 2개만
    elif current_score >= 50:
        return base_recommendations[:3]  # 상위 3개
    else:
        return base_recommendations  # 전체

def calculate_overall_readiness(standards_analysis: List[Dict[str, Any]]) -> str:
    """전체 준비도 계산"""
    if not standards_analysis:
        return "분석불가"
    
    avg_score = sum(std['currentScore'] for std in standards_analysis) / len(standards_analysis)
    
    if avg_score >= 80:
        return "준비완료"
    elif avg_score >= 60:
        return "부분준비"
    elif avg_score >= 40:
        return "기본준비"
    else:
        return "준비필요"

def calculate_estimated_cost(selected_standards: List[str], total_employees: int) -> Dict[str, Any]:
    """예상 비용 계산"""
    
    # 표준별 기본 비용 (단위: 만원)
    base_costs = {
        'iso9001': 500,
        'iso14001': 400,
        'iso45001': 450
    }
    
    # 직원 수에 따른 복잡도 계수
    if total_employees < 50:
        complexity_factor = 0.8
    elif total_employees < 200:
        complexity_factor = 1.0
    elif total_employees < 1000:
        complexity_factor = 1.3
    else:
        complexity_factor = 1.6
    
    # 표준 수에 따른 할인 계수
    if len(selected_standards) == 1:
        discount_factor = 1.0
    elif len(selected_standards) == 2:
        discount_factor = 0.9
    else:
        discount_factor = 0.8
    
    total_base_cost = sum(base_costs.get(std, 400) for std in selected_standards)
    estimated_cost = int(total_base_cost * complexity_factor * discount_factor)
    
    return {
        'total': estimated_cost,
        'breakdown': {
            'consulting': int(estimated_cost * 0.6),
            'certification': int(estimated_cost * 0.3),
            'training': int(estimated_cost * 0.1)
        }
    }

def calculate_timeline(selected_standards: List[str], complexity: str) -> Dict[str, Any]:
    """예상 일정 계산 (월 단위)"""
    
    # 복잡도별 기본 기간
    base_timeline = {
        'Low': 6,
        'Medium': 9,
        'High': 12,
        'Very High': 18
    }
    
    # 표준 수에 따른 추가 기간
    standard_adjustment = (len(selected_standards) - 1) * 2
    
    total_months = base_timeline.get(complexity, 9) + standard_adjustment
    
    return {
        'totalMonths': total_months,
        'phases': {
            'preparation': 2,
            'implementation': total_months - 4,
            'certification': 2
        }
    }

def generate_recommendations(standards_analysis: List[Dict[str, Any]]) -> List[str]:
    """전체 권장사항 생성"""
    
    recommendations = [
        "경영진의 강력한 리더십과 지속적인 지원이 성공적인 ISO 인증을 위한 핵심 요소입니다.",
        "모든 직원이 경영시스템의 중요성을 이해하고 참여할 수 있도록 교육과 소통을 강화하세요.",
        "현재 운영 중인 우수한 관행들을 ISO 요구사항에 맞게 체계적으로 문서화하세요.",
        "정기적인 내부심사와 경영검토를 통해 시스템의 효과성을 지속적으로 개선하세요.",
        "고객과 이해관계자의 요구사항을 파악하고 만족도를 측정할 수 있는 체계를 구축하세요."
    ]
    
    return recommendations

def generate_gap_analysis_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """메인 갭분석 보고서 생성 함수"""
    
    selected_standards = data.get('selectedISOStandards', [])
    total_employees = int(data.get('totalEmployees', 0))
    company_name = data.get('companyName', 'Unknown Company')
    
    # 복잡도 계산
    complexity = calculate_complexity(total_employees)
    
    # 표준별 분석
    standards_analysis = []
    for standard in selected_standards:
        analysis = analyze_standard(standard, total_employees, complexity)
        standards_analysis.append(analysis)
    
    # 전체 준비도 계산
    overall_readiness = calculate_overall_readiness(standards_analysis)
    
    # 비용 및 일정 추정
    estimated_cost = calculate_estimated_cost(selected_standards, total_employees)
    estimated_timeline = calculate_timeline(selected_standards, complexity)
    
    # 보고서 생성
    report = {
        "companyName": company_name,
        "analysisDate": datetime.now().isoformat(),
        "overallReadiness": overall_readiness,
        "standards": standards_analysis,
        "summary": {
            "totalGaps": sum(std['gap'] for std in standards_analysis),
            "averageScore": round(sum(std['currentScore'] for std in standards_analysis) / len(standards_analysis)) if standards_analysis else 0,
            "estimatedCost": estimated_cost,
            "estimatedTimeline": estimated_timeline,
            "complexity": complexity,
            "totalEmployees": total_employees
        },
        "recommendations": generate_recommendations(standards_analysis),
        "nextSteps": [
            "경영진 승인 및 프로젝트 팀 구성",
            "현재 상태 상세 분석 및 갭 분석 실시",
            "개선 계획 수립 및 일정 조정",
            "직원 교육 및 인식 제고 프로그램 실시",
            "시스템 구축 및 문서화 작업",
            "내부심사 실시 및 개선사항 적용",
            "인증기관 선정 및 인증심사 신청"
        ],
        "contactInfo": {
            "phone": "02-1234-5678",
            "email": "info@lrqa.com",
            "website": "www.lrqa.com"
        }
    }
    
    return report

def main():
    """메인 실행 함수 (기존 시스템과 호환)"""
    if len(sys.argv) != 2:
        print("Usage: python gap_analysis.py <data_file.json>")
        sys.exit(1)
    
    try:
        # JSON 파일 읽기
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 갭분석 보고서 생성
        report = generate_gap_analysis_report(data)
        
        # 결과 출력
        print(json.dumps(report, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
