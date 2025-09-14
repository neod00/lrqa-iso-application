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
        const { recipientEmail, companyName, reportContent } = JSON.parse(event.body);
        console.log(`Sending gap analysis email to ${recipientEmail} for ${companyName}`);

        // 이메일 발송 시뮬레이션
        const emailId = `gap_email_${Date.now()}`;
        
        // 실제 이메일 발송 로직은 여기에 구현
        // 현재는 시뮬레이션만 수행
        
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: '갭분석 보고서가 성공적으로 발송되었습니다.',
                emailId: emailId,
                recipient: recipientEmail,
                subject: `[LRQA] ${companyName} ISO 갭분석 보고서`,
                reportContentPreview: reportContent ? reportContent.substring(0, 100) + '...' : 'No content',
                sentAt: new Date().toISOString()
            })
        };
    } catch (error) {
        console.error('Error sending gap analysis email:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                message: '갭분석 보고서 발송 중 오류가 발생했습니다.',
                error: error.message
            })
        };
    }
};
