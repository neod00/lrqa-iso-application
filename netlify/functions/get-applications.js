const { google } = require('googleapis');

// Google Sheets 설정
const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SHEET_NAME = 'ISO_Applications';

// CORS 헤더
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Content-Type': 'application/json'
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

// 신청서 데이터 가져오기
async function getApplications() {
  const sheets = await getGoogleSheetsClient();
  
  try {
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A:Z`
    });

    const rows = response.data.values || [];
    if (rows.length === 0) {
      return [];
    }

    // 첫 번째 행은 헤더이므로 제외
    const headers = rows[0];
    const data = rows.slice(1);

    const applications = data.map(row => {
      const obj = {};
      headers.forEach((header, index) => {
        obj[header] = row[index] || '';
      });
      return obj;
    });

    // 신청일시 기준으로 최신순 정렬
    applications.sort((a, b) => {
      const dateA = new Date(a['신청일시'] || 0);
      const dateB = new Date(b['신청일시'] || 0);
      return dateB - dateA; // 최신순 (내림차순)
    });

    return applications;
  } catch (error) {
    console.error('Error fetching applications:', error);
    throw error;
  }
}

// 통계 데이터 생성
function generateStats(applications) {
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  const stats = {
    total: applications.length,
    new: 0,
    monthly: 0,
    completed: 0
  };

  applications.forEach(app => {
    const status = app['상태'] || '';
    const dateStr = app['신청일시'] || '';
    
    if (status === '신규') {
      stats.new++;
    } else if (status === '완료') {
      stats.completed++;
    }

    // 이달의 신청서 카운트
    if (dateStr) {
      const appDate = new Date(dateStr);
      if (appDate.getMonth() === currentMonth && appDate.getFullYear() === currentYear) {
        stats.monthly++;
      }
    }
  });

  return stats;
}

// 메인 핸들러
exports.handler = async (event, context) => {
  // CORS 처리
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers
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
    const applications = await getApplications();
    const stats = generateStats(applications);

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: {
          applications,
          stats,
          sheetUrl: `https://docs.google.com/spreadsheets/d/${SHEET_ID}/edit`
        }
      })
    };
  } catch (error) {
    console.error('Error processing request:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        message: '데이터 로드 중 오류가 발생했습니다.' 
      })
    };
  }
};
