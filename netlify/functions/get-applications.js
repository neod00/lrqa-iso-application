exports.handler = async (event, context) => {
    // CORS 헤더 설정
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // OPTIONS 요청 처리
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    try {
        // 샘플 신청서 데이터 (관리자 화면용)
        const sampleApplications = [
            {
                id: 'APP-2025-001',
                '신청일시': '2025-09-13T12:39:02.710Z',
                '법인명(국문)': '테스트 컴퍼니',
                '법인명(영문)': 'Test Company',
                '담당자명': '김테스트',
                '담당자전화': '010-1234-5678',
                '담당자이메일': 'kim.test@testcompany.com',
                '인증범위': 'ISO 9001, ISO 14001, ISO 45001',
                '상태': '신규',
                '총직원수': '100',
                '희망년도': '2025',
                '희망월': '12월',
                companyName: '테스트 컴퍼니 (Test Company)',
                contactName: '김테스트 (대리)',
                totalEmployees: 100,
                siteCount: 1,
                isoStandards: ['iso9001', 'iso14001', 'iso45001'],
                desiredAuditDate: '2025-12'
            },
            {
                id: 'APP-2025-002',
                '신청일시': '2025-09-13T14:15:30.000Z',
                '법인명(국문)': '스마트테크솔루션',
                '법인명(영문)': 'Smart Tech Solutions',
                '담당자명': '박스마트',
                '담당자전화': '010-2345-6789',
                '담당자이메일': 'park.smart@smarttech.co.kr',
                '인증범위': 'ISO 9001, ISO 14001, ISO 45001',
                '상태': '신규',
                '총직원수': '85',
                '희망년도': '2025',
                '희망월': '11월',
                companyName: '스마트테크솔루션 (Smart Tech Solutions)',
                contactName: '박스마트 (CTO)',
                totalEmployees: 85,
                siteCount: 2,
                isoStandards: ['iso9001', 'iso14001', 'iso45001'],
                desiredAuditDate: '2025-11'
            },
            {
                id: 'APP-2025-003',
                '신청일시': '2025-09-10T14:20:00Z',
                '법인명(국문)': '예시 기업',
                '법인명(영문)': 'Example Corp',
                '담당자명': '이담당',
                '담당자전화': '010-9876-5432',
                '담당자이메일': 'lee@example.com',
                '인증범위': 'ISO 9001',
                '상태': '진행중',
                '총직원수': '50',
                '희망년도': '2025',
                '희망월': '11월',
                companyName: '예시 기업 (Example Corp)',
                contactName: '이담당 (과장)',
                totalEmployees: 50,
                siteCount: 1,
                isoStandards: ['iso9001'],
                desiredAuditDate: '2025-11'
            },
            {
                id: 'APP-2025-004',
                '신청일시': '2025-09-09T16:45:00Z',
                '법인명(국문)': '샘플 회사',
                '법인명(영문)': 'Sample Company',
                '담당자명': '박담당',
                '담당자전화': '010-5555-6666',
                '담당자이메일': 'park@sample.com',
                '인증범위': 'ISO 9001, ISO 14001',
                '상태': '완료',
                '총직원수': '30',
                '희망년도': '2025',
                '희망월': '10월',
                companyName: '샘플 회사 (Sample Company)',
                contactName: '박담당 (대리)',
                totalEmployees: 30,
                siteCount: 1,
                isoStandards: ['iso9001', 'iso14001'],
                desiredAuditDate: '2025-10'
            }
        ];

        // 통계 계산
        const stats = {
            total: sampleApplications.length,
            new: sampleApplications.filter(app => app.상태 === '신규').length,
            monthly: sampleApplications.filter(app => {
                const date = new Date(app.신청일시);
                const now = new Date();
                return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
            }).length,
            completed: sampleApplications.filter(app => app.상태 === '완료').length
        };

        // Google Sheets URL (샘플)
        const sheetUrl = 'https://docs.google.com/spreadsheets/d/1sample_sheet_id';

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                data: {
                    applications: sampleApplications,
                    stats: stats,
                    sheetUrl: sheetUrl
                }
            })
        };

    } catch (error) {
        console.error('Error in get-applications:', error);
        
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                message: '신청서 데이터를 불러오는 중 오류가 발생했습니다.',
                error: error.message
            })
        };
    }
};
