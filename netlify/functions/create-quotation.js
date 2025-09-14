/**
 * 견적서 생성 함수
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

        const { applicationId, quotationData } = JSON.parse(event.body);

        if (!applicationId) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'Application ID is required' })
            };
        }

        // 견적서 생성 로직
        const quotation = await generateQuotation(applicationId, quotationData);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                quotation: quotation,
                message: '견적서가 성공적으로 생성되었습니다.'
            })
        };

    } catch (error) {
        console.error('견적서 생성 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: '견적서 생성 중 오류가 발생했습니다.',
                message: error.message
            })
        };
    }
};

// 견적서 생성 함수
async function generateQuotation(applicationId, quotationData) {
    const quotationId = `QUO_${Date.now()}`;
    const currentDate = new Date();
    
    // 기본 견적서 구조
    const quotation = {
        id: quotationId,
        applicationId: applicationId,
        quotationNumber: `LRQA-${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}-${quotationId.slice(-4)}`,
        createdDate: currentDate.toISOString(),
        validUntil: new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30일 후
        status: 'Draft',
        
        // 신청서 정보
        companyInfo: {
            name: quotationData?.companyName || '신청기업',
            contactName: quotationData?.contactName || '담당자',
            email: quotationData?.contactEmail || 'contact@company.com',
            phone: quotationData?.contactPhone || '010-0000-0000'
        },
        
        // 인증 정보
        certification: {
            standards: quotationData?.isoStandards || ['ISO 9001'],
            scope: quotationData?.businessScope || '제조업',
            sites: quotationData?.siteCount || 1,
            employees: quotationData?.totalEmployees || 50
        },
        
        // 견적 항목
        items: [
            {
                id: 'cert_audit',
                description: '인증 심사비',
                quantity: 1,
                unitPrice: calculateAuditFee(quotationData),
                total: calculateAuditFee(quotationData)
            },
            {
                id: 'cert_certificate',
                description: '인증서 발급비',
                quantity: 1,
                unitPrice: 500000,
                total: 500000
            },
            {
                id: 'cert_surveillance',
                description: '사후관리비 (연간)',
                quantity: 1,
                unitPrice: calculateSurveillanceFee(quotationData),
                total: calculateSurveillanceFee(quotationData)
            }
        ],
        
        // 총액 계산
        subtotal: 0,
        vat: 0,
        total: 0,
        
        // 결제 조건
        paymentTerms: {
            currency: 'KRW',
            paymentMethod: 'Bank Transfer',
            paymentDue: '견적서 승인 후 7일 이내',
            validityPeriod: '30일'
        },
        
        // 추가 정보
        notes: [
            '본 견적서는 30일간 유효합니다.',
            '가격은 부가세가 포함된 금액입니다.',
            '실제 심사 일정은 별도 협의를 통해 결정됩니다.',
            '추가 서류가 필요한 경우 별도 안내드립니다.'
        ]
    };

    // 총액 계산
    quotation.subtotal = quotation.items.reduce((sum, item) => sum + item.total, 0);
    quotation.vat = Math.round(quotation.subtotal * 0.1); // 10% 부가세
    quotation.total = quotation.subtotal + quotation.vat;

    console.log('견적서 생성됨:', quotation);

    return quotation;
}

// 심사비 계산 함수
function calculateAuditFee(data) {
    const baseFee = 2000000; // 기본 심사비 200만원
    const employeeCount = parseInt(data?.totalEmployees) || 50;
    const siteCount = parseInt(data?.siteCount) || 1;
    const standardCount = (data?.isoStandards?.length) || 1;
    
    // 직원 수에 따른 추가 비용
    let employeeMultiplier = 1;
    if (employeeCount > 100) employeeMultiplier = 1.2;
    if (employeeCount > 500) employeeMultiplier = 1.5;
    if (employeeCount > 1000) employeeMultiplier = 2.0;
    
    // 사업장 수에 따른 추가 비용
    const siteMultiplier = 1 + (siteCount - 1) * 0.3;
    
    // 표준 수에 따른 추가 비용
    const standardMultiplier = 1 + (standardCount - 1) * 0.4;
    
    return Math.round(baseFee * employeeMultiplier * siteMultiplier * standardMultiplier);
}

// 사후관리비 계산 함수
function calculateSurveillanceFee(data) {
    const auditFee = calculateAuditFee(data);
    return Math.round(auditFee * 0.6); // 심사비의 60%
}
