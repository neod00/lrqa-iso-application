const DocxTemplate = require('docxtemplater');
const PizZip = require('pizzip');
const fs = require('fs');
const path = require('path');

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
        console.log('=== 견적서 생성 시작 ===');
        
        const requestBody = JSON.parse(event.body);
        const { timestamp, applicationData } = requestBody;
        
        if (!timestamp || !applicationData) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'Missing required data: timestamp and applicationData' 
                })
            };
        }

        console.log('견적서 데이터:', applicationData);

        // 견적서 데이터 변환
        const quotationData = convertApplicationToQuotationData(applicationData);
        
        // LRQA 템플릿 기반 Word 문서 생성
        const buffer = await createQuotationFromTemplate(quotationData);
        
        // Base64로 인코딩
        const base64File = buffer.toString('base64');

        console.log('=== 견적서 생성 완료 ===');

        return {
            statusCode: 200,
            headers: {
                ...headers,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                success: true,
                message: '견적서가 성공적으로 생성되었습니다.',
                filename: `LRQA_견적서_${applicationData['법인명(국문)'] || 'Unknown'}_${new Date().toISOString().split('T')[0]}.docx`,
                fileData: base64File
            })
        };

    } catch (error) {
        console.error('=== 견적서 생성 오류 ===');
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
                details: error.message
            })
        };
    }
};

/**
 * 신청서 데이터를 견적서 생성용 데이터로 변환
 */
function convertApplicationToQuotationData(applicationData) {
    // 표준 정보 추출
    const standards = [];
    if (applicationData['ISO표준']) {
        const isoStandards = applicationData['ISO표준'];
        if (isoStandards.includes('ISO 9001') || isoStandards.includes('ISO9001')) {
            standards.push('ISO 9001');
        }
        if (isoStandards.includes('ISO 14001') || isoStandards.includes('ISO14001')) {
            standards.push('ISO 14001');
        }
        if (isoStandards.includes('ISO 45001') || isoStandards.includes('ISO45001')) {
            standards.push('ISO 45001');
        }
    }

    // 기본값 설정
    if (standards.length === 0) {
        standards.push('ISO 9001');
    }

    // 직원 수
    const totalEmployees = parseInt(applicationData['총직원수']) || 30;
    
    // 견적 계산 (간단한 로직)
    const baseDays = calculateAuditDays(totalEmployees, standards.length);
    const dayRate = 1400000; // 1 manday 단가
    const subtotal = baseDays * dayRate;
    const vat = subtotal * 0.1;
    const totalCost = subtotal + vat;

    return {
        // 회사 정보
        companyName: applicationData['법인명(국문)'] || '알 수 없음',
        companyNameEn: applicationData['법인명(영문)'] || applicationData['법인명(국문)'] || 'Unknown',
        address: applicationData['본사주소'] || '서울시 강남구',
        contactName: applicationData['담당자명'] || '알 수 없음',
        contactEmail: applicationData['담당자이메일'] || 'unknown@example.com',
        contactPhone: applicationData['담당자전화'] || '010-0000-0000',
        
        // 견적 정보
        quotationNumber: `LRQA-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`,
        quotationDate: new Date().toLocaleDateString('ko-KR'),
        validUntil: new Date(Date.now() + 90*24*60*60*1000).toLocaleDateString('ko-KR'),
        
        // 표준 정보
        standards: standards,
        standardsText: standards.join(', '),
        
        // 직원 정보
        totalEmployees: totalEmployees,
        
        // 견적 상세
        auditDays: baseDays,
        dayRate: dayRate,
        subtotal: subtotal,
        vat: vat,
        totalCost: totalCost,
        
        // 기타
        isIntegrated: applicationData['다중표준시스템'] === '예',
        remoteAudit: applicationData['원격심사'] === '예'
    };
}

/**
 * 심사일수 계산 (간단한 로직)
 */
function calculateAuditDays(employees, standardCount) {
    let baseDays = 0;
    
    // 직원 수에 따른 기본 일수
    if (employees <= 10) {
        baseDays = 1.5;
    } else if (employees <= 50) {
        baseDays = 2.0;
    } else if (employees <= 100) {
        baseDays = 2.5;
    } else if (employees <= 250) {
        baseDays = 3.0;
    } else if (employees <= 500) {
        baseDays = 3.5;
    } else {
        baseDays = 4.0;
    }
    
    // 표준 수에 따른 가중치
    const standardMultiplier = Math.min(standardCount * 0.3, 0.6); // 최대 60% 증가
    baseDays = baseDays * (1 + standardMultiplier);
    
    return Math.round(baseDays * 10) / 10; // 소수점 첫째자리까지
}

/**
 * LRQA 템플릿을 사용한 Word 문서 생성
 */
async function createQuotationFromTemplate(data) {
    try {
        // 템플릿 파일 경로
        const templatePath = path.join(__dirname, 'templates', 'LRQA_quotation.docx');
        
        // 템플릿 파일 읽기
        const templateBuffer = fs.readFileSync(templatePath);
        
        // PizZip으로 압축 해제
        const zip = new PizZip(templateBuffer);
        
        // DocxTemplate 인스턴스 생성
        const doc = new DocxTemplate(zip);
        
        // 템플릿 데이터 설정
        doc.setData({
            // 회사 정보
            client_name: data.companyName,
            client_name_en: data.companyNameEn,
            client_address: data.address,
            contact_person: data.contactName,
            contact_email: data.contactEmail,
            contact_phone: data.contactPhone,
            
            // 견적 정보
            quotation_number: data.quotationNumber,
            quotation_date: data.quotationDate,
            valid_until: data.validUntil,
            
            // 표준 정보
            standards_text: data.standardsText,
            has_iso9001: data.standards.includes('ISO 9001'),
            has_iso14001: data.standards.includes('ISO 14001'),
            has_iso45001: data.standards.includes('ISO 45001'),
            
            // 직원 정보
            total_employees: data.totalEmployees,
            
            // 견적 상세
            total_audit_days: data.auditDays,
            day_rate: data.dayRate,
            subtotal: data.subtotal,
            vat_amount: data.vat,
            total_cost: data.totalCost,
            
            // 추가 정보
            is_integrated: data.isIntegrated,
            remote_audit: data.remoteAudit,
            
            // 기타
            prepared_by: 'LRQA Korea',
            prepared_title: '사업개발본부'
        });
        
        // 템플릿 렌더링
        doc.render();
        
        // Buffer로 변환
        const buffer = doc.getZip().generate({ type: 'nodebuffer' });
        
        return buffer;
        
    } catch (error) {
        console.error('템플릿 기반 문서 생성 오류:', error);
        throw new Error(`템플릿 기반 문서 생성 실패: ${error.message}`);
    }
}