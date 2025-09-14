/**
 * 이메일 전송 API
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

    // 이메일 전송
    const emailResult = sendQuotationEmail(body);
    
    // 응답 데이터 구성
    const responseData = {
      success: true,
      message: '이메일이 성공적으로 전송되었습니다.',
      email_id: emailResult.email_id,
      recipient: emailResult.recipient,
      sent_at: new Date().toISOString()
    };
    
    res.status(200).json(responseData);
    
  } catch (error) {
    console.error('Error sending email:', error);
    res.status(500).json({
      success: false,
      error: '이메일 전송 중 오류가 발생했습니다.',
      message: error.message
    });
  }
}

function sendQuotationEmail(data) {
  // 이메일 데이터 추출
  const recipientEmail = data.recipient_email;
  const quotationData = data.quotation || {};
  const companyName = quotationData.company_name || '고객사';
  const quotationNumber = quotationData.quotation_number || 'N/A';
  const totalCost = quotationData.total_cost || 0;
  
  // 이메일 내용 생성
  const emailContent = generateEmailContent(quotationData);
  
  // 실제 환경에서는 여기서 실제 이메일 서비스 (SendGrid, AWS SES 등)를 사용
  // 현재는 시뮬레이션만 수행
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  const hash = Math.abs(recipientEmail.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0);
    return a & a;
  }, 0));
  const emailId = `EMAIL_${timestamp}_${hash.toString().padStart(4, '0')}`;
  
  console.log('이메일 전송 시뮬레이션:');
  console.log(`  수신자: ${recipientEmail}`);
  console.log(`  제목: [LRQA] 견적서 - ${companyName}`);
  console.log(`  견적서 번호: ${quotationNumber}`);
  console.log(`  총 견적 금액: ${totalCost.toLocaleString()}원`);
  
  return {
    email_id: emailId,
    recipient: recipientEmail,
    subject: `[LRQA] 견적서 - ${companyName}`,
    content: emailContent,
    sent_at: new Date().toISOString()
  };
}

function generateEmailContent(quotationData) {
  const companyName = quotationData.company_name || '고객사';
  const quotationNumber = quotationData.quotation_number || 'N/A';
  const totalCost = quotationData.total_cost || 0;
  const standards = quotationData.standards || [];
  const totalAuditDays = quotationData.total_audit_days || 0;
  
  const content = `
안녕하세요, ${companyName} 담당자님

LRQA Korea에서 견적서를 발송해드립니다.

■ 견적서 정보
- 견적서 번호: ${quotationNumber}
- 회사명: ${companyName}
- 적용 표준: ${standards.join(', ')}
- 총 심사일수: ${totalAuditDays}일
- 총 견적 금액: ${totalCost.toLocaleString()}원 (VAT 포함)

■ 다음 단계
1. 견적서 검토 (7일 이내)
2. 계약서 작성 및 검토
3. 심사 일정 조율
4. 심사 진행

문의사항이 있으시면 언제든지 연락주시기 바랍니다.

감사합니다.

LRQA Korea
사업개발본부
Tel: 02-1234-5678
Email: info@lrqa.co.kr
`;
  
  return content;
}

