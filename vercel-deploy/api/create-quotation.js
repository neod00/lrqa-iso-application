/**
 * 견적서 생성 API
 * docx-templates를 사용하여 LRQA_quotation.docx 템플릿으로 Word 문서 생성
 */

import Docxtemplater from 'docxtemplater';
import PizZip from 'pizzip';
import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Content-Type', 'application/json');

  // OPTIONS 요청 처리 (CORS preflight)
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // POST 요청만 허용
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    // 요청 데이터 파싱
    const body = req.body || {};
    
    if (!body || Object.keys(body).length === 0) {
      res.status(400).json({ error: 'Request body is required' });
      return;
    }

    // 견적서 데이터 생성
    const quotationData = createQuotationData(body);
    
    // Word 문서 생성
    const wordDocumentUrl = await generateWordDocument(quotationData, body.quotation_number || 'default');
    
    // 응답 데이터 구성
    const responseData = {
      success: true,
      message: '견적서가 성공적으로 생성되었습니다.',
      quotation: {
        quotation_number: quotationData.company_name + '_' + new Date().toISOString().slice(0, 19).replace(/:/g, '-'),
        company_name: quotationData.company_name,
        total_cost: quotationData.total_cost,
        total_audit_days: quotationData.total_audit_days,
        standards: quotationData.standards,
        breakdowns: quotationData.breakdowns,
        word_document_url: wordDocumentUrl,
        created_at: new Date().toISOString()
      }
    };
    
    res.status(200).json(responseData);
    
  } catch (error) {
    console.error('Error creating quotation:', error);
    res.status(500).json({
      success: false,
      error: '견적서 생성 중 오류가 발생했습니다.',
      message: error.message
    });
  }
}

function createQuotationData(data) {
  // 디버깅: 전송된 데이터 확인
  console.log('전송된 데이터:', JSON.stringify(data, null, 2));
  console.log('standards 배열:', data.standards);
  
  // 표준 타입 변환
  const standards = [];
  for (const std of data.standards || []) {
    const stdLower = std.toLowerCase();
    console.log(`표준 처리: "${std}" -> "${stdLower}"`);
    if (stdLower.includes('9001')) {
      standards.push('ISO 9001');
    } else if (stdLower.includes('14001')) {
      standards.push('ISO 14001');
    } else if (stdLower.includes('45001')) {
      standards.push('ISO 45001');
    } else {
      standards.push('ISO 9001'); // 기본값
    }
  }
  
  console.log('변환된 standards:', standards);
  console.log('has_iso14001 계산:', standards.includes('ISO 14001'));

  // 기본 견적 계산 (간단한 버전)
  const totalEmployees = parseInt(data.total_employees) || 30;
  const standardCount = standards.length;
  
  // ENP 계산 (간단한 버전)
  const enp = Math.max(totalEmployees, 1);
  
  // 심사일수 계산 (간단한 버전)
  const baseDays = Math.max(2, Math.ceil(enp / 25)); // 최소 2일, 25명당 1일 추가
  const stage1Days = Math.ceil(baseDays * 0.3); // Stage 1: 30%
  const stage2Days = baseDays; // Stage 2: 100%
  const surveillanceDays = Math.ceil(baseDays * 0.6); // Surveillance: 60%
  const totalAuditDays = (stage1Days + stage2Days + surveillanceDays) * standardCount;
  
  // 비용 계산 (기존 템플릿 기준으로 수정)
  const dayRate = 1400000; // 1일 140만원 (기존 템플릿 기준)
  const vatRate = 0.1; // 10% 부가세
  const subtotalCost = totalAuditDays * dayRate;
  const vatAmount = subtotalCost * vatRate;
  const totalCost = subtotalCost + vatAmount;

  // 견적 상세 정보
  const breakdowns = standards.map(standard => ({
    standard: standard,
    stage1_days: stage1Days,
    stage2_days: stage2Days,
    surveillance_days: surveillanceDays,
    total_days: stage1Days + stage2Days + surveillanceDays,
    total_cost: (stage1Days + stage2Days + surveillanceDays) * dayRate
  }));

  return {
    company_name: data.company_name || '알 수 없음',
    company_name_en: data.company_name_en || data.company_name || 'Unknown',
    contact_name: data.contact_name || '알 수 없음',
    contact_email: data.contact_email || 'unknown@example.com',
    contact_phone: data.contact_phone || '010-0000-0000',
    address: data.address || '서울시 강남구',
    standards: standards,
    total_employees: totalEmployees,
    total_audit_days: totalAuditDays,
    subtotal_cost: subtotalCost,
    vat_amount: vatAmount,
    total_cost: totalCost,
    breakdowns: breakdowns,
    assumptions: data.assumptions || [
      '심사 일정은 고객사와 협의하여 결정됩니다.',
      '심사 비용은 2024년 기준 요율을 적용합니다.',
      '추가 비용이 발생할 수 있는 사항은 사전에 고객사에 안내드립니다.'
    ],
    justification: data.justification || [
      'ENP(Equivalent Number of Personnel) 기준으로 심사 일수를 산정했습니다.',
      'ISO 표준 요구사항에 따라 Stage 1 및 Stage 2 심사를 진행합니다.',
      '통합심사 시 할인 혜택이 적용됩니다.'
    ],
    created_at: new Date().toISOString()
  };
}

async function generateWordDocument(quotationData, quotationNumber) {
  try {
    // 로컬 파일 시스템에서 템플릿 읽기
    console.log('로컬 파일 시스템에서 템플릿 읽기 시도...');

    const possiblePaths = [
      path.join(process.cwd(), 'public', 'templates', 'LRQA_quotation.docx'),
      path.join(process.cwd(), 'templates', 'LRQA_quotation.docx'),
      '/var/task/public/templates/LRQA_quotation.docx',
      '/var/task/templates/LRQA_quotation.docx',
      path.join(__dirname, '..', 'public', 'templates', 'LRQA_quotation.docx'),
      path.join(__dirname, '..', 'templates', 'LRQA_quotation.docx'),
      path.join(process.cwd(), '..', 'public', 'templates', 'LRQA_quotation.docx'),
      path.join(process.cwd(), '..', 'templates', 'LRQA_quotation.docx'),
      './public/templates/LRQA_quotation.docx',
      './templates/LRQA_quotation.docx',
      '../public/templates/LRQA_quotation.docx',
      '../templates/LRQA_quotation.docx'
    ];

    console.log('현재 작업 디렉토리:', process.cwd());
    console.log('__dirname:', __dirname);

    let template;
    let templateFound = false;
    
    for (const templatePath of possiblePaths) {
      try {
        console.log('경로 시도:', templatePath);
        if (fs.existsSync(templatePath)) {
          template = fs.readFileSync(templatePath);
          console.log('템플릿 파일 로드 성공: ' + templatePath);
          templateFound = true;
          break;
        } else {
          console.log('파일이 존재하지 않음:', templatePath);
        }
      } catch (err) {
        console.log('경로 시도 실패:', templatePath, err.message);
      }
    }

    if (!templateFound) {
      console.error('사용 가능한 템플릿 경로들:');
      possiblePaths.forEach((p, i) => {
        const exists = fs.existsSync(p);
        console.error(`${i+1}:`, p, 'exists:', exists);
      });
      throw new Error('Word 템플릿 파일을 찾을 수 없습니다.');
    }
    
    // 템플릿 데이터 준비 (LRQA_quotation.docx 템플릿에 맞게)
    const templateData = {
      // 기본 정보 (템플릿에서 사용하는 변수명으로 수정)
      client_name: quotationData.company_name,
      client_name_en: quotationData.company_name_en,
      contact_person: quotationData.contact_name,
      contact_email: quotationData.contact_email,
      contact_phone: quotationData.contact_phone,
      client_address: quotationData.address,
      
      // 견적 정보
      quotation_number: quotationNumber || `LRQA-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.abs(quotationData.company_name.split('').reduce((a, b) => { a = ((a << 5) - a) + b.charCodeAt(0); return a & a; }, 0)) % 10000}`,
      quotation_date: new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }),
      valid_until: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }),
      
      // 표준 정보
      standards: quotationData.standards,
      standards_text: quotationData.standards.join(', '),
      total_employees: quotationData.total_employees,
      
      // 개별 표준 확인 변수들
      has_iso9001: quotationData.standards.includes('ISO 9001'),
      has_iso14001: quotationData.standards.includes('ISO 14001'),
      has_iso45001: quotationData.standards.includes('ISO 45001'),
      
      // 디버깅: 표준 확인 변수들 로그
      debug_standards: quotationData.standards,
      debug_has_iso9001: quotationData.standards.includes('ISO 9001'),
      debug_has_iso14001: quotationData.standards.includes('ISO 14001'),
      debug_has_iso45001: quotationData.standards.includes('ISO 45001'),
      
      // 템플릿 디버깅을 위한 추가 변수들
      debug_total_audit_days: quotationData.total_audit_days,
      debug_total_cost: quotationData.total_cost,
      debug_total_cost_with_travel: quotationData.total_cost + 500000,
      iso9001_name: 'ISO 9001 품질경영시스템',
      iso14001_name: 'ISO 14001 환경경영시스템',
      iso45001_name: 'ISO 45001 안전보건경영시스템',
      
      // 심사 일수 정보
      total_audit_days: quotationData.total_audit_days,
      stage1_days: quotationData.breakdowns.reduce((sum, b) => sum + b.stage1_days, 0),
      stage2_days: quotationData.breakdowns.reduce((sum, b) => sum + b.stage2_days, 0),
      surveillance_days: quotationData.breakdowns.reduce((sum, b) => sum + b.surveillance_days, 0),
      
      // 비용 정보 (템플릿에서 사용하는 변수명으로 수정)
      day_rate: 1400000, // 1일 140만원 (기존 템플릿 기준)
      day_rate_text: '1,400,000',
      subtotal: quotationData.subtotal_cost,
      subtotal_text: quotationData.subtotal_cost.toLocaleString(),
      vat_amount: quotationData.vat_amount,
      vat_amount_text: quotationData.vat_amount.toLocaleString(),
      total_cost: quotationData.total_cost,
      total_cost_text: quotationData.total_cost.toLocaleString(),
      
      // 여행비 포함 총 비용
      travel_expense: 500000, // 50만원 여행비
      total_cost_with_travel: quotationData.total_cost + 500000,
      total_cost_with_travel_formatted: (quotationData.total_cost + 500000).toLocaleString(),
      
      // 개별 비용 변수들
      initial_audit_cost: quotationData.breakdowns.reduce((sum, b) => sum + (b.stage1_days + b.stage2_days) * 1400000, 0),
      initial_audit_vat: quotationData.breakdowns.reduce((sum, b) => sum + (b.stage1_days + b.stage2_days) * 1400000, 0) * 0.1,
      surveillance_cost: quotationData.breakdowns.reduce((sum, b) => sum + b.surveillance_days * 1400000, 0),
      stage1_cost: quotationData.breakdowns.reduce((sum, b) => sum + b.stage1_days * 1400000, 0),
      stage2_cost: quotationData.breakdowns.reduce((sum, b) => sum + b.stage2_days * 1400000, 0),
      
      // 개별 표준별 변수들 - Surveillance
      iso9001_surveillance_days: quotationData.standards.includes('ISO 9001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.surveillance_days || 0 : 0,
      iso14001_surveillance_days: quotationData.standards.includes('ISO 14001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.surveillance_days || 0 : 0,
      iso45001_surveillance_days: quotationData.standards.includes('ISO 45001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.surveillance_days || 0 : 0,
      iso9001_surveillance_cost: quotationData.standards.includes('ISO 9001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.surveillance_days || 0) * 1400000 : 0,
      iso14001_surveillance_cost: quotationData.standards.includes('ISO 14001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.surveillance_days || 0) * 1400000 : 0,
      iso45001_surveillance_cost: quotationData.standards.includes('ISO 45001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.surveillance_days || 0) * 1400000 : 0,
      
      // 개별 표준별 변수들 - Stage1
      iso9001_stage1_days: quotationData.standards.includes('ISO 9001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage1_days || 0 : 0,
      iso14001_stage1_days: quotationData.standards.includes('ISO 14001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage1_days || 0 : 0,
      iso45001_stage1_days: quotationData.standards.includes('ISO 45001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage1_days || 0 : 0,
      iso9001_stage1_cost: quotationData.standards.includes('ISO 9001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage1_days || 0) * 1400000 : 0,
      iso14001_stage1_cost: quotationData.standards.includes('ISO 14001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage1_days || 0) * 1400000 : 0,
      iso45001_stage1_cost: quotationData.standards.includes('ISO 45001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage1_days || 0) * 1400000 : 0,
      
      // 개별 표준별 변수들 - Stage2
      iso9001_stage2_days: quotationData.standards.includes('ISO 9001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage2_days || 0 : 0,
      iso14001_stage2_days: quotationData.standards.includes('ISO 14001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage2_days || 0 : 0,
      iso45001_stage2_days: quotationData.standards.includes('ISO 45001') ? quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage2_days || 0 : 0,
      iso9001_stage2_cost: quotationData.standards.includes('ISO 9001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage2_days || 0) * 1400000 : 0,
      iso14001_stage2_cost: quotationData.standards.includes('ISO 14001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage2_days || 0) * 1400000 : 0,
      iso45001_stage2_cost: quotationData.standards.includes('ISO 45001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage2_days || 0) * 1400000 : 0,
      
      // 개별 표준별 Stage1+Stage2 합산값 변수들
      iso9001_stage1_2_days: quotationData.standards.includes('ISO 9001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage1_days || 0) + (quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage2_days || 0) : 0,
      iso14001_stage1_2_days: quotationData.standards.includes('ISO 14001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage1_days || 0) + (quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage2_days || 0) : 0,
      iso45001_stage1_2_days: quotationData.standards.includes('ISO 45001') ? (quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage1_days || 0) + (quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage2_days || 0) : 0,
      iso9001_stage1_2_cost: quotationData.standards.includes('ISO 9001') ? ((quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage1_days || 0) + (quotationData.breakdowns.find(b => b.standard === 'ISO 9001')?.stage2_days || 0)) * 1400000 : 0,
      iso14001_stage1_2_cost: quotationData.standards.includes('ISO 14001') ? ((quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage1_days || 0) + (quotationData.breakdowns.find(b => b.standard === 'ISO 14001')?.stage2_days || 0)) * 1400000 : 0,
      iso45001_stage1_2_cost: quotationData.standards.includes('ISO 45001') ? ((quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage1_days || 0) + (quotationData.breakdowns.find(b => b.standard === 'ISO 45001')?.stage2_days || 0)) * 1400000 : 0,
      
      // 견적 상세
      breakdowns: quotationData.breakdowns,
      quotation_details: quotationData.breakdowns.map(b => ({
        standard: b.standard,
        standard_name: b.standard === 'ISO 9001' ? 'ISO 9001 품질경영시스템' : 
                      b.standard === 'ISO 14001' ? 'ISO 14001 환경경영시스템' : 
                      b.standard === 'ISO 45001' ? 'ISO 45001 안전보건경영시스템' : b.standard,
        enp: quotationData.total_employees,
        complexity: '표준',
        stage1_days: b.stage1_days,
        stage2_days: b.stage2_days,
        surveillance_days: b.surveillance_days,
        recert_days: 0,
        total_days: b.total_days,
        stage1_cost: b.stage1_days * 1400000,
        stage2_cost: b.stage2_days * 1400000,
        surveillance_cost: b.surveillance_days * 1400000,
        recert_cost: 0,
        total_cost: b.total_cost
      })),
      
      // 사업장 정보 (템플릿에서 필요한 변수들)
      total_sites: 1, // 기본값
      sites: [{
        address: quotationData.address,
        activity: '제조업',
        employees: quotationData.total_employees
      }],
      
      // 직원 정보
      employee_breakdown: {
        regular: Math.floor(quotationData.total_employees * 0.8),
        temporary: Math.floor(quotationData.total_employees * 0.2),
        contractor: 0
      },
      
      // 통합심사 정보
      is_integrated: quotationData.standards.length > 1,
      integration_discount: quotationData.standards.length > 1 ? 10 : 0,
      
      // 원격심사 정보
      remote_audit_ratio: 0,
      remote_discount: 0,
      
      // 제경비 (최초심사 비용의 10%)
      travel_expense: Math.floor(quotationData.breakdowns.reduce((sum, b) => sum + (b.stage1_days + b.stage2_days) * 1400000, 0) * 0.1),
      
      // 제경비 포함 총 비용 (최초심사 + 제경비, VAT 별도)
      total_cost_with_travel: Math.floor(quotationData.breakdowns.reduce((sum, b) => sum + (b.stage1_days + b.stage2_days) * 1400000, 0) + quotationData.breakdowns.reduce((sum, b) => sum + (b.stage1_days + b.stage2_days) * 1400000, 0) * 0.1),
      
      // 가정 및 근거
      assumptions: quotationData.assumptions || [],
      justification: quotationData.justification || [],
      
      // 회사 정보
      lrqa_company: 'LRQA Korea',
      lrqa_address: '서울시 강남구 테헤란로 123',
      lrqa_phone: '02-1234-5678',
      lrqa_email: 'info@lrqa.co.kr',
      
      // 작성자 정보
      prepared_by: 'LRQA Korea',
      prepared_title: '사업개발본부',
      
      // 기타 변수들
      travel_expense: 0, // 여행비
      certification_fee: 0, // 인증서 발급비
      report_fee: 0, // 보고서 작성비
      other_fees: 0, // 기타 수수료
      
      // 기타
      created_at: new Date().toISOString(),
      year: new Date().getFullYear()
    };
    
    
    // Word 문서 생성 (docxtemplater 사용)
    const zip = new PizZip(template);
    const doc = new Docxtemplater(zip, {
      paragraphLoop: true,
      linebreaks: true,
      errorLogging: true
    });
    
    // 템플릿 데이터 설정
    doc.setData(templateData);
    
    // 템플릿 렌더링
    try {
      doc.render();
    } catch (error) {
      console.error('템플릿 렌더링 오류:', error);
      throw new Error('템플릿 렌더링 중 오류가 발생했습니다: ' + error.message);
    }
    
    // Word 문서를 Buffer로 생성
    const report = doc.getZip().generate({
      type: 'nodebuffer',
      compression: 'DEFLATE'
    });
    
    // 임시 파일로 저장 (실제 환경에서는 클라우드 스토리지 사용)
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const outputFilename = `LRQA_Quotation_${quotationNumber}_${timestamp}.docx`;
    const outputPath = path.join('/tmp', outputFilename);
    
    // /tmp 디렉토리가 없으면 생성
    if (!fs.existsSync('/tmp')) {
      fs.mkdirSync('/tmp', { recursive: true });
    }
    
    fs.writeFileSync(outputPath, report);
    
    console.log(`Word 문서 생성 완료: ${outputPath}`);
    console.log(`파일 크기: ${fs.statSync(outputPath).size} bytes`);
    
    return `/tmp/${outputFilename}`;
    
  } catch (error) {
    console.error('Word 문서 생성 오류:', error);
    return null;
  }
}
