const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

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

    // POST 요청만 처리
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ success: false, message: 'Method not allowed' })
        };
    }

    try {
        // 요청 데이터 파싱
        const requestData = JSON.parse(event.body);
        const { timestamp, applicationData } = requestData;

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

        // 임시 파일 경로 설정
        const tempDir = '/tmp';
        const inputFile = path.join(tempDir, `input_${timestamp}.json`);
        const outputFile = path.join(tempDir, `quotation_${timestamp}.docx`);

        // 견적서 생성을 위한 데이터 변환
        const quotationData = convertApplicationToQuotationData(applicationData);

        // JSON 파일 생성
        fs.writeFileSync(inputFile, JSON.stringify(quotationData, null, 2), 'utf8');

        // Python 스크립트 실행 경로
        const pythonScriptPath = path.join(__dirname, 'adj_quote_engine', 'generate_quotation.py');
        const adjQuoteEnginePath = path.join(__dirname, 'adj_quote_engine');

        // Python 스크립트 실행
        const command = `cd ${adjQuoteEnginePath} && python generate_quotation.py "${inputFile}" "${outputFile}"`;

        return new Promise((resolve) => {
            exec(command, { timeout: 30000 }, (error, stdout, stderr) => {
                if (error) {
                    console.error('Python script error:', error);
                    console.error('stderr:', stderr);
                    resolve({
                        statusCode: 500,
                        headers,
                        body: JSON.stringify({ 
                            success: false, 
                            message: '견적서 생성 중 오류가 발생했습니다.',
                            error: error.message 
                        })
                    });
                    return;
                }

                // 생성된 파일 확인
                if (!fs.existsSync(outputFile)) {
                    resolve({
                        statusCode: 500,
                        headers,
                        body: JSON.stringify({ 
                            success: false, 
                            message: '견적서 파일이 생성되지 않았습니다.' 
                        })
                    });
                    return;
                }

                // 파일 읽기
                const fileBuffer = fs.readFileSync(outputFile);
                const base64File = fileBuffer.toString('base64');

                // 임시 파일 정리
                try {
                    fs.unlinkSync(inputFile);
                    fs.unlinkSync(outputFile);
                } catch (cleanupError) {
                    console.warn('Cleanup error:', cleanupError);
                }

                resolve({
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
                });
            });
        });

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ 
                success: false, 
                message: '서버 오류가 발생했습니다.',
                error: error.message 
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
            standards.push('ISO9001');
        }
        if (isoStandards.includes('ISO 14001') || isoStandards.includes('ISO14001')) {
            standards.push('ISO14001');
        }
        if (isoStandards.includes('ISO 45001') || isoStandards.includes('ISO45001')) {
            standards.push('ISO45001');
        }
    }

    // 기본값 설정
    if (standards.length === 0) {
        standards.push('ISO9001');
    }

    // 사업장 정보 생성
    const sites = [{
        name: '본사',
        address: applicationData['본사주소'] || '서울시 강남구',
        standards: standards,
        total_headcount: parseInt(applicationData['총직원수']) || 30,
        part_time_count: parseInt(applicationData['비정규직수']) || 0,
        contractor_count: parseInt(applicationData['협력업체직원수']) || 0,
        shift_workers: 0,
        seasonal_factor: 1.0,
        repetitive_process: applicationData['반복작업직원그룹'] === '예',
        remote_audit_ratio: applicationData['원격심사'] === '예' ? 0.5 : 0.0
    }];

    // 통합심사 정보
    const integration = {
        is_integrated: applicationData['다중표준시스템'] === '예',
        integration_level: applicationData['다중표준시스템'] === '예' ? 0.8 : 0.0,
        shared_management_system: applicationData['다중표준시스템'] === '예',
        common_processes: applicationData['다중표준시스템'] === '예',
        same_audit_team: applicationData['다중표준시스템'] === '예'
    };

    // 옵션 설정
    const options = {
        stage1: true,
        stage2: true,
        surveillance: true,
        recert: false,
        remote_audit_ratio: applicationData['원격심사'] === '예' ? 0.5 : 0.0,
        day_rate: 1400000.0, // 1 manday 단가
        vat_rate: 0.1 // VAT 10%
    };

    return {
        client_name: applicationData['법인명(국문)'] || '알 수 없음',
        client_name_en: applicationData['법인명(영문)'] || applicationData['법인명(국문)'] || 'Unknown',
        contact_name: applicationData['담당자명'] || '알 수 없음',
        contact_email: applicationData['담당자이메일'] || 'unknown@example.com',
        contact_phone: applicationData['담당자전화'] || '010-0000-0000',
        standards: standards,
        sites: sites,
        integration: integration,
        options: options,
        total_employees: parseInt(applicationData['총직원수']) || 30
    };
}
