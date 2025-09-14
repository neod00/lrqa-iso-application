exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // OPTIONS 요청 처리 (CORS preflight)
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    if (event.httpMethod !== 'GET') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ 
                success: false, 
                error: 'Method not allowed' 
            })
        };
    }

    try {
        // 실제 환경에서는 데이터베이스에서 실제 통계를 계산합니다
        // 현재는 테스트용 더미 데이터를 제공합니다
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();

        // 모의 대시보드 통계 데이터
        const dashboardStats = {
            totalApplications: 15,
            newApplications: 3,
            monthlyApplications: 8,
            completedApplications: 12,
            pendingApplications: 3,
            quotationsGenerated: 10,
            lastUpdated: now.toISOString(),
            monthlyTrend: {
                applications: [5, 8, 12, 15, 8], // 최근 5개월
                quotations: [4, 6, 10, 12, 10]
            },
            topISOStandards: [
                { standard: 'ISO 9001', count: 12 },
                { standard: 'ISO 14001', count: 8 },
                { standard: 'ISO 45001', count: 6 }
            ],
            businessTypes: [
                { type: '제조업', count: 6 },
                { type: '서비스업', count: 4 },
                { type: '소프트웨어 개발', count: 3 },
                { type: '기타', count: 2 }
            ],
            recentActivity: [
                {
                    type: 'application',
                    message: '테스트 컴퍼니에서 새 신청서를 제출했습니다.',
                    timestamp: now.toISOString()
                },
                {
                    type: 'quotation',
                    message: '예시 기업의 견적서가 생성되었습니다.',
                    timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString()
                },
                {
                    type: 'application',
                    message: '샘플 회사의 신청서 처리가 완료되었습니다.',
                    timestamp: new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString()
                }
            ]
        };

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                data: dashboardStats,
                message: '대시보드 데이터를 성공적으로 조회했습니다.'
            })
        };

    } catch (error) {
        console.error('Error in get-dashboard:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: 'Internal server error',
                message: '대시보드 데이터 조회 중 오류가 발생했습니다.'
            })
        };
    }
};
