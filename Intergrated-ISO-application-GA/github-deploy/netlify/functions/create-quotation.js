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
        const { applicationId, quotationData, adminEmail } = JSON.parse(event.body);
        console.log(`Creating quotation for application ID: ${applicationId}`);
        console.log('Quotation Data:', quotationData);
        console.log('Admin Email:', adminEmail);

        // 저장된 신청서에서 데이터 찾기
        const storedApplications = global.applications || [];
        let application = storedApplications.find(app => app.id === applicationId);
        
        // 저장된 신청서에서 찾지 못한 경우 샘플 데이터에서 찾기
        if (!application) {
            const sampleApplications = [
                {
                    id: 'sample_1',
                    companyName: '샘플제조업체',
                    contactName: '김철수',
                    contactEmail: 'kim@sample.com',
                    isoStandards: ['ISO 9001'],
                    totalEmployees: 30,
                    siteCount: 1
                }
            ];
            application = sampleApplications.find(app => app.id === applicationId);
        }
        
        // 여전히 찾지 못한 경우 quotationData에서 직접 정보 추출
        if (!application && quotationData) {
            application = {
                id: applicationId,
                companyName: quotationData['법인명(국문)'] || quotationData.companyName || '알 수 없음',
                contactName: quotationData['담당자명'] || quotationData.contactName || '알 수 없음',
                contactEmail: quotationData['담당자이메일'] || quotationData.contactEmail || '알 수 없음',
                isoStandards: quotationData['인증범위'] ? [quotationData['인증범위']] : ['ISO 9001'],
                totalEmployees: parseInt(quotationData['총직원수'] || quotationData.totalEmployees || 30),
                siteCount: parseInt(quotationData.siteCount || 1)
            };
        }
        
        if (!application) {
            return {
                statusCode: 404,
                headers,
                body: JSON.stringify({
                    success: false,
                    message: '신청서를 찾을 수 없습니다.',
                    error: 'Application not found'
                })
            };
        }

        // 견적서 생성 로직
        const quotation = {
            quotationNumber: `Q-${Date.now()}`,
            applicationId: applicationId,
            companyName: application.companyName,
            contactName: application.contactName,
            contactEmail: application.contactEmail,
            isoStandards: application.isoStandards,
            totalEmployees: application.totalEmployees,
            siteCount: application.siteCount,
            totalCost: calculateQuotationCost(application),
            currency: 'KRW',
            issueDate: new Date().toISOString().split('T')[0],
            validUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days validity
            details: generateQuotationDetails(application),
            status: 'Generated',
            // Word 문서 생성을 위한 추가 정보
            wordDocumentPath: null,
            emailSent: false
        };

        // Word 문서 생성 시도
        try {
            const wordDocumentPath = await generateWordDocument(quotation);
            quotation.wordDocumentPath = wordDocumentPath;
        } catch (error) {
            console.log('Word 문서 생성 실패 (계속 진행):', error.message);
        }

        // 견적서 저장 (메모리 기반)
        if (!global.quotations) {
            global.quotations = [];
        }
        global.quotations.push(quotation);

        // 이메일 전송 시도
        let emailResult = null;
        if (adminEmail) {
            try {
                emailResult = await sendQuotationEmail(quotation, adminEmail);
                quotation.emailSent = emailResult.success;
            } catch (error) {
                console.log('이메일 전송 실패 (계속 진행):', error.message);
            }
        }

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                message: '견적서가 성공적으로 생성되었습니다.',
                quotation: quotation,
                emailResult: emailResult
            })
        };
    } catch (error) {
        console.error('Error creating quotation:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                message: '견적서 생성 중 오류가 발생했습니다.',
                error: error.message
            })
        };
    }
};

// 견적서 비용 계산 함수
function calculateQuotationCost(application) {
    const baseCost = 1000000; // 기본 비용
    const employeeMultiplier = Math.ceil(application.totalEmployees / 10) * 100000; // 직원 수에 따른 추가 비용
    const siteMultiplier = (application.siteCount - 1) * 200000; // 추가 사이트당 비용
    const standardMultiplier = application.isoStandards.length * 500000; // ISO 표준 수에 따른 비용
    
    return baseCost + employeeMultiplier + siteMultiplier + standardMultiplier;
}

// 견적서 상세 정보 생성 함수
function generateQuotationDetails(application) {
    return {
        companyInfo: {
            name: application.companyName,
            contact: application.contactName,
            email: application.contactEmail,
            employees: application.totalEmployees,
            sites: application.siteCount
        },
        standards: application.isoStandards,
        services: [
            'ISO 인증 심사',
            '인증서 발급',
            '연간 감사',
            '기술 지원'
        ],
        timeline: '신청서 접수 후 2-4주 내 심사 진행',
        validity: '30일'
    };
}

// Word 문서 생성 함수 (직접 생성)
async function generateWordDocument(quotation) {
    const fs = require('fs');
    const path = require('path');
    
    try {
        // Docxtemplater를 사용하여 직접 Word 문서 생성
        const Docxtemplater = require('docxtemplater');
        const PizZip = require('pizzip');
        
        // 템플릿 파일 경로
        const templatePath = path.join(__dirname, 'templates', 'LRQA_quotation.docx');
        
        // 템플릿 파일 존재 확인
        if (!fs.existsSync(templatePath)) {
            console.log('템플릿 파일이 없습니다. 텍스트 문서로 대체합니다.');
            return generateTextDocument(quotation);
        }
        
        // 템플릿 파일 읽기
        const content = fs.readFileSync(templatePath, 'binary');
        const zip = new PizZip(content);
        
        // Docxtemplater 인스턴스 생성
        const doc = new Docxtemplater(zip, {
            paragraphLoop: true,
            linebreaks: true,
            errorLogging: true
        });
        
        // 템플릿 컨텍스트 데이터 준비
        const context = prepareTemplateContext(quotation);
        
        // 템플릿 렌더링
        doc.render(context);
        
        // Word 문서를 Buffer로 생성
        const buffer = doc.getZip().generate({
            type: 'nodebuffer',
            compression: 'DEFLATE'
        });
        
        // 임시 파일로 저장
        const tempDir = '/tmp';
        const outputFile = path.join(tempDir, `quotation_${quotation.quotationNumber}.docx`);
        
        fs.writeFileSync(outputFile, buffer);
        
        console.log('Word 문서 생성 성공:', outputFile);
        return outputFile;
        
    } catch (error) {
        console.error('Word 문서 생성 오류:', error);
        // 실패 시 텍스트 파일로 대체
        return generateTextDocument(quotation);
    }
}

// 템플릿 컨텍스트 데이터 준비
function prepareTemplateContext(quotation) {
    const isoStandards = quotation.isoStandards || [];
    
    return {
        // 회사 정보
        client_name: quotation.companyName,
        client_name_en: quotation.companyName,
        client_address: "서울시 강남구 테헤란로 123",
        contact_person: quotation.contactName,
        contact_email: quotation.contactEmail,
        contact_phone: "02-1234-5678",
        
        // 견적 정보
        quotation_date: new Date().toLocaleDateString('ko-KR', {year: 'numeric', month: 'long', day: 'numeric'}),
        quotation_number: quotation.quotationNumber,
        valid_until: new Date(Date.now() + 30*24*60*60*1000).toLocaleDateString('ko-KR', {year: 'numeric', month: 'long', day: 'numeric'}),
        
        // 표준 정보
        standards_text: isoStandards.join(', '),
        has_iso9001: isoStandards.some(std => std.toLowerCase().includes('9001')),
        has_iso14001: isoStandards.some(std => std.toLowerCase().includes('14001')),
        has_iso45001: isoStandards.some(std => std.toLowerCase().includes('45001')),
        iso9001_name: 'ISO 9001 품질경영시스템',
        iso14001_name: 'ISO 14001 환경경영시스템',
        iso45001_name: 'ISO 45001 안전보건경영시스템',
        
        // 사업장 정보
        sites: [{
            number: 1,
            name: '본사',
            address: '서울시 강남구 테헤란로 123',
            headcount: quotation.totalEmployees,
            standards: isoStandards.join(', '),
            activities: '제조업'
        }],
        total_sites: quotation.siteCount,
        total_employees: quotation.totalEmployees,
        
        // 견적 상세 정보
        total_audit_days: 3,
        subtotal: Math.floor(quotation.totalCost / 1.1),
        vat_amount: Math.floor(quotation.totalCost * 0.1),
        total_cost: quotation.totalCost,
        total_cost_formatted: quotation.totalCost.toLocaleString(),
        
        // 표준별 개별 일수 및 비용
        stage1_days: 1,
        stage2_days: 2,
        surveillance_days: 1,
        stage1_cost: 500000,
        stage2_cost: 1000000,
        surveillance_cost: 500000,
        
        // 통합심사 정보
        is_integrated: isoStandards.length > 1,
        integration_discount: isoStandards.length > 1 ? 10 : 0,
        
        // 원격심사 정보
        remote_audit_ratio: 30,
        remote_discount: 5,
        
        // 기타
        created_at: new Date().toISOString(),
        prepared_by: 'LRQA Korea',
        prepared_title: '사업개발본부'
    };
}

// 텍스트 문서 생성 (백업용)
function generateTextDocument(quotation) {
    const fs = require('fs');
    const path = require('path');
    
    const tempDir = '/tmp';
    const fileName = `quotation_${quotation.quotationNumber}.txt`;
    const filePath = path.join(tempDir, fileName);
    
    const content = `
LRQA 견적서
견적서 번호: ${quotation.quotationNumber}
회사명: ${quotation.companyName}
담당자: ${quotation.contactName}
이메일: ${quotation.contactEmail}
ISO 표준: ${quotation.isoStandards.join(', ')}
총 직원 수: ${quotation.totalEmployees}
사업장 수: ${quotation.siteCount}
총 비용: ${quotation.totalCost.toLocaleString()}원
발행일: ${quotation.issueDate}
유효기간: ${quotation.validUntil}
    `;
    
    fs.writeFileSync(filePath, content, 'utf8');
    return filePath;
}

// 이메일 전송 함수
async function sendQuotationEmail(quotation, adminEmail) {
    // 실제 이메일 전송 로직은 여기에 구현
    // 현재는 시뮬레이션만 수행
    console.log(`견적서 이메일 전송 시뮬레이션: ${quotation.quotationNumber} -> ${adminEmail}`);
    
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                success: true,
                emailId: `email_${Date.now()}`,
                recipient: adminEmail,
                subject: `[LRQA] 견적서 생성 완료 - ${quotation.companyName}`,
                message: '견적서가 성공적으로 생성되었습니다.'
            });
        }, 1000);
    });
}
