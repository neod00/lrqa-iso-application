const nodemailer = require('nodemailer');

// 이메일 설정
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'dal.kim@lrqa.com';
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;

// CORS 헤더
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Content-Type': 'application/json'
};

// 이메일 전송 테스트 함수
async function sendTestEmail() {
  console.log('=== 이메일 전송 테스트 시작 ===');
  console.log('SMTP_USER:', SMTP_USER ? 'Set' : 'Not set');
  console.log('SMTP_PASS:', SMTP_PASS ? 'Set' : 'Not set');
  console.log('ADMIN_EMAIL:', ADMIN_EMAIL);
  
  if (!SMTP_USER || !SMTP_PASS) {
    console.log('SMTP credentials not configured, skipping email notification');
    return { success: false, message: 'SMTP credentials not configured' };
  }

  // Gmail 설정
  const transporter = nodemailer.createTransporter({
    service: 'gmail',
    auth: {
      user: SMTP_USER,
      pass: SMTP_PASS
    }
  });

  const testSubject = '[LRQA 테스트] 이메일 전송 테스트';
  const testBody = `
이메일 전송 테스트입니다.

테스트 시간: ${new Date().toLocaleString('ko-KR')}
테스트 환경: Netlify Functions

이 메일이 정상적으로 수신되었다면 이메일 시스템이 올바르게 작동하고 있습니다.

감사합니다.
LRQA Korea 자동 시스템
`;

  try {
    console.log('관리자에게 테스트 이메일 전송 시도...');
    
    await transporter.sendMail({
      from: SMTP_USER,
      to: ADMIN_EMAIL,
      subject: testSubject,
      text: testBody
    });
    
    console.log('테스트 이메일 전송 성공!');
    return { success: true, message: '테스트 이메일이 성공적으로 전송되었습니다.' };
    
  } catch (error) {
    console.error('이메일 전송 오류:', error);
    return { success: false, message: `이메일 전송 실패: ${error.message}` };
  }
}

// 메인 핸들러
exports.handler = async (event, context) => {
  console.log('=== test-email 함수 시작 ===');
  
  // CORS 처리
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const result = await sendTestEmail();
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(result)
    };
    
  } catch (error) {
    console.error('함수 실행 오류:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        message: '함수 실행 오류',
        error: error.message 
      })
    };
  }
};
