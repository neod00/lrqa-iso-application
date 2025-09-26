const Docxtemplater = require('docxtemplater');
const PizZip = require('pizzip');
const fs = require('fs');
const path = require('path');

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
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
            headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                success: false, 
                error: 'Method not allowed' 
            })
        };
    }

    try {
        const requestBody = JSON.parse(event.body);
        const { quotationData, adminEmail } = requestBody;

        console.log('견적서 생성 시작:', quotationData);

        // 견적서 데이터 추출
        const companyName = quotationData.companyName || '회사명 없음';
        const contactName = quotationData.contactName || '담당자 없음';
        const contactEmail = quotationData.contactEmail || '이메일 없음';
        const totalEmployees = quotationData.totalEmployees || 0;
        const siteCount = quotationData.siteCount || 1;
        const isoStandards = quotationData.isoStandards || [];
        const desiredAuditDate = quotationData.desiredAuditDate || '2025-12';
        
        // 디버깅: 전송된 데이터 확인
        console.log('전송된 견적서 데이터:', JSON.stringify(quotationData, null, 2));
        console.log('ISO 표준 배열:', isoStandards);
        console.log('has_iso14001 계산:', isoStandards.some(std => std.toLowerCase().includes('14001')));

        // ISO 표준 한글명 매핑
        const isoStandardNames = {
            'iso9001': 'ISO 9001 (품질경영시스템)',
            'iso14001': 'ISO 14001 (환경경영시스템)',
            'iso45001': 'ISO 45001 (직업안전보건경영시스템)'
        };

        const selectedStandards = isoStandards.map(std => isoStandardNames[std] || std).join(', ');

        // ADJ_v.2.2 기준 심사일수 계산
        let baseDays = 0;
        if (totalEmployees <= 10) baseDays = 1;
        else if (totalEmployees <= 50) baseDays = 2;
        else if (totalEmployees <= 100) baseDays = 3;
        else if (totalEmployees <= 500) baseDays = 4;
        else baseDays = 5;

        // 사업장 수에 따른 추가 일수
        const additionalDays = (siteCount - 1) * 0.5;
        const totalDays = Math.ceil(baseDays + additionalDays);

        // 심사비 계산 (일당 1,450,000원)
        const dailyRate = 1450000;
        const totalFee = totalDays * dailyRate;
        const additionalExpenses = Math.round(totalFee * 0.1); // 제경비 10%
        const grandTotal = totalFee + additionalExpenses;

        // 견적 상세 데이터 준비 (표준별 분석)
        const quotationDetails = [];
        const stage1Days = Math.ceil(totalDays * 0.3); // Stage1은 총 일수의 30%
        const stage2Days = totalDays - stage1Days; // Stage2는 나머지
        const surveillanceDays = Math.ceil(totalDays * 0.4); // Surveillance는 총 일수의 40%

        isoStandards.forEach(std => {
            const standardName = isoStandardNames[std] || std;
            const recertDays = Math.ceil(totalDays * 0.8); // 재인증은 총 일수의 80%
            quotationDetails.push({
                standard: std.toUpperCase(),
                standard_name: standardName,
                enp: totalEmployees, // Effective Number of Personnel
                complexity: 'MEDIUM',
                stage1_days: stage1Days,
                stage2_days: stage2Days,
                surveillance_days: surveillanceDays,
                recert_days: recertDays,
                total_days: totalDays,
                stage1_cost: stage1Days * dailyRate,
                stage2_cost: stage2Days * dailyRate,
                surveillance_cost: surveillanceDays * dailyRate,
                recert_cost: recertDays * dailyRate,
                total_cost: totalDays * dailyRate
            });
        });

        // 사업장 데이터 준비
        const sites = [{
            number: 1,
            name: '본사',
            address: quotationData.headOfficeAddress || '서울시 강남구 테헤란로 123',
            headcount: totalEmployees,
            standards: selectedStandards,
            activities: '제조업'
        }];

        // 직원 구성 데이터 준비
        const employeeBreakdown = {
            total: totalEmployees,
            permanent: Math.floor(totalEmployees * 0.88), // 88% 정규직
            temporary: Math.floor(totalEmployees * 0.06),  // 6% 비정규직
            contractors: Math.floor(totalEmployees * 0.06)  // 6% 협력업체
        };

        // 가정 사항 및 근거
        const assumptions = [
            'ADJ_v.2.2 기준에 따라 계산되었습니다.',
            `총 직원 수 ${totalEmployees}명 기준으로 심사일수가 산정되었습니다.`,
            '사업장 수에 따른 추가 일수가 적용되었습니다.',
            '일당 1,450,000원 기준으로 계산되었습니다.'
        ];

        const justification = [
            'ISO 인증심사 표준 절차에 따라 Stage1, Stage2 심사로 구성됩니다.',
            'Surveillance 심사는 연 1회 실시됩니다.',
            '제경비는 심사비의 10%로 산정됩니다.',
            '견적 유효기간은 30일입니다.'
        ];

        // 템플릿 데이터 준비 (template_variables.md 기준)
        const templateData = {
            // 회사 정보
            client_name: companyName,
            client_name_en: companyName.includes('(') ? companyName.split('(')[1].replace(')', '') : companyName,
            client_address: quotationData.headOfficeAddress || '서울시 강남구 테헤란로 123',
            contact_person: contactName,
            contact_email: contactEmail,
            contact_phone: quotationData.contactPhone || '02-1234-5678',
            
            // 견적 정보
            quotation_date: new Date().toLocaleDateString('ko-KR', {year: 'numeric', month: 'long', day: 'numeric'}),
            quotation_number: `LRQA-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`,
            valid_until: new Date(Date.now() + 30*24*60*60*1000).toLocaleDateString('ko-KR', {year: 'numeric', month: 'long', day: 'numeric'}),
            
            // 표준 정보
            standards_text: selectedStandards,
            has_iso9001: isoStandards.some(std => std.toLowerCase().includes('9001')),
            has_iso14001: isoStandards.some(std => std.toLowerCase().includes('14001')),
            has_iso45001: isoStandards.some(std => std.toLowerCase().includes('45001')),
            iso9001_name: 'ISO 9001 품질경영시스템',
            iso14001_name: 'ISO 14001 환경경영시스템',
            iso45001_name: 'ISO 45001 안전보건경영시스템',
            
            // 사업장 정보
            sites: sites,
            total_sites: siteCount,
            total_employees: totalEmployees,
            
            // 직원 구성 정보
            employee_breakdown: employeeBreakdown,
            
            // 견적 상세 정보
            quotation_details: quotationDetails,
            total_audit_days: totalDays,
            subtotal: Math.floor(grandTotal / 1.1), // VAT 제외
            vat_amount: Math.floor(grandTotal * 0.1), // VAT 10%
            total_cost: grandTotal,
            
            // 표준별 개별 일수 및 비용
            stage1_days: stage1Days,
            stage2_days: stage2Days,
            surveillance_days: surveillanceDays,
            stage1_cost: stage1Days * dailyRate,
            stage2_cost: stage2Days * dailyRate,
            surveillance_cost: surveillanceDays * dailyRate,
            
            // 통합심사 정보
            is_integrated: isoStandards.length > 1,
            integration_discount: isoStandards.length > 1 ? 10 : 0,
            
            // 원격심사 정보
            remote_audit_ratio: 30,
            remote_discount: 5,
            
            // 가정 및 근거
            assumptions: assumptions,
            justification: justification,
            
            // 기타
            created_at: new Date().toISOString(),
            prepared_by: 'LRQA Korea',
            prepared_title: '사업개발본부'
        };

        // 디버깅: has_iso 변수들 확인
        console.log('ISO 표준 체크 결과:');
        console.log('has_iso9001:', templateData.has_iso9001);
        console.log('has_iso14001:', templateData.has_iso14001);
        console.log('has_iso45001:', templateData.has_iso45001);
        
        console.log('템플릿 데이터:', JSON.stringify(templateData, null, 2));

        // 템플릿 파일 읽기
        const templatePath = path.join(__dirname, 'templates', 'LRQA_quotation.docx');
        console.log('템플릿 파일 경로:', templatePath);
        
        // 파일 존재 확인
        if (!fs.existsSync(templatePath)) {
            throw new Error(`템플릿 파일을 찾을 수 없습니다: ${templatePath}`);
        }

        const content = fs.readFileSync(templatePath, 'binary');
        console.log('템플릿 파일 크기:', content.length, 'bytes');
        const zip = new PizZip(content);
        
        // Docxtemplater 인스턴스 생성
        const doc = new Docxtemplater(zip, {
            paragraphLoop: true,
            linebreaks: true,
            errorLogging: true
        });

        console.log('템플릿 변수 치환 시작...');
        // 템플릿에 데이터 바인딩
        doc.render(templateData);
        console.log('템플릿 변수 치환 완료');

        // Word 문서를 Buffer로 생성
        console.log('Word 문서 생성 시작...');
        const buffer = doc.getZip().generate({
            type: 'nodebuffer',
            compression: 'DEFLATE'
        });

        console.log('Word 견적서 생성 완료, 크기:', buffer.length);

        return {
            statusCode: 200,
            headers: {
                ...headers,
                'Content-Disposition': `attachment; filename="LRQA_quotation_${quotationData.id || 'quotation'}.docx"`,
                'Content-Length': buffer.length.toString()
            },
            body: buffer.toString('base64'),
            isBase64Encoded: true
        };

    } catch (error) {
        console.error('Error generating quotation:', error);
        console.error('Error stack:', error.stack);
        
        // Docxtemplater 오류 상세 정보 추가
        if (error.properties && error.properties.errors) {
            console.error('Docxtemplater errors:', error.properties.errors);
        }
        
        return {
            statusCode: 500,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                success: false,
                error: 'Internal server error',
                message: '견적서 생성 중 오류가 발생했습니다.',
                details: error.message,
                stack: error.stack,
                docxErrors: error.properties && error.properties.errors ? error.properties.errors : null
            })
        };
    }
};