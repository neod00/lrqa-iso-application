/**
 * 견적서 생성 API - JavaScript 버전
 * jinja2와 유사한 템플릿 처리를 JavaScript로 구현
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
    
    console.log('핵심두뇌 API 호출 시도...');
    console.log('핵심두뇌 API 호출:', coreBrainUrl);
    console.log('요청 데이터:', JSON.stringify(requestData, null, 2));
    
    const response = await fetch(coreBrainUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('핵심두뇌 API 응답:', result);
    return result;
    
  } catch (error) {
    console.log('핵심두뇌 API 호출 오류:', error.message);
    return null;
  }
}

async function createQuotationData(applicationData) {
  console.log('전송된 데이터:', JSON.stringify(applicationData, null, 2));
  
  const appData = applicationData.applicationData || {};
  console.log('standards 배열:', applicationData.standards);
  console.log('applicationData ISO표준:', appData['ISO표준']);
  
  // 핵심두뇌 API 호출 시도
  let coreBrainResult = null;
  try {
    coreBrainResult = await callCoreBrainAPI(appData);
  } catch (error) {
    console.log('핵심두뇌 API 호출 실패, 기본 견적 계산 사용');
  }
  
  // 표준 처리
  let standards = [];
  if (appData['ISO표준']) {
    const isoStandard = appData['ISO표준'].toLowerCase();
    console.log('표준 처리:', `"${isoStandard}" -> "${isoStandard}"`);
    standards = [isoStandard.toUpperCase()];
  }
  console.log('변환된 standards:', standards);
  
  // ISO 14001 포함 여부 확인
  const has_iso14001 = standards.some(std => std.toLowerCase().includes('14001'));
  console.log('has_iso14001 계산:', has_iso14001);
  
  if (coreBrainResult) {
    console.log('핵심두뇌 API 결과 사용');
    return {
      company_name: appData['법인명(국문)'] || 'Unknown Company',
      client_name: appData['법인명(국문)'] || 'Unknown Company',
      client_address: appData['본사주소'] || '서울시 강남구',
      standards: standards,
      total_employees: parseInt(appData['총직원수']) || 30,
      quotation_date: new Date().toISOString().split('T')[0],
      quotation_number: `Q${new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)}`,
      total_sites: 1,
      has_iso14001: has_iso14001,
      has_iso45001: standards.some(std => std.toLowerCase().includes('45001')),
      total_audit_days: coreBrainResult.total_audit_days || 3,
      total_cost: coreBrainResult.total_cost || 4200000,
      breakdowns: coreBrainResult.breakdowns || []
    };
  } else {
    console.log('기본 견적 계산 사용');
    
    // 기본 견적 계산
    const baseDays = 3;
    const baseCost = baseDays * 1400000; // 일당 140만원
    
    return {
      company_name: appData['법인명(국문)'] || 'Unknown Company',
      client_name: appData['법인명(국문)'] || 'Unknown Company',
      client_address: appData['본사주소'] || '서울시 강남구',
      standards: standards,
      total_employees: parseInt(appData['총직원수']) || 30,
      quotation_date: new Date().toISOString().split('T')[0],
      quotation_number: `Q${new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)}`,
      total_sites: 1,
      has_iso14001: has_iso14001,
      has_iso45001: standards.some(std => std.toLowerCase().includes('45001')),
      total_audit_days: baseDays,
      total_cost: baseCost,
      breakdowns: [{
        standard: standards[0] || 'ISO9001',
        stage1_days: baseDays,
        stage2_days: 0,
        surveillance_days: 0,
        cost: baseCost
      }]
    };
  }
}

// jinja2와 유사한 템플릿 처리 함수들
function formatCurrency(value) {
  if (typeof value !== 'number') return '0원';
  return value.toLocaleString('ko-KR') + '원';
}

function formatNumber(value) {
  if (typeof value !== 'number') return '0';
  return value.toLocaleString('ko-KR');
}

function formatDate(value) {
  if (!value) return new Date().toISOString().split('T')[0];
  if (typeof value === 'string') return value;
  return new Date(value).toISOString().split('T')[0];
}

function safeDivide(a, b) {
  if (!b || b === 0) return 0;
  return a / b;
}

async function generateWordDocument(quotationData, quotation_number) {
  console.log('=== applicationData 확인 ===');
  console.log('applicationData 존재:', !!quotationData);
  console.log('applicationData 키 개수:', Object.keys(quotationData).length);
  console.log('법인명(국문):', quotationData.company_name);
  console.log('담당자명:', quotationData.client_name);
  console.log('총직원수:', quotationData.total_employees);
  console.log('standards:', quotationData.standards);
  console.log('has_iso14001:', quotationData.has_iso14001);
  
  console.log('=== quotationData 객체 확인 ===');
  console.log('quotationData.company_name:', quotationData.company_name);
  console.log('quotationData.standards:', quotationData.standards);
  console.log('quotationData.has_iso14001:', quotationData.has_iso14001);
  console.log('quotationData.total_employees:', quotationData.total_employees);
  
  // 템플릿 파일 로드
  console.log('로컬 파일 시스템에서 템플릿 읽기 시도...');
  console.log('현재 작업 디렉토리:', process.cwd());
  console.log('__dirname:', __dirname);
  
  let templatePath = path.join(process.cwd(), 'public', 'templates', 'LRQA_quotation.docx');
  console.log('경로 시도:', templatePath);
  
  if (!fs.existsSync(templatePath)) {
    console.log('파일이 존재하지 않음:', templatePath);
    templatePath = path.join(process.cwd(), 'templates', 'LRQA_quotation.docx');
    console.log('경로 시도:', templatePath);
    
    if (!fs.existsSync(templatePath)) {
      console.log('파일이 존재하지 않음:', templatePath);
      templatePath = path.join(process.cwd(), 'public', 'templates', 'LRQA_quotation.docx');
      console.log('경로 시도:', templatePath);
      
      if (!fs.existsSync(templatePath)) {
        console.log('파일이 존재하지 않음:', templatePath);
        templatePath = path.join(process.cwd(), 'templates', 'LRQA_quotation.docx');
        console.log('경로 시도:', templatePath);
        
        if (!fs.existsSync(templatePath)) {
          console.log('파일이 존재하지 않음:', templatePath);
          templatePath = path.join(process.cwd(), 'vercel-deploy', 'public', 'templates', 'LRQA_quotation.docx');
          console.log('템플릿 파일 로드 성공:', templatePath);
        }
      }
    }
  }
  
  const template = fs.readFileSync(templatePath);
  console.log('=== 템플릿 데이터 준비 시작 ===');
  console.log('quotationData.company_name:', quotationData.company_name);
  console.log('quotationData.standards:', quotationData.standards);
  console.log('quotationData.has_iso14001:', quotationData.has_iso14001);
  
  // 템플릿 데이터 준비 (jinja2와 유사한 형식)
  const templateData = {
    // 기본 정보
    client_name: quotationData.client_name || quotationData.company_name,
    client_address: quotationData.client_address,
    standards_text: quotationData.standards.join(', '),
    quotation_date: formatDate(quotationData.quotation_date),
    quotation_number: quotationData.quotation_number,
    total_sites: quotationData.total_sites || 1,
    total_employees: quotationData.total_employees,
    
    // 견적 정보
    total_audit_days: quotationData.total_audit_days,
    total_cost: quotationData.total_cost,
    total_cost_with_travel: quotationData.total_cost + (quotationData.total_cost * 0.1),
    travel_expense: quotationData.total_cost * 0.1,
    
    // 포맷된 값들 (jinja2 필터와 유사)
    total_audit_days_formatted: formatNumber(quotationData.total_audit_days) + '일',
    total_cost_formatted: formatCurrency(quotationData.total_cost),
    total_cost_with_travel_formatted: formatCurrency(quotationData.total_cost + (quotationData.total_cost * 0.1)),
    travel_expense_formatted: formatCurrency(quotationData.total_cost * 0.1),
    
    // ISO별 정보
    has_iso9001: quotationData.standards.some(std => std.toLowerCase().includes('9001')),
    has_iso14001: quotationData.has_iso14001,
    has_iso45001: quotationData.has_iso45001,
    
    // ISO 9001 정보
    iso9001_days: quotationData.standards.some(std => std.toLowerCase().includes('9001')) ? quotationData.total_audit_days : 0,
    iso9001_cost: quotationData.standards.some(std => std.toLowerCase().includes('9001')) ? quotationData.total_cost : 0,
    iso9001_days_formatted: quotationData.standards.some(std => std.toLowerCase().includes('9001')) ? formatNumber(quotationData.total_audit_days) + '일' : '0일',
    iso9001_cost_formatted: quotationData.standards.some(std => std.toLowerCase().includes('9001')) ? formatCurrency(quotationData.total_cost) : '0원',
    
    // ISO 14001 정보
    iso14001_days: quotationData.has_iso14001 ? quotationData.total_audit_days : 0,
    iso14001_cost: quotationData.has_iso14001 ? quotationData.total_cost : 0,
    iso14001_days_formatted: quotationData.has_iso14001 ? formatNumber(quotationData.total_audit_days) + '일' : '0일',
    iso14001_cost_formatted: quotationData.has_iso14001 ? formatCurrency(quotationData.total_cost) : '0원',
    
    // ISO 45001 정보
    iso45001_days: quotationData.has_iso45001 ? quotationData.total_audit_days : 0,
    iso45001_cost: quotationData.has_iso45001 ? quotationData.total_cost : 0,
    iso45001_days_formatted: quotationData.has_iso45001 ? formatNumber(quotationData.total_audit_days) + '일' : '0일',
    iso45001_cost_formatted: quotationData.has_iso45001 ? formatCurrency(quotationData.total_cost) : '0원',
    
    // 기타
    created_at: new Date().toISOString(),
    year: new Date().getFullYear()
  };
  
  console.log('템플릿 파일 크기:', template.length);
  console.log('템플릿 데이터 키 개수:', Object.keys(templateData).length);
  console.log('has_iso14001 값:', templateData.has_iso14001);
  console.log('standards_text 값:', templateData.standards_text);
  
  // 디버깅: 주요 변수들 확인
  console.log('=== 템플릿 변수 디버깅 ===');
  console.log('total_audit_days:', templateData.total_audit_days);
  console.log('total_cost_with_travel_formatted:', templateData.total_cost_with_travel_formatted);
  console.log('iso14001_surveillance_days:', templateData.iso14001_days);
  console.log('iso14001_stage1_2_days:', templateData.iso14001_days);
  console.log('iso14001_stage1_2_cost_formatted:', templateData.iso14001_cost_formatted);
  console.log('travel_expense_formatted:', templateData.travel_expense_formatted);
  
  try {
    // docxtemplater 사용
    const zip = new PizZip(template);
    const doc = new Docxtemplater(zip, {
      paragraphLoop: true,
      linebreaks: true,
      errorLogging: true
    });
    
    console.log('=== docxtemplater 설정 확인 ===');
    console.log('docxtemplater 인스턴스 생성 완료');
    
    // 템플릿 내용 확인
    console.log('=== 템플릿 내용 확인 ===');
    const templateContent = zip.file('word/document.xml').asText();
    console.log('템플릿에 quotation_date 포함:', templateContent.includes('quotation_date'));
    console.log('템플릿에 {{ quotation_date }} 포함:', templateContent.includes('{{ quotation_date }}'));
    console.log('템플릿에 { quotation_date } 포함:', templateContent.includes('{ quotation_date }'));
    console.log('템플릿 내용 샘플:', templateContent.substring(0, 500));
    
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
    console.log('iso14001_surveillance_days:', templateData.iso14001_days);
    console.log('travel_expense_formatted:', templateData.travel_expense_formatted);
    
    // 템플릿에서 사용하는 모든 변수명 확인
    console.log('=== 템플릿 변수명 전체 목록 ===');
    const allKeys = Object.keys(templateData);
    allKeys.forEach(key => {
      console.log(`${key}:`, templateData[key]);
    });
    
    // 안정적인 docxtemplater API 사용
    // doc.render(templateData)로 변경 (setData는 deprecated)
    doc.render(templateData);
    
    console.log('=== docxtemplater 렌더링 완료 ===');
    
    // Word 문서를 Buffer로 변환
    const buffer = doc.getZip().generate({
      type: 'nodebuffer',
      compression: 'DEFLATE',
      compressionOptions: {
        level: 9
      }
    });
    
    console.log('Word 문서 생성 완료, 크기:', buffer.length, 'bytes');
    
    return buffer;
    
  } catch (error) {
    console.error('docxtemplater 오류:', error);
    console.log('오류로 인해 원본 템플릿 반환');
    
    // 오류 발생 시 원본 템플릿 반환
    return template;
  }
}

