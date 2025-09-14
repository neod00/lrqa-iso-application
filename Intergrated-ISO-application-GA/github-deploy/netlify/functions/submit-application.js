exports.handler = async (event, context) => {
    // CORS 헤더 설정
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
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
        // POST 요청만 처리
        if (event.httpMethod !== 'POST') {
            return {
                statusCode: 405,
                headers,
                body: JSON.stringify({ error: 'Method not allowed' })
            };
        }

        // 요청 본문 파싱
        const formData = JSON.parse(event.body);
        console.log('Received form data:', formData);

        // 신청서 데이터 검증
        if (!formData.companyName || !formData.contactEmail) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({
                    success: false,
                    error: '필수 정보가 누락되었습니다.'
                })
            };
        }

        // 신청서 처리 로직
        const applicationResult = await processApplication(formData);

        // 이메일 발송 시뮬레이션
        const emailResult = await sendApplicationEmail(formData);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: '신청서가 성공적으로 제출되었습니다.',
                applicationId: applicationResult.applicationId,
                emailSent: emailResult.success,
                emailId: emailResult.emailId,
                nextSteps: [
                    '신청서 검토 후 1-2 영업일 내에 연락드리겠습니다',
                    '필요한 경우 추가 서류를 요청할 수 있습니다',
                    '심사 일정 조율을 위해 담당자가 연락드리겠습니다'
                ]
            })
        };

    } catch (error) {
        console.error('Error in submit application:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: '신청서 제출 중 오류가 발생했습니다.',
                details: error.message
            })
        };
    }
};

// 신청서 처리 함수
async function processApplication(formData) {
    try {
        // 신청서 ID 생성
        const applicationId = `APP_${Date.now()}`;
        
        // 신청서 데이터 정리
        const applicationData = {
            id: applicationId,
            companyName: formData.companyName || formData.companyNameKo,
            companyNameEn: formData.companyNameEn,
            contactName: formData.contactName,
            contactEmail: formData.contactEmail,
            contactPhone: formData.contactPhone,
            mobilePhone: formData.mobilePhone,
            department: formData.department,
            headOfficeAddress: formData.headOfficeAddress,
            city: formData.city,
            province: formData.province,
            postalCode: formData.postalCode,
            country: formData.country,
            mainPhone: formData.mainPhone,
            mainEmail: formData.mainEmail,
            totalEmployees: parseInt(formData.totalEmployees) || 0,
            permanentEmployees: parseInt(formData.permanentEmployees) || 0,
            temporaryEmployees: parseInt(formData.temporaryEmployees) || 0,
            siteCount: parseInt(formData.siteCount) || 1,
            isoStandards: formData.isoStandards || [],
            desiredAuditDate: formData.desiredAuditDate,
            businessType: formData.businessType,
            dataProcessConsent: formData.dataProcessConsent,
            signature: formData.signature,
            status: '신규',
            receivedAt: new Date().toISOString(),
            estimatedReviewTime: '1-2 영업일',
            assignedTo: 'LRQA Korea Sales Team'
        };

        // 메모리 기반 저장소에 저장 (실제 운영에서는 데이터베이스 사용)
        if (!global.applications) {
            global.applications = [];
        }
        
        // 신청서 저장
        global.applications.push(applicationData);
        console.log('신청서 데이터 저장 완료:', applicationData);
        console.log('총 저장된 신청서 수:', global.applications.length);
        
        return {
            applicationId: applicationId,
            status: 'Received',
            receivedAt: applicationData.receivedAt,
            estimatedReviewTime: '1-2 영업일',
            assignedTo: 'LRQA Korea Sales Team'
        };
        
    } catch (error) {
        console.error('신청서 처리 오류:', error);
        throw error;
    }
}

// 이메일 발송 시뮬레이션
async function sendApplicationEmail(formData) {
    // 실제 이메일 발송 로직은 여기에 구현
    // 현재는 시뮬레이션만 수행
    
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                success: true,
                emailId: `app_${Date.now()}`,
                recipient: formData.contactEmail,
                subject: `[LRQA] ${formData.companyName} 인증 신청서 접수 확인`,
                message: '신청서가 성공적으로 접수되었습니다.'
            });
        }, 1000);
    });
}
