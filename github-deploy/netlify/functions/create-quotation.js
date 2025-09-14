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

// Word 문서 생성 함수
async function generateWordDocument(quotation) {
    const { exec } = require('child_process');
    const fs = require('fs');
    const path = require('path');
    const util = require('util');
    const execAsync = util.promisify(exec);
    
    try {
        // Python 스크립트를 위한 데이터 파일 생성
        const tempDir = '/tmp';
        const dataFile = path.join(tempDir, `quotation_data_${quotation.quotationNumber}.json`);
        const outputFile = path.join(tempDir, `quotation_${quotation.quotationNumber}.docx`);
        
        // 견적서 데이터를 Python 스크립트가 이해할 수 있는 형식으로 변환
        const pythonData = {
            quotation_number: quotation.quotationNumber,
            company_name: quotation.companyName,
            company_name_en: quotation.companyName, // 영문명이 없으면 동일하게
            contact_name: quotation.contactName,
            contact_email: quotation.contactEmail,
            contact_phone: "010-0000-0000", // 기본값
            standards: quotation.isoStandards,
            total_employees: quotation.totalEmployees,
            site_count: quotation.siteCount,
            total_cost: quotation.totalCost,
            issue_date: quotation.issueDate,
            valid_until: quotation.validUntil,
            address: "서울시 강남구", // 기본 주소
            sites: [{
                name: "본사",
                address: "서울시 강남구",
                standards: quotation.isoStandards,
                total_headcount: quotation.totalEmployees
            }]
        };
        
        // 데이터 파일 저장
        fs.writeFileSync(dataFile, JSON.stringify(pythonData, null, 2), 'utf8');
        
        // Python 스크립트 실행
        const pythonScript = path.join(__dirname, '..', 'adj_quote_engine', 'generate_quotation.py');
        const command = `python3 "${pythonScript}" "${dataFile}" "${outputFile}"`;
        
        console.log('Python 명령어 실행:', command);
        const { stdout, stderr } = await execAsync(command);
        
        if (stderr) {
            console.log('Python 실행 경고:', stderr);
        }
        
        console.log('Python 실행 결과:', stdout);
        
        // 생성된 파일 확인
        if (fs.existsSync(outputFile)) {
            console.log('Word 문서 생성 성공:', outputFile);
            return outputFile;
        } else {
            throw new Error('Word 문서 파일이 생성되지 않았습니다.');
        }
        
    } catch (error) {
        console.error('Word 문서 생성 오류:', error);
        // 실패 시 텍스트 파일로 대체
        return generateTextDocument(quotation);
    }
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
