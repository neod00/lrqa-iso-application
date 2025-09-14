const { google } = require('googleapis');

// Google Sheets 설정
const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SHEET_NAME = 'ISO_Applications';

// CORS 헤더
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Content-Type': 'text/csv; charset=utf-8'
};

// Google Sheets API 클라이언트 초기화
async function getGoogleSheetsClient() {
  const auth = new google.auth.GoogleAuth({
    credentials: {
      type: 'service_account',
      project_id: process.env.GOOGLE_PROJECT_ID,
      private_key_id: process.env.GOOGLE_PRIVATE_KEY_ID,
      private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
      client_email: process.env.GOOGLE_CLIENT_EMAIL,
      client_id: process.env.GOOGLE_CLIENT_ID,
      auth_uri: 'https://accounts.google.com/o/oauth2/auth',
      token_uri: 'https://oauth2.googleapis.com/token',
      auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
      client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${process.env.GOOGLE_CLIENT_EMAIL}`
    },
    scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });

  const sheets = google.sheets({ version: 'v4', auth });
  return sheets;
}

// CSV 형식으로 변환
function convertToCSV(data) {
  if (!data || data.length === 0) {
    return '';
  }

  // BOM 추가 (Excel에서 UTF-8 한글 인식을 위해)
  const BOM = '\uFEFF';
  
  // 첫 번째 행을 헤더로 사용
  const headers = data[0];
  const rows = data.slice(1);

  // CSV 문자열 생성
  let csvContent = BOM;
  
  // 헤더 추가
  csvContent += headers.map(header => `"${header}"`).join(',') + '\n';
  
  // 데이터 행 추가
  rows.forEach(row => {
    const csvRow = row.map(cell => {
      // 셀 값에 따옴표나 쉼표가 있으면 따옴표로 감싸기
      const cellValue = (cell || '').toString();
      if (cellValue.includes('"') || cellValue.includes(',') || cellValue.includes('\n')) {
        return `"${cellValue.replace(/"/g, '""')}"`;
      }
      return `"${cellValue}"`;
    }).join(',');
    csvContent += csvRow + '\n';
  });

  return csvContent;
}

// 메인 핸들러
exports.handler = async (event, context) => {
  // CORS 처리
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
      }
    };
  }

  if (event.httpMethod !== 'GET') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const sheets = await getGoogleSheetsClient();
    
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A:Z`
    });

    const rows = response.data.values || [];
    if (rows.length === 0) {
      return {
        statusCode: 404,
        headers,
        body: '데이터가 없습니다.'
      };
    }

    const csvContent = convertToCSV(rows);
    const filename = `LRQA_ISO_Applications_${new Date().toISOString().split('T')[0]}.csv`;

    return {
      statusCode: 200,
      headers: {
        ...headers,
        'Content-Disposition': `attachment; filename="${filename}"`
      },
      body: csvContent
    };
  } catch (error) {
    console.error('Error exporting CSV:', error);
    
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        success: false, 
        message: 'CSV 내보내기 중 오류가 발생했습니다.' 
      })
    };
  }
}; 
