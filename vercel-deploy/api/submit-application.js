/**
 * 신청서 제출 API
 * Vercel JavaScript 런타임에서 실행
 */

export default function handler(req, res) {
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

    // 신청서 데이터 검증
    const validationResult = validateApplicationData(body);
    if (!validationResult.valid) {
      res.status(400).json({
        success: false,
        error: '신청서 데이터 검증 실패',
        details: validationResult.errors
      });
      return;
    }

    // 신청서 저장 (실제 환경에서는 데이터베이스에 저장)
    const applicationId = saveApplication(body);
    
    // 응답 데이터 구성
    const responseData = {
      success: true,
      message: '신청서가 성공적으로 제출되었습니다.',
      application_id: applicationId,
      submitted_at: new Date().toISOString(),
      next_steps: [
        '신청서 검토 (1-2 영업일)',
        '견적서 생성 및 발송',
        '계약서 작성 및 검토',
        '심사 일정 조율'
      ]
    };
    
    res.status(200).json(responseData);
    
  } catch (error) {
    console.error('Error submitting application:', error);
    res.status(500).json({
      success: false,
      error: '신청서 제출 중 오류가 발생했습니다.',
      message: error.message
    });
  }
}

function validateApplicationData(data) {
  const errors = [];
  
  // 필수 필드 검증 (프론트엔드 필드명에 맞게 수정)
  if (!data.companyName || data.companyName.trim() === '') {
    errors.push('회사명은 필수 입력 항목입니다.');
  }
  
  if (!data.contactName || data.contactName.trim() === '') {
    errors.push('담당자명은 필수 입력 항목입니다.');
  }
  
  if (!data.contactEmail || data.contactEmail.trim() === '') {
    errors.push('이메일은 필수 입력 항목입니다.');
  }
  
  if (!data.contactPhone || data.contactPhone.trim() === '') {
    errors.push('전화번호는 필수 입력 항목입니다.');
  }
  
  // 이메일 형식 검증 (더 유연하게)
  const email = data.contactEmail || '';
  if (email && !email.includes('@')) {
    errors.push('올바른 이메일 형식이 아닙니다.');
  }
  
  // 전화번호 형식 검증 (더 유연하게)
  const phone = data.contactPhone || '';
  if (phone && phone.replace(/[- ]/g, '').length < 8) {
    errors.push('올바른 전화번호 형식이 아닙니다.');
  }
  
  // 직원 수 검증 (더 유연하게)
  const totalEmployees = parseInt(data.totalEmployees);
  if (isNaN(totalEmployees) || totalEmployees < 1) {
    errors.push('직원 수는 1명 이상의 숫자여야 합니다.');
  }
  
  // 표준 검증 (더 유연하게)
  const standards = data.standards || [];
  if (standards.length === 0) {
    errors.push('최소 1개 이상의 ISO 표준을 선택해야 합니다.');
  }
  
  // 표준 값 정규화 및 검증
  const validStandards = ['ISO 9001', 'ISO 14001', 'ISO 45001', 'ISO9001', 'ISO14001', 'ISO45001'];
  const normalizedStandards = [];
  
  for (const std of standards) {
    let normalizedStd = std;
    
    // 표준 값 정규화
    if (std === 'ISO9001' || std === 'iso9001') {
      normalizedStd = 'ISO 9001';
    } else if (std === 'ISO14001' || std === 'iso14001') {
      normalizedStd = 'ISO 14001';
    } else if (std === 'ISO45001' || std === 'iso45001') {
      normalizedStd = 'ISO 45001';
    }
    
    if (validStandards.includes(normalizedStd)) {
      normalizedStandards.push(normalizedStd);
    } else {
      errors.push(`지원하지 않는 표준입니다: ${std}`);
    }
  }
  
  // 정규화된 표준을 데이터에 다시 설정
  if (normalizedStandards.length > 0) {
    data.standards = normalizedStandards;
  }
  
  // 데이터 처리 동의 검증 (더 유연하게)
  const dataProcessConsent = data.dataProcessConsent;
  if (!dataProcessConsent || (dataProcessConsent !== 'yes' && dataProcessConsent !== true)) {
    errors.push('데이터 처리 동의는 필수입니다.');
  }
  
  // 서명 검증
  if (!data.signature || data.signature.trim() === '') {
    errors.push('서명은 필수 입력 항목입니다.');
  }
  
  return {
    valid: errors.length === 0,
    errors: errors
  };
}

function saveApplication(data) {
  // 신청서 ID 생성
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  const hash = Math.abs(data.companyName.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0);
    return a & a;
  }, 0));
  const applicationId = `APP_${timestamp}_${hash.toString().padStart(4, '0')}`;
  
  // 신청서 데이터 정리 (프론트엔드 필드명에 맞게 수정)
  const applicationData = {
    id: applicationId,
    company_name: data.companyName,
    company_name_en: data.companyNameEn,
    contact_name: data.contactName,
    contact_email: data.contactEmail,
    contact_phone: data.contactPhone,
    address: data.companyAddress,
    standards: data.standards || [],
    total_employees: parseInt(data.totalEmployees) || 0,
    sites: data.sites || [],
    integration: data.integration || {},
    options: data.options || {},
    submitted_at: new Date().toISOString(),
    status: 'submitted'
  };
  
  // 실제 환경에서는 여기서 데이터베이스에 저장
  // 현재는 로그만 출력
  console.log(`신청서 저장: ${applicationId}`);
  console.log(`회사명: ${applicationData.company_name}`);
  console.log(`담당자: ${applicationData.contact_name}`);
  console.log(`표준: ${applicationData.standards.join(', ')}`);
  
  return applicationId;
}
