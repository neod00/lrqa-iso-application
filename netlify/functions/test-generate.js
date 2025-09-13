/**
 * 간단한 테스트 견적서 생성 함수
 */

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

    if (event.httpMethod !== 'POST') {
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
        console.log('=== 테스트 견적서 생성 시작 ===');
        
        // 요청 데이터 파싱
        const requestData = JSON.parse(event.body);
        console.log('받은 데이터:', Object.keys(requestData));

        // 간단한 견적서 데이터 생성
        const quotationData = {
            companyName: requestData.companyName || '테스트 회사',
            contactPerson: requestData.contactPerson || '김테스트',
            auditDays: 3,
            auditFee: 4350000,
            expenses: 435000,
            totalAmount: 4785000,
            generatedDate: new Date().toISOString(),
            success: true
        };

        console.log('견적서 데이터 생성 완료:', quotationData);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: '테스트 견적서가 성공적으로 생성되었습니다',
                data: quotationData
            })
        };

    } catch (error) {
        console.error('견적서 생성 오류:', error);
        
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: error.message,
                details: error.stack
            })
        };
    }
};
