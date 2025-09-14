/**
 * JavaScript API 테스트
 * Vercel JavaScript 런타임은 안정적으로 작동
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
    
    // 간단한 응답
    const responseData = {
      success: true,
      message: 'JavaScript API가 정상적으로 작동합니다.',
      received_data: body,
      timestamp: new Date().toISOString(),
      runtime: 'JavaScript'
    };
    
    res.status(200).json(responseData);
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'API 오류가 발생했습니다.',
      message: error.message
    });
  }
}

