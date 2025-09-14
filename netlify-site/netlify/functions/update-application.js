const { google } = require('googleapis');

// Google Sheets 설정
const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SHEET_NAME = 'ISO_Applications';

// CORS 헤더
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'PUT, OPTIONS',
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

// 신청서 데이터 업데이트
async function updateApplication(rowIndex, updatedData) {
  const sheets = await getGoogleSheetsClient();
  
  try {
    // 헤더 가져오기
    const headerResponse = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A1:Z1`
    });
    
    const headers = headerResponse.data.values[0];
    
    // 업데이트할 데이터 배열 생성
    const rowData = headers.map(header => updatedData[header] || '');
    
    // 특정 행 업데이트
    await sheets.spreadsheets.values.update({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A${rowIndex}:Z${rowIndex}`,
      valueInputOption: 'RAW',
      resource: {
        values: [rowData]
      }
    });
    
    return { success: true };
  } catch (error) {
    console.error('Error updating application:', error);
    throw error;
  }
}

// 특정 신청서 조회
async function getApplicationByTimestamp(timestamp) {
  const sheets = await getGoogleSheetsClient();
  
  try {
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A:Z`
    });

    const rows = response.data.values || [];
    if (rows.length === 0) {
      return null;
    }

    const headers = rows[0];
    const data = rows.slice(1);

    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      if (row[0] === timestamp) { // 첫 번째 열이 신청일시
        const obj = {};
        headers.forEach((header, index) => {
          obj[header] = row[index] || '';
        });
        obj.rowIndex = i + 2; // 실제 시트 행 번호 (헤더 + 1)
        return obj;
      }
    }
    
    return null;
  } catch (error) {
    console.error('Error fetching application:', error);
    throw error;
  }
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

  if (event.httpMethod !== 'PUT') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const { timestamp, updatedData } = JSON.parse(event.body);
    
    if (!timestamp || !updatedData) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          success: false, 
          message: '필수 데이터가 누락되었습니다.' 
        })
      };
    }

    // 기존 신청서 조회
    const existingApp = await getApplicationByTimestamp(timestamp);
    if (!existingApp) {
      return {
        statusCode: 404,
        headers,
        body: JSON.stringify({ 
          success: false, 
          message: '신청서를 찾을 수 없습니다.' 
        })
      };
    }

    // 데이터 업데이트
    await updateApplication(existingApp.rowIndex, updatedData);
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ 
        success: true, 
        message: '신청서가 성공적으로 수정되었습니다.' 
      })
    };
    
  } catch (error) {
    console.error('Error processing update:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        message: '신청서 수정 중 오류가 발생했습니다.' 
      })
    };
  }
}; 