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

    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ 
                success: false, 
                error: 'Method not allowed',
                message: 'POST 요청만 허용됩니다.'
            })
        };
    }

    try {
        console.log('=== 견적서 생성 테스트 시작 ===');
        
        const requestBody = JSON.parse(event.body);
        console.log('요청 본문 파싱 완료');
        
        const { quotationData, adminEmail } = requestBody;
        console.log('견적서 데이터:', quotationData);
        console.log('관리자 이메일:', adminEmail);

        // 간단한 JSON 응답 반환 (Word 문서 대신)
        const response = {
            success: true,
            message: '견적서 생성 테스트 성공',
            quotationData: {
                id: quotationData.id || 'TEST-001',
                companyName: quotationData.companyName || '테스트 회사',
                contactName: quotationData.contactName || '담당자',
                contactEmail: quotationData.contactEmail || 'test@example.com',
                totalEmployees: quotationData.totalEmployees || '100',
                isoStandards: quotationData.isoStandards || ['ISO 9001'],
                quotationNumber: `LRQA-${Date.now()}`,
                quotationDate: new Date().toLocaleDateString('ko-KR'),
                validUntil: new Date(Date.now() + 30*24*60*60*1000).toLocaleDateString('ko-KR'),
                totalCost: '₩4,785,000',
                auditDays: '3 mandays',
                subtotal: '₩4,350,000',
                vat: '₩435,000'
            },
            adminEmail: adminEmail,
            generatedAt: new Date().toISOString()
        };

        console.log('=== 견적서 생성 테스트 성공 ===');

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(response)
        };

    } catch (error) {
        console.error('=== 견적서 생성 테스트 오류 ===');
        console.error('Error:', error);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: 'Internal server error',
                message: '견적서 생성 중 오류가 발생했습니다.',
                details: error.message,
                stack: error.stack
            })
        };
    }
};