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
        // 실제 환경에서는 데이터베이스나 파일에서 데이터를 읽어옵니다
        // 현재는 테스트용 더미 데이터를 제공합니다
        const mockApplications = [
            {
                id: 'APP-2025-001',
                timestamp: new Date().toISOString(),
                companyName: '테스트 컴퍼니 (Test Company)',
                contactName: '김테스트 (대리)',
                contactEmail: 'kim.test@testcompany.com',
                contactPhone: '02-1234-5679',
                totalEmployees: 50,
                siteCount: 1,
                isoStandards: ['iso9001', 'iso14001', 'iso45001'],
                desiredAuditDate: '2025-12',
                businessType: '소프트웨어 개발',
                address: '서울시 강남구 테헤란로 123',
                status: 'new',
                submittedAt: new Date().toISOString()
            },
            {
                id: 'APP-2025-002',
                timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
                companyName: '예시 기업 (Example Corp)',
                contactName: '이담당 (과장)',
                contactEmail: 'lee.manager@example.com',
                contactPhone: '02-9876-5432',
                totalEmployees: 100,
                siteCount: 2,
                isoStandards: ['iso9001'],
                desiredAuditDate: '2025-11',
                businessType: '제조업',
                address: '경기도 성남시 분당구 판교로 123',
                status: 'in_progress',
                submittedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
            },
            {
                id: 'APP-2025-003',
                timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
                companyName: '샘플 회사 (Sample Company)',
                contactName: '박담당 (대리)',
                contactEmail: 'park.rep@sample.com',
                contactPhone: '02-1111-2222',
                totalEmployees: 25,
                siteCount: 1,
                isoStandards: ['iso14001', 'iso45001'],
                desiredAuditDate: '2025-10',
                businessType: '서비스업',
                address: '서울시 종로구 세종대로 123',
                status: 'completed',
                submittedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
            }
        ];

        // 통계 데이터 계산
        const stats = {
            total: mockApplications.length,
            new: mockApplications.filter(app => app.status === 'new').length,
            inProgress: mockApplications.filter(app => app.status === 'in_progress').length,
            completed: mockApplications.filter(app => app.status === 'completed').length,
            thisMonth: mockApplications.filter(app => {
                const appDate = new Date(app.submittedAt);
                const now = new Date();
                return appDate.getMonth() === now.getMonth() && 
                       appDate.getFullYear() === now.getFullYear();
            }).length
        };

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                data: {
                    applications: mockApplications,
                    stats: stats
                },
                message: '신청서 목록을 성공적으로 조회했습니다.'
            })
        };

    } catch (error) {
        console.error('Error in get-applications:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: 'Internal server error',
                message: '신청서 목록 조회 중 오류가 발생했습니다.'
            })
        };
    }
};
