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
        // 저장된 신청서 데이터 가져오기
        const storedApplications = global.applications || [];
        
        // 샘플 신청서 데이터 (기본 데이터)
        const sampleApplications = [
            {
                id: 'sample_1',
                '신청일시': '2025-01-15T09:30:00Z',
                '법인명(국문)': '테크노제조',
                '법인명(영문)': 'Techno Manufacturing',
                '담당자명': '김철수',
                '담당자전화': '010-1234-5678',
                '담당자이메일': 'kim@techno.com',
                '인증범위': 'ISO 9001, ISO 14001',
                '상태': '신규',
                '총직원수': '50',
                '희망년도': '2025',
                '희망월': '3월'
            },
            {
                id: 'sample_2',
                '신청일시': '2025-01-14T14:20:00Z',
                '법인명(국문)': '그린환경',
                '법인명(영문)': 'Green Environment',
                '담당자명': '이영희',
                '담당자전화': '010-9876-5432',
                '담당자이메일': 'lee@green.com',
                '인증범위': 'ISO 14001, ISO 45001',
                '상태': '진행중',
                '총직원수': '25',
                '희망년도': '2025',
                '희망월': '4월'
            },
            {
                id: 'sample_3',
                '신청일시': '2025-01-13T11:15:00Z',
                '법인명(국문)': '안전건설',
                '법인명(영문)': 'Safety Construction',
                '담당자명': '박민수',
                '담당자전화': '010-5555-1234',
                '담당자이메일': 'park@safety.com',
                '인증범위': 'ISO 45001',
                '상태': '완료',
                '총직원수': '120',
                '희망년도': '2025',
                '희망월': '2월'
            }
        ];
        
        // 저장된 신청서를 관리자 페이지 형식으로 변환
        const convertedApplications = storedApplications.map(app => ({
            '신청일시': app.receivedAt,
            '법인명(국문)': app.companyName,
            '법인명(영문)': app.companyNameEn || '',
            '담당자명': app.contactName,
            '담당자전화': app.mobilePhone || app.contactPhone,
            '담당자이메일': app.contactEmail,
            '인증범위': Array.isArray(app.isoStandards) ? app.isoStandards.join(', ') : app.isoStandards || '',
            '상태': app.status,
            '총직원수': app.totalEmployees?.toString() || '0',
            '희망년도': app.desiredAuditDate ? app.desiredAuditDate.split('-')[0] : '2025',
            '희망월': app.desiredAuditDate ? `${app.desiredAuditDate.split('-')[1]}월` : '12월'
        }));
        
        // 샘플 데이터와 저장된 데이터 결합
        const allApplications = [...convertedApplications, ...sampleApplications];

        // 통계 계산
        const stats = {
            total: allApplications.length,
            new: allApplications.filter(app => app.상태 === '신규').length,
            monthly: allApplications.filter(app => {
                const date = new Date(app.신청일시);
                const now = new Date();
                return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
            }).length,
            completed: allApplications.filter(app => app.상태 === '완료').length
        };

        // Google Sheets URL (샘플)
        const sheetUrl = 'https://docs.google.com/spreadsheets/d/1sample_sheet_id';

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                data: {
                    applications: allApplications,
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
