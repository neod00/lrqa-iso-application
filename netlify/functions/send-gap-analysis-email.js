/**
 * 갭분석 보고서 이메일 발송 함수
 */

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
        if (event.httpMethod !== 'POST') {
            return {
                statusCode: 405,
                headers,
                body: JSON.stringify({ error: 'Method not allowed' })
            };
        }

        const { email, report } = JSON.parse(event.body);

        if (!email || !report) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'Email and report are required' })
            };
        }

        // 이메일 발송 시뮬레이션 (실제로는 SendGrid, AWS SES 등을 사용)
        console.log('갭분석 보고서 이메일 발송:', {
            to: email,
            companyName: report.companyName,
            analysisDate: report.analysisDate
        });

        // 실제 이메일 발송 로직은 여기에 구현
        // 예: SendGrid, AWS SES, Nodemailer 등 사용

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: '갭분석 보고서가 이메일로 발송되었습니다.',
                email: email
            })
        };

    } catch (error) {
        console.error('이메일 발송 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: '이메일 발송 중 오류가 발생했습니다.',
                message: error.message
            })
        };
    }
};
