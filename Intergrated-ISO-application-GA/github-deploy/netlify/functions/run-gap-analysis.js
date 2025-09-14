exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    if (event.httpMethod !== 'POST') {
        return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
    }

    try {
        const { formData, selectedStandards } = JSON.parse(event.body);
        console.log('Running gap analysis for:', formData.companyName, 'Standards:', selectedStandards);

        // 갭분석 시뮬레이션
        const analysisResult = {
            companyName: formData.companyName,
            standards: selectedStandards,
            analysisDate: new Date().toISOString(),
            report: generateGapAnalysisReport(formData, selectedStandards),
            recommendations: generateRecommendations(selectedStandards),
            readinessScore: calculateReadinessScore(formData, selectedStandards),
            estimatedTimeline: calculateTimeline(selectedStandards),
            status: 'Completed'
        };

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: '갭분석이 완료되었습니다.',
                result: analysisResult
            })
        };
    } catch (error) {
        console.error('Error in gap analysis:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                message: '갭분석 중 오류가 발생했습니다.',
                error: error.message
            })
        };
    }
};

// 갭분석 보고서 생성
function generateGapAnalysisReport(formData, selectedStandards) {
    return {
        executiveSummary: `${formData.companyName}의 ${selectedStandards.join(', ')} 인증 준비도 분석 결과`,
        currentStatus: '기본적인 경영시스템 구축이 필요한 상태',
        gaps: [
            '문서화된 경영시스템 부족',
            '직원 교육 프로그램 미비',
            '내부심사 체계 부재',
            '지속적 개선 프로세스 부족'
        ],
        strengths: [
            '기본적인 조직 구조 구축',
            '품질에 대한 인식 개선 필요',
            '고객 만족도 향상 의지'
        ],
        nextSteps: [
            '경영시스템 문서화',
            '직원 교육 프로그램 수립',
            '내부심사 체계 구축',
            '지속적 개선 프로세스 도입'
        ]
    };
}

// 권장사항 생성
function generateRecommendations(selectedStandards) {
    const recommendations = [];
    
    if (selectedStandards.includes('iso9001')) {
        recommendations.push({
            standard: 'ISO 9001',
            priority: 'High',
            action: '품질경영시스템 문서화 및 프로세스 구축',
            timeline: '3-6개월'
        });
    }
    
    if (selectedStandards.includes('iso14001')) {
        recommendations.push({
            standard: 'ISO 14001',
            priority: 'Medium',
            action: '환경경영시스템 구축 및 환경영향 평가',
            timeline: '4-8개월'
        });
    }
    
    if (selectedStandards.includes('iso45001')) {
        recommendations.push({
            standard: 'ISO 45001',
            priority: 'High',
            action: '안전보건경영시스템 구축 및 위험관리 체계 수립',
            timeline: '3-6개월'
        });
    }
    
    return recommendations;
}

// 준비도 점수 계산
function calculateReadinessScore(formData, selectedStandards) {
    let score = 0;
    
    // 기본 점수
    score += 20;
    
    // 직원 수에 따른 점수
    if (formData.totalEmployees > 50) score += 10;
    if (formData.totalEmployees > 100) score += 10;
    
    // 사업장 수에 따른 점수
    if (formData.siteCount > 1) score += 5;
    
    // ISO 표준 수에 따른 점수
    score += selectedStandards.length * 15;
    
    return Math.min(score, 100);
}

// 예상 소요 시간 계산
function calculateTimeline(selectedStandards) {
    const baseMonths = 3;
    const additionalMonths = selectedStandards.length * 2;
    return `${baseMonths + additionalMonths}개월`;
}
