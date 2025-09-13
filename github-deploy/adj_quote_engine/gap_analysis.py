#!/usr/bin/env python3
"""
LRQA ISO 갭분석 보고서 생성기
"""

import json
import sys
import os
from datetime import datetime
import random

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python gap_analysis.py <data_file>"}))
        sys.exit(1)
    
    data_file = sys.argv[1]
    
    try:
        # 데이터 파일 읽기
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 갭분석 보고서 생성
        gap_analysis_report = generate_gap_analysis_report(data)
        
        # 결과 출력
        print(json.dumps(gap_analysis_report, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "error": "갭분석 생성 중 오류가 발생했습니다.",
            "details": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

def generate_gap_analysis_report(data):
    """갭분석 보고서 생성"""
    
    selected_standards = data.get('selectedISOStandards', [])
    total_employees = int(data.get('totalEmployees', 0))
    company_name = data.get('companyName', 'Unknown Company')
    
    # 복잡도 계산
    complexity = calculate_complexity(total_employees)
    
    # ISO 표준별 갭분석 결과
    standards_analysis = []
    for standard in selected_standards:
        analysis = analyze_standard(standard, total_employees, complexity)
        standards_analysis.append(analysis)
    
    # 전체 준비도 계산
    overall_readiness = calculate_overall_readiness(standards_analysis)
    
    # 예상 비용 및 일정 계산
    estimated_cost = calculate_estimated_cost(selected_standards, total_employees)
    estimated_timeline = calculate_timeline(selected_standards, complexity)
    
    # 갭분석 보고서 구성
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
            "complexity": complexity
        },
        "recommendations": generate_recommendations(standards_analysis),
        "nextSteps": [
            "현재 갭분석 보고서를 검토하세요",
            "우선순위가 높은 개선사항부터 시작하세요",
            "LRQA 컨설턴트와 상담을 예약하세요",
            "인증 준비 계획을 수립하세요"
        ],
        "contactInfo": {
            "email": "zzzkorea-sales@lrqa.com",
            "phone": "+82 2 736 6231",
            "website": "https://www.lrqa.com/ko-kr/"
        }
    }
    
    return report

def calculate_complexity(total_employees):
    """복잡도 계산"""
    if total_employees > 100:
        return "High"
    elif total_employees > 50:
        return "Medium"
    else:
        return "Low"

def analyze_standard(standard, total_employees, complexity):
    """개별 ISO 표준 분석"""
    
    # 기본 점수 계산 (직원 수와 복잡도에 따라)
    base_score = 40
    if complexity == "High":
        base_score += random.randint(0, 20)
    elif complexity == "Medium":
        base_score += random.randint(0, 15)
    else:
        base_score += random.randint(0, 10)
    
    # 표준별 특성 반영
    standard_modifiers = {
        "iso9001": 5,  # 품질관리는 상대적으로 쉬움
        "iso14001": 0,  # 환경관리는 보통
        "iso45001": -5  # 안전보건은 상대적으로 어려움
    }
    
    current_score = min(85, base_score + standard_modifiers.get(standard, 0))
    target_score = 85
    gap = target_score - current_score
    
    # 준비도 평가
    if current_score >= 70:
        readiness = "Good"
    elif current_score >= 50:
        readiness = "Fair"
    else:
        readiness = "Poor"
    
    # 개선 영역 및 권장사항
    critical_gaps = get_critical_gaps(standard, current_score)
    recommendations = get_recommendations(standard, current_score, complexity)
    
    # 예상 준비 시간
    preparation_time = get_preparation_time(complexity, current_score)
    
    return {
        "standard": standard,
        "standardName": get_standard_name(standard),
        "currentScore": current_score,
        "targetScore": target_score,
        "gap": gap,
        "readiness": readiness,
        "criticalGaps": critical_gaps,
        "recommendations": recommendations,
        "preparationTime": preparation_time,
        "priority": "High" if gap > 20 else "Medium" if gap > 10 else "Low"
    }

def get_standard_name(standard):
    """표준명 반환"""
    names = {
        "iso9001": "ISO 9001 - 품질경영시스템",
        "iso14001": "ISO 14001 - 환경경영시스템",
        "iso45001": "ISO 45001 - 안전보건경영시스템"
    }
    return names.get(standard, standard)

def get_critical_gaps(standard, score):
    """핵심 갭 영역 식별"""
    
    gap_areas = {
        "iso9001": [
            "품질 정책 및 목표 설정",
            "고객 요구사항 관리",
            "공급업체 관리",
            "내부 심사 체계",
            "시정조치 및 예방조치"
        ],
        "iso14001": [
            "환경 정책 수립",
            "환경 목표 및 프로그램",
            "법적 요구사항 준수",
            "환경 측정 및 모니터링",
            "비상 대응 계획"
        ],
        "iso45001": [
            "안전보건 정책",
            "위험성 평가 및 관리",
            "사고 조사 및 분석",
            "안전 교육 및 훈련",
            "보호구 및 안전장비 관리"
        ]
    }
    
    areas = gap_areas.get(standard, ["정책 수립", "절차 문서화", "교육 실시", "성과 측정"])
    
    # 점수에 따라 갭 영역 선택
    if score < 50:
        return areas[:4]  # 상위 4개
    elif score < 70:
        return areas[:3]  # 상위 3개
    else:
        return areas[:2]  # 상위 2개

def get_recommendations(standard, score, complexity):
    """권장사항 생성"""
    
    recommendations = []
    
    if score < 50:
        recommendations.extend([
            "기본 정책 및 절차 수립이 필요합니다",
            "전담 조직 구성 및 역할 분담을 명확히 하세요",
            "외부 컨설팅을 통한 체계적 접근을 고려하세요",
            "단계별 실행 계획을 수립하세요"
        ])
    elif score < 70:
        recommendations.extend([
            "핵심 절차를 문서화하고 표준화하세요",
            "직원 교육 프로그램을 강화하세요",
            "성과 측정 및 모니터링 체계를 구축하세요",
            "지속적 개선 활동을 활성화하세요"
        ])
    else:
        recommendations.extend([
            "현재 수준을 유지하고 지속적으로 개선하세요",
            "정기적인 내부 심사를 실시하세요",
            "벤치마킹을 통한 우수 사례 도입을 검토하세요",
            "인증 준비를 위한 최종 점검을 실시하세요"
        ])
    
    # 복잡도에 따른 추가 권장사항
    if complexity == "High":
        recommendations.append("대규모 조직에 적합한 관리 체계를 구축하세요")
    elif complexity == "Medium":
        recommendations.append("중간 규모 조직에 맞는 효율적인 시스템을 구축하세요")
    
    return recommendations

def get_preparation_time(complexity, score):
    """예상 준비 시간 계산"""
    
    base_months = {
        "Low": 6,
        "Medium": 8,
        "High": 12
    }
    
    base_time = base_months[complexity]
    
    # 점수에 따른 조정
    if score < 50:
        adjustment = 4
    elif score < 70:
        adjustment = 2
    else:
        adjustment = 0
    
    total_months = base_time + adjustment
    return f"{total_months}개월"

def calculate_overall_readiness(standards_analysis):
    """전체 준비도 계산"""
    if not standards_analysis:
        return "Unknown"
    
    avg_score = sum(std['currentScore'] for std in standards_analysis) / len(standards_analysis)
    
    if avg_score >= 70:
        return "Good"
    elif avg_score >= 50:
        return "Fair"
    else:
        return "Poor"

def calculate_estimated_cost(standards, total_employees):
    """예상 비용 계산"""
    base_cost = 5000000  # 500만원 기본비용
    per_standard = 3000000  # 표준당 300만원
    per_employee = 50000 if total_employees > 50 else 30000  # 직원당 비용
    
    total_cost = base_cost + (len(standards) * per_standard) + (total_employees * per_employee)
    return f"{int(total_cost / 10000)}만원"

def calculate_timeline(standards, complexity):
    """예상 일정 계산"""
    base_months = {
        "Low": 6,
        "Medium": 8,
        "High": 12
    }
    
    base_time = base_months[complexity]
    standard_bonus = 2 if len(standards) > 1 else 0
    
    return f"{base_time + standard_bonus}개월"

def generate_recommendations(standards_analysis):
    """전체 권장사항 생성"""
    recommendations = [
        "전사적인 경영시스템 구축을 위한 최고경영진의 의지와 지원이 필요합니다",
        "각 표준별로 전담 담당자를 지정하고 명확한 역할과 책임을 부여하세요",
        "단계별 실행 계획을 수립하고 정기적으로 진행 상황을 점검하세요",
        "직원들의 인식 제고를 위한 교육 프로그램을 체계적으로 운영하세요"
    ]
    
    # 표준별 특화 권장사항
    standards = [std['standard'] for std in standards_analysis]
    
    if 'iso9001' in standards:
        recommendations.append("고객 만족도 측정 및 개선 활동을 강화하세요")
    
    if 'iso14001' in standards:
        recommendations.append("환경 영향 평가 및 법적 요구사항 준수를 체계화하세요")
    
    if 'iso45001' in standards:
        recommendations.append("위험성 평가 및 안전보건 교육을 정기적으로 실시하세요")
    
    return recommendations

if __name__ == "__main__":
    main()
