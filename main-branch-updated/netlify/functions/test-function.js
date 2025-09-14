// 환경 변수 테스트 함수
exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json'
  };

  // CORS 처리
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers
    };
  }

  try {
    const envStatus = {
      GOOGLE_SHEET_ID: process.env.GOOGLE_SHEET_ID ? '✅ 설정됨' : '❌ 누락',
      GOOGLE_PROJECT_ID: process.env.GOOGLE_PROJECT_ID ? '✅ 설정됨' : '❌ 누락',
      GOOGLE_PRIVATE_KEY_ID: process.env.GOOGLE_PRIVATE_KEY_ID ? '✅ 설정됨' : '❌ 누락',
      GOOGLE_CLIENT_EMAIL: process.env.GOOGLE_CLIENT_EMAIL ? '✅ 설정됨' : '❌ 누락',
      GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID ? '✅ 설정됨' : '❌ 누락',
      GOOGLE_PRIVATE_KEY: process.env.GOOGLE_PRIVATE_KEY ? '✅ 설정됨' : '❌ 누락',
      ADMIN_EMAIL: process.env.ADMIN_EMAIL ? '✅ 설정됨' : '❌ 누락',
      SMTP_USER: process.env.SMTP_USER ? '✅ 설정됨' : '❌ 누락',
      SMTP_PASS: process.env.SMTP_PASS ? '✅ 설정됨' : '❌ 누락',
      timestamp: new Date().toISOString(),
      functionWorking: true
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        message: '테스트 함수가 정상적으로 실행되었습니다.',
        environmentVariables: envStatus
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        message: '테스트 함수 실행 중 오류가 발생했습니다.',
        error: error.message
      })
    };
  }
}; 
