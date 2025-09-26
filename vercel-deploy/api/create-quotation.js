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
    const quotationData = await createQuotationData(body);
    
    // Word 문서 생성
    const wordDocumentBuffer = await generateWordDocument(quotationData, body.quotation_number || 'default');
    
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
        word_document_buffer: wordDocumentBuffer,
        created_at: new Date().toISOString()
      }
    };
    
    // Word 문서를 직접 반환
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    
    // 파일명을 URL 인코딩하여 한글 문제 해결
    const fileName = `quotation_${quotationData.company_name}_${new Date().toISOString().slice(0, 10)}.docx`;
    const encodedFileName = encodeURIComponent(fileName);
    res.setHeader('Content-Disposition', `attachment; filename*=UTF-8''${encodedFileName}`);
    
    res.status(200).send(wordDocumentBuffer);
    
  } catch (error) {
    console.error('Error creating quotation:', error);
    res.status(500).json({
      success: false,
      error: '견적서 생성 중 오류가 발생했습니다.',
      message: error.message
    });
  }
}

async function callCoreBrainAPI(applicationData) {
  try {
    const coreBrainUrl = 'http://localhost:5001/calculate-audit-days';
    
    // applicationData를 핵심두뇌 API 형식으로 변환
    const requestData = {
      client_name: applicationData['법인명(국문)'] || 'Unknown',
      sites: [{
        name: applicationData['법인명(국문)'] || 'Unknown',
        address: applicationData['본사주소'] || '서울시 강남구',
        standards: [applicationData['ISO표준'] || 'ISO9001'],
        total_headcount: parseInt(applicationData['총직원수']) || 30,
        business_sector: 'MANUFACTURING',
        management_system_maturity: 'MEDIUM'
      }],
      standards: [applicationData['ISO표준'] || 'ISO9001'],
      options: {
        stage1: true,
        stage2: true,
        surveillance: true,
        recert: true
      }
    };
    
    console.log('핵심두뇌 API 호출:', coreBrainUrl);
    console.log('요청 데이터:', JSON.stringify(requestData, null, 2));
    
    const response = await fetch(coreBrainUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('핵심두뇌 API 응답:', result);
      return result;
    } else {
      console.log('핵심두뇌 API 호출 실패:', response.status, response.statusText);
      return null;
    }
  } catch (error) {
    console.log('핵심두뇌 API 호출 오류:', error.message);
    return null;
  }
}

async function createQuotationData(data) {
  // 디버깅: 전송된 데이터 확인
  console.log('전송된 데이터:', JSON.stringify(data, null, 2));
  console.log('standards 배열:', data.standards);
  console.log('applicationData ISO표준:', data.applicationData?.['ISO표준']);
  
  // 핵심두뇌 API 호출 시도
  let coreBrainResult = null;
  if (data.applicationData) {
    console.log('핵심두뇌 API 호출 시도...');
    coreBrainResult = await callCoreBrainAPI(data.applicationData);
  }
  
  // 표준 타입 변환 - applicationData에서 ISO표준 필드 확인
  const standards = [];
  let standardsToProcess = data.standards || [];
  
  // applicationData에서 ISO표준 필드가 있는 경우 사용
  if (data.applicationData && data.applicationData['ISO표준']) {
    const isoStandard = data.applicationData['ISO표준'];
    if (isoStandard && isoStandard.trim()) {
      standardsToProcess = [isoStandard];
    }
  }
  
  for (const std of standardsToProcess) {
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

  // 핵심두뇌 API 결과가 있으면 사용, 없으면 기본 계산
  let totalAuditDays, subtotalCost, vatAmount, totalCost, breakdowns;
  
  if (coreBrainResult && coreBrainResult.success) {
    console.log('핵심두뇌 API 결과 사용');
    totalAuditDays = coreBrainResult.total_audit_days;
    breakdowns = coreBrainResult.breakdowns || [];
    
    // 비용 계산
    const dayRate = 1400000; // 1일 140만원
    const vatRate = 0.1; // 10% 부가세
    subtotalCost = totalAuditDays * dayRate;
    vatAmount = subtotalCost * vatRate;
    totalCost = subtotalCost + vatAmount;
  } else {
    console.log('기본 견적 계산 사용');
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
    totalAuditDays = (stage1Days + stage2Days + surveillanceDays) * standardCount;
    
    // 비용 계산 (기존 템플릿 기준으로 수정)
    const dayRate = 1400000; // 1일 140만원 (기존 템플릿 기준)
    const vatRate = 0.1; // 10% 부가세
    subtotalCost = totalAuditDays * dayRate;
    vatAmount = subtotalCost * vatRate;
    totalCost = subtotalCost + vatAmount;

    // 견적 상세 정보
    breakdowns = standards.map(standard => ({
      standard: standard,
      stage1_days: stage1Days,
      stage2_days: stage2Days,
      surveillance_days: surveillanceDays,
      total_days: stage1Days + stage2Days + surveillanceDays,
      total_cost: (stage1Days + stage2Days + surveillanceDays) * dayRate
    }));
  }

  // applicationData에서 올바른 필드 매핑
  const applicationData = data.applicationData || {};
  
  console.log('=== applicationData 확인 ===');
  console.log('applicationData 존재:', !!applicationData);
  console.log('applicationData 키 개수:', Object.keys(applicationData).length);
  console.log('법인명(국문):', applicationData['법인명(국문)']);
  console.log('담당자명:', applicationData['담당자명']);
  console.log('총직원수:', applicationData['총직원수']);
  console.log('standards:', standards);
  console.log('has_iso14001:', standards.includes('ISO 14001'));
  
  const quotationData = {
    company_name: applicationData['법인명(국문)'] || data.company_name || '알 수 없음',
    company_name_en: applicationData['법인명(영문)'] || data.company_name_en || 'Unknown',
    contact_name: applicationData['담당자명'] || data.contact_name || '알 수 없음',
    contact_email: applicationData['담당자이메일'] || data.contact_email || 'unknown@example.com',
    contact_phone: applicationData['담당자전화'] || data.contact_phone || '010-0000-0000',
    address: applicationData['본사주소'] || data.address || '서울시 강남구',
    standards: standards,
    total_employees: parseInt(applicationData['총직원수']) || totalEmployees,
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
    has_iso9001: standards.includes('ISO 9001'),
    has_iso14001: standards.includes('ISO 14001'),
    has_iso45001: standards.includes('ISO 45001'),
    created_at: new Date().toISOString()
  };
  
  console.log('=== quotationData 객체 확인 ===');
  console.log('quotationData.company_name:', quotationData.company_name);
  console.log('quotationData.standards:', quotationData.standards);
  console.log('quotationData.has_iso14001:', quotationData.has_iso14001);
  console.log('quotationData.total_employees:', quotationData.total_employees);
  
  return quotationData;
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
          template = fs.readFileSync(templatePath, { encoding: null }); // 바이너리 모드로 읽기
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
    console.log('=== 템플릿 데이터 준비 시작 ===');
    console.log('quotationData.company_name:', quotationData.company_name);
    console.log('quotationData.standards:', quotationData.standards);
    console.log('quotationData.has_iso14001:', quotationData.has_iso14001);
    
    const templateData = {
      // 기본 정보 (템플릿에서 사용하는 변수명으로 수정)
      client_name: quotationData.company_name || '알 수 없음',
      client_name_en: quotationData.company_name_en || 'Unknown',
      contact_person: quotationData.contact_name || '알 수 없음',
      contact_email: quotationData.contact_email || 'unknown@example.com',
      contact_phone: quotationData.contact_phone || '010-0000-0000',
      client_address: quotationData.address || '서울시 강남구',
      
      // 견적 정보
      quotation_number: quotationNumber || `LRQA-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.abs((quotationData.company_name || 'Unknown').split('').reduce((a, b) => { a = ((a << 5) - a) + b.charCodeAt(0); return a & a; }, 0)) % 10000}`,
      quotation_date: new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }),
      valid_until: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }),
      
      // 표준 정보
      standards: quotationData.standards || [],
      standards_text: (quotationData.standards || []).join(', ') || 'ISO 9001',
      total_employees: quotationData.total_employees || 0,
      
      // 개별 표준 확인 변수들
      has_iso9001: (quotationData.standards || []).includes('ISO 9001'),
      has_iso14001: (quotationData.standards || []).includes('ISO 14001'),
      has_iso45001: (quotationData.standards || []).includes('ISO 45001'),
      
      // 디버깅: 표준 확인 변수들 로그
      debug_standards: quotationData.standards || [],
      debug_has_iso9001: (quotationData.standards || []).includes('ISO 9001'),
      debug_has_iso14001: (quotationData.standards || []).includes('ISO 14001'),
      debug_has_iso45001: (quotationData.standards || []).includes('ISO 45001'),
      
      // 템플릿 디버깅을 위한 추가 변수들
      debug_total_audit_days: quotationData.total_audit_days,
      debug_total_cost: quotationData.total_cost,
      debug_total_cost_with_travel: quotationData.total_cost + 500000,
      iso9001_name: 'ISO 9001 품질경영시스템',
      iso14001_name: 'ISO 14001 환경경영시스템',
      iso45001_name: 'ISO 45001 안전보건경영시스템',
      
      // 심사 일수 정보
      total_audit_days: quotationData.total_audit_days || 0,
      stage1_days: (quotationData.breakdowns || []).reduce((sum, b) => sum + (b.stage1_days || 0), 0),
      stage2_days: (quotationData.breakdowns || []).reduce((sum, b) => sum + (b.stage2_days || 0), 0),
      surveillance_days: (quotationData.breakdowns || []).reduce((sum, b) => sum + (b.surveillance_days || 0), 0),
      
      // 비용 정보 (템플릿에서 사용하는 변수명으로 수정)
      day_rate: 1400000, // 1일 140만원 (기존 템플릿 기준)
      day_rate_text: '1,400,000',
      subtotal: quotationData.subtotal_cost || 0,
      subtotal_text: (quotationData.subtotal_cost || 0).toLocaleString(),
      vat_amount: quotationData.vat_amount || 0,
      vat_amount_text: (quotationData.vat_amount || 0).toLocaleString(),
      total_cost: quotationData.total_cost || 0,
      total_cost_text: (quotationData.total_cost || 0).toLocaleString(),
      
      // 여행비 포함 총 비용
      travel_expense: 500000, // 50만원 여행비
      total_cost_with_travel: (quotationData.total_cost || 0) + 500000,
      total_cost_with_travel_formatted: ((quotationData.total_cost || 0) + 500000).toLocaleString(),
      
      // 개별 비용 변수들
      initial_audit_cost: (quotationData.breakdowns || []).reduce((sum, b) => sum + ((b.stage1_days || 0) + (b.stage2_days || 0)) * 1400000, 0),
      initial_audit_vat: (quotationData.breakdowns || []).reduce((sum, b) => sum + ((b.stage1_days || 0) + (b.stage2_days || 0)) * 1400000, 0) * 0.1,
      surveillance_cost: (quotationData.breakdowns || []).reduce((sum, b) => sum + (b.surveillance_days || 0) * 1400000, 0),
      stage1_cost: (quotationData.breakdowns || []).reduce((sum, b) => sum + (b.stage1_days || 0) * 1400000, 0),
      stage2_cost: (quotationData.breakdowns || []).reduce((sum, b) => sum + (b.stage2_days || 0) * 1400000, 0),
      
      // 개별 표준별 변수들 - Surveillance
      iso9001_surveillance_days: (quotationData.standards || []).includes('ISO 9001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.surveillance_days || 0 : 0,
      iso14001_surveillance_days: (quotationData.standards || []).includes('ISO 14001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.surveillance_days || 0 : 0,
      iso45001_surveillance_days: (quotationData.standards || []).includes('ISO 45001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.surveillance_days || 0 : 0,
      iso9001_surveillance_cost: (quotationData.standards || []).includes('ISO 9001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.surveillance_days || 0) * 1400000 : 0,
      iso14001_surveillance_cost: (quotationData.standards || []).includes('ISO 14001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.surveillance_days || 0) * 1400000 : 0,
      iso45001_surveillance_cost: (quotationData.standards || []).includes('ISO 45001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.surveillance_days || 0) * 1400000 : 0,
      
      // 개별 표준별 변수들 - Stage1
      iso9001_stage1_days: (quotationData.standards || []).includes('ISO 9001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage1_days || 0 : 0,
      iso14001_stage1_days: (quotationData.standards || []).includes('ISO 14001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage1_days || 0 : 0,
      iso45001_stage1_days: (quotationData.standards || []).includes('ISO 45001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage1_days || 0 : 0,
      iso9001_stage1_cost: (quotationData.standards || []).includes('ISO 9001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage1_days || 0) * 1400000 : 0,
      iso14001_stage1_cost: (quotationData.standards || []).includes('ISO 14001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage1_days || 0) * 1400000 : 0,
      iso45001_stage1_cost: (quotationData.standards || []).includes('ISO 45001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage1_days || 0) * 1400000 : 0,
      
      // 개별 표준별 변수들 - Stage2
      iso9001_stage2_days: (quotationData.standards || []).includes('ISO 9001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage2_days || 0 : 0,
      iso14001_stage2_days: (quotationData.standards || []).includes('ISO 14001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage2_days || 0 : 0,
      iso45001_stage2_days: (quotationData.standards || []).includes('ISO 45001') ? (quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage2_days || 0 : 0,
      iso9001_stage2_cost: (quotationData.standards || []).includes('ISO 9001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage2_days || 0) * 1400000 : 0,
      iso14001_stage2_cost: (quotationData.standards || []).includes('ISO 14001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage2_days || 0) * 1400000 : 0,
      iso45001_stage2_cost: (quotationData.standards || []).includes('ISO 45001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage2_days || 0) * 1400000 : 0,
      
      // 개별 표준별 Stage1+Stage2 합산값 변수들
      iso9001_stage1_2_days: (quotationData.standards || []).includes('ISO 9001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage2_days || 0) : 0,
      iso14001_stage1_2_days: (quotationData.standards || []).includes('ISO 14001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage2_days || 0) : 0,
      iso45001_stage1_2_days: (quotationData.standards || []).includes('ISO 45001') ? ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage2_days || 0) : 0,
      iso9001_stage1_2_cost: (quotationData.standards || []).includes('ISO 9001') ? (((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage2_days || 0)) * 1400000 : 0,
      iso14001_stage1_2_cost: (quotationData.standards || []).includes('ISO 14001') ? (((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage2_days || 0)) * 1400000 : 0,
      iso45001_stage1_2_cost: (quotationData.standards || []).includes('ISO 45001') ? (((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage2_days || 0)) * 1400000 : 0,
      
      // 개별 표준별 Stage1+Stage2 비용 formatted 변수들
      iso9001_stage1_2_cost_formatted: (quotationData.standards || []).includes('ISO 9001') ? ((((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 9001')?.stage2_days || 0)) * 1400000).toLocaleString() : '0',
      iso14001_stage1_2_cost_formatted: (quotationData.standards || []).includes('ISO 14001') ? ((((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 14001')?.stage2_days || 0)) * 1400000).toLocaleString() : '0',
      iso45001_stage1_2_cost_formatted: (quotationData.standards || []).includes('ISO 45001') ? ((((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage1_days || 0) + ((quotationData.breakdowns || []).find(b => b.standard === 'ISO 45001')?.stage2_days || 0)) * 1400000).toLocaleString() : '0',
      
      // 견적 상세
      breakdowns: quotationData.breakdowns || [],
      quotation_details: (quotationData.breakdowns || []).map(b => ({
        standard: b.standard || 'ISO 9001',
        standard_name: b.standard === 'ISO 9001' ? 'ISO 9001 품질경영시스템' : 
                      b.standard === 'ISO 14001' ? 'ISO 14001 환경경영시스템' : 
                      b.standard === 'ISO 45001' ? 'ISO 45001 안전보건경영시스템' : b.standard || 'ISO 9001',
        enp: quotationData.total_employees || 0,
        complexity: '표준',
        stage1_days: b.stage1_days || 0,
        stage2_days: b.stage2_days || 0,
        surveillance_days: b.surveillance_days || 0,
        recert_days: 0,
        total_days: b.total_days || 0,
        stage1_cost: (b.stage1_days || 0) * 1400000,
        stage2_cost: (b.stage2_days || 0) * 1400000,
        surveillance_cost: (b.surveillance_days || 0) * 1400000,
        recert_cost: 0,
        total_cost: b.total_cost || 0
      })),
      
      // 사업장 정보 (템플릿에서 필요한 변수들)
      total_sites: 1, // 기본값
      total_employees: quotationData.total_employees || 0,
      sites: [{
        address: quotationData.address || '서울시 강남구',
        activity: '제조업',
        employees: quotationData.total_employees || 0
      }],
      
      // 직원 정보
      employee_breakdown: {
        regular: Math.floor((quotationData.total_employees || 0) * 0.8),
        temporary: Math.floor((quotationData.total_employees || 0) * 0.2),
        contractor: 0
      },
      
      // 통합심사 정보
      is_integrated: (quotationData.standards || []).length > 1,
      integration_discount: (quotationData.standards || []).length > 1 ? 10 : 0,
      
      // 원격심사 정보
      remote_audit_ratio: 0,
      remote_discount: 0,
      
      // 제경비 (최초심사 비용의 10%)
      travel_expense: Math.floor((quotationData.breakdowns || []).reduce((sum, b) => sum + ((b.stage1_days || 0) + (b.stage2_days || 0)) * 1400000, 0) * 0.1),
      travel_expense_formatted: Math.floor((quotationData.breakdowns || []).reduce((sum, b) => sum + ((b.stage1_days || 0) + (b.stage2_days || 0)) * 1400000, 0) * 0.1).toLocaleString(),
      
      // 제경비 포함 총 비용 (최초심사 + 제경비, VAT 별도)
      total_cost_with_travel: Math.floor((quotationData.breakdowns || []).reduce((sum, b) => sum + ((b.stage1_days || 0) + (b.stage2_days || 0)) * 1400000, 0) + (quotationData.breakdowns || []).reduce((sum, b) => sum + ((b.stage1_days || 0) + (b.stage2_days || 0)) * 1400000, 0) * 0.1),
      
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
      certification_fee: 0, // 인증서 발급비
      report_fee: 0, // 보고서 작성비
      other_fees: 0, // 기타 수수료
      
      // 기타
      created_at: new Date().toISOString(),
      year: new Date().getFullYear()
    };
    
    
    // Word 문서 생성 (docxtemplater 올바른 사용)
    console.log('템플릿 파일 크기:', template.length);
    console.log('템플릿 데이터 키 개수:', Object.keys(templateData).length);
    console.log('has_iso14001 값:', templateData.has_iso14001);
    console.log('standards_text 값:', templateData.standards_text);
    
    // 디버깅: 주요 변수들 확인
    console.log('=== 템플릿 변수 디버깅 ===');
    console.log('total_audit_days:', templateData.total_audit_days);
    console.log('total_cost_with_travel_formatted:', templateData.total_cost_with_travel_formatted);
    console.log('iso14001_surveillance_days:', templateData.iso14001_surveillance_days);
    console.log('iso14001_stage1_2_days:', templateData.iso14001_stage1_2_days);
    console.log('iso14001_stage1_2_cost_formatted:', templateData.iso14001_stage1_2_cost_formatted);
    console.log('travel_expense_formatted:', templateData.travel_expense_formatted);
    
    try {
      // docxtemplater 사용
      const zip = new PizZip(template);
      const doc = new Docxtemplater(zip, {
        paragraphLoop: true,
        linebreaks: true,
        errorLogging: true
      });
      
      // 구분자 설정 (별도로 설정)
      doc.setOptions({
        delimiters: {
          start: '{{',
          end: '}}'
        }
      });
      
      console.log('=== docxtemplater 설정 확인 ===');
      console.log('delimiters:', doc.getDelimiters());
      console.log('paragraphLoop:', doc.getOptions().paragraphLoop);
      console.log('linebreaks:', doc.getOptions().linebreaks);
      
      // 템플릿 데이터 설정 (안정적인 방식)
      console.log('=== 템플릿 데이터 설정 ===');
      console.log('templateData 키 개수:', Object.keys(templateData).length);
      console.log('templateData.has_iso14001:', templateData.has_iso14001);
      console.log('templateData.client_name:', templateData.client_name);
      
      // 주요 변수들 상세 로그
      console.log('=== 주요 템플릿 변수 상세 확인 ===');
      console.log('client_name:', templateData.client_name);
      console.log('client_address:', templateData.client_address);
      console.log('standards_text:', templateData.standards_text);
      console.log('quotation_date:', templateData.quotation_date);
      console.log('quotation_number:', templateData.quotation_number);
      console.log('total_sites:', templateData.total_sites);
      console.log('total_employees:', templateData.total_employees);
      console.log('total_audit_days:', templateData.total_audit_days);
      console.log('total_cost_with_travel_formatted:', templateData.total_cost_with_travel_formatted);
      console.log('iso14001_surveillance_days:', templateData.iso14001_surveillance_days);
      console.log('travel_expense_formatted:', templateData.travel_expense_formatted);
      
      // 템플릿에서 사용하는 모든 변수명 확인
      console.log('=== 템플릿 변수명 전체 목록 ===');
      const allKeys = Object.keys(templateData);
      allKeys.forEach(key => {
        console.log(`${key}:`, templateData[key]);
      });
      
      // 안정적인 docxtemplater API 사용
      doc.setData(templateData);
      
      // 템플릿 렌더링
      console.log('=== 템플릿 렌더링 시작 ===');
      try {
        doc.render();
        console.log('=== 템플릿 렌더링 완료 ===');
      } catch (renderError) {
        console.error('=== 템플릿 렌더링 오류 ===');
        console.error('오류 메시지:', renderError.message);
        console.error('오류 스택:', renderError.stack);
        
        // 렌더링 오류가 있어도 계속 진행
        console.log('렌더링 오류 무시하고 계속 진행...');
      }
      
      // Word 문서를 Buffer로 생성
      const report = doc.getZip().generate({
        type: 'nodebuffer',
        compression: 'DEFLATE'
      });
      
      console.log('Word 문서 생성 완료, 크기:', report.length);
      return report;
      
    } catch (error) {
      console.error('docxtemplater 오류:', error);
      // 오류 발생 시 원본 템플릿 반환
      console.log('오류로 인해 원본 템플릿 반환');
      return template;
    }
    
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
