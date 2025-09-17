/**
 * Google Sheets 데이터 정렬 문제 수정 스크립트 (v2)
 * 기존 데이터가 한 칸씩 밀린 문제를 해결합니다.
 * netlify/functions/submit-application.js와 동일한 방식 사용
 */

const { google } = require('googleapis');

// 환경 변수
const SHEET_ID = '1qX7aAZuC5AimWEg-SeLvyoxyHWGn_E9Pb2f-OBd4VS0';
const SHEET_NAME = '신청서데이터';

// Google Sheets API 클라이언트 초기화
async function getGoogleSheetsClient() {
  console.log('=== Google Sheets 클라이언트 초기화 시작 ===');
  
  // 환경 변수 확인
  if (!process.env.GOOGLE_PROJECT_ID) {
    throw new Error('GOOGLE_PROJECT_ID 환경 변수가 설정되지 않았습니다.');
  }
  if (!process.env.GOOGLE_PRIVATE_KEY) {
    throw new Error('GOOGLE_PRIVATE_KEY 환경 변수가 설정되지 않았습니다.');
  }
  if (!process.env.GOOGLE_CLIENT_EMAIL) {
    throw new Error('GOOGLE_CLIENT_EMAIL 환경 변수가 설정되지 않았습니다.');
  }
  
  console.log('환경 변수 검증 완료');
  
  try {
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
    console.log('Google Sheets 클라이언트 초기화 완료');
    return sheets;
  } catch (error) {
    console.error('Google Sheets 클라이언트 초기화 실패:', error);
    throw error;
  }
}

// 현재 데이터 분석
async function analyzeCurrentData() {
  console.log('=== Google Sheets 데이터 분석 시작 ===');
  
  const sheets = await getGoogleSheetsClient();
  
  try {
    // 모든 데이터 읽기
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A:Z`
    });

    const rows = response.data.values || [];
    console.log(`총 ${rows.length}개의 행이 있습니다.`);
    
    if (rows.length === 0) {
      console.log('데이터가 없습니다.');
      return { sheets, rows: [], headers: [] };
    }
    
    // 헤더 정보
    const headers = rows[0];
    console.log('헤더 정보:');
    console.log('인증만료일 위치:', headers.indexOf('인증만료일'));
    console.log('총직원수 위치:', headers.indexOf('총직원수'));
    console.log('정규직수 위치:', headers.indexOf('정규직수'));
    console.log('비정규직수 위치:', headers.indexOf('비정규직수'));
    console.log('하청업체직원수 위치:', headers.indexOf('하청업체직원수'));
    console.log('임시직수 위치:', headers.indexOf('임시직수'));
    
    // 첫 번째 데이터 행 분석
    if (rows.length > 1) {
      const firstDataRow = rows[1];
      console.log('\n첫 번째 데이터 행 분석:');
      console.log('인증만료일 값:', firstDataRow[headers.indexOf('인증만료일')]);
      console.log('총직원수 값:', firstDataRow[headers.indexOf('총직원수')]);
      console.log('정규직수 값:', firstDataRow[headers.indexOf('정규직수')]);
      console.log('비정규직수 값:', firstDataRow[headers.indexOf('비정규직수')]);
      console.log('하청업체직원수 값:', firstDataRow[headers.indexOf('하청업체직원수')]);
      console.log('임시직수 값:', firstDataRow[headers.indexOf('임시직수')]);
    }
    
    return { sheets, rows, headers };
  } catch (error) {
    console.error('데이터 읽기 오류:', error.message);
    throw error;
  }
}

// 데이터 정렬 수정
async function fixDataAlignment() {
  console.log('=== 데이터 정렬 수정 시작 ===');
  
  const { sheets, rows, headers } = await analyzeCurrentData();
  
  if (rows.length <= 1) {
    console.log('수정할 데이터가 없습니다.');
    return;
  }
  
  // 헤더 인덱스 찾기
  const certExpiryDateIndex = headers.indexOf('인증만료일');
  const totalEmployeesIndex = headers.indexOf('총직원수');
  const permanentEmployeesIndex = headers.indexOf('정규직수');
  const temporaryEmployeesIndex = headers.indexOf('비정규직수');
  const contractorEmployeesIndex = headers.indexOf('하청업체직원수');
  const casualEmployeesIndex = headers.indexOf('임시직수');
  
  console.log('헤더 인덱스:', {
    certExpiryDateIndex,
    totalEmployeesIndex,
    permanentEmployeesIndex,
    temporaryEmployeesIndex,
    contractorEmployeesIndex,
    casualEmployeesIndex
  });
  
  // 각 데이터 행에 대해 수정
  const updatedRows = [];
  
  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    console.log(`\n행 ${i} 수정 중...`);
    
    // 현재 값들 저장
    const currentValues = {
      certExpiryDate: row[certExpiryDateIndex] || '',
      totalEmployees: row[totalEmployeesIndex] || '',
      permanentEmployees: row[permanentEmployeesIndex] || '',
      temporaryEmployees: row[temporaryEmployeesIndex] || '',
      contractorEmployees: row[contractorEmployeesIndex] || '',
      casualEmployees: row[casualEmployeesIndex] || ''
    };
    
    console.log('현재 값들:', currentValues);
    
    // 데이터가 한 칸씩 밀린 경우를 확인
    // 인증만료일에 총직원수가 들어있고, 총직원수에 정규직수가 들어있는 경우
    if (currentValues.certExpiryDate && !isNaN(currentValues.certExpiryDate) && 
        currentValues.totalEmployees && !isNaN(currentValues.totalEmployees)) {
      
      console.log('데이터 정렬 문제 발견, 수정 중...');
      
      // 새로운 행 생성 (기존 행 복사)
      const newRow = [...row];
      
      // 올바른 위치로 데이터 이동
      newRow[certExpiryDateIndex] = ''; // 인증만료일은 보통 비어있어야 함
      newRow[totalEmployeesIndex] = currentValues.certExpiryDate;
      newRow[permanentEmployeesIndex] = currentValues.totalEmployees;
      newRow[temporaryEmployeesIndex] = currentValues.permanentEmployees;
      newRow[contractorEmployeesIndex] = currentValues.temporaryEmployees;
      newRow[casualEmployeesIndex] = currentValues.contractorEmployees;
      
      updatedRows.push({
        range: `${SHEET_NAME}!A${i + 1}:Z${i + 1}`,
        values: [newRow]
      });
      
      console.log('수정된 값들:', {
        certExpiryDate: newRow[certExpiryDateIndex],
        totalEmployees: newRow[totalEmployeesIndex],
        permanentEmployees: newRow[permanentEmployeesIndex],
        temporaryEmployees: newRow[temporaryEmployeesIndex],
        contractorEmployees: newRow[contractorEmployeesIndex],
        casualEmployees: newRow[casualEmployeesIndex]
      });
    } else {
      console.log('이 행은 수정이 필요하지 않습니다.');
    }
  }
  
  // 수정된 데이터를 시트에 업데이트
  if (updatedRows.length > 0) {
    console.log(`\n${updatedRows.length}개 행을 수정합니다...`);
    
    try {
      await sheets.spreadsheets.values.batchUpdate({
        spreadsheetId: SHEET_ID,
        resource: {
          valueInputOption: 'RAW',
          data: updatedRows
        }
      });
      
      console.log('데이터 수정 완료!');
    } catch (error) {
      console.error('데이터 수정 중 오류:', error.message);
      throw error;
    }
  } else {
    console.log('수정할 데이터가 없습니다.');
  }
  
  console.log('\n=== 데이터 정렬 수정 완료 ===');
}

// 메인 실행
async function main() {
  try {
    console.log('주의: 이 스크립트를 실행하기 전에 다음을 확인하세요:');
    console.log('1. SHEET_ID를 실제 Google Sheets ID로 변경');
    console.log('2. google-credentials.json 파일이 존재하는지 확인');
    console.log('3. 서비스 계정이 해당 시트에 대한 편집 권한을 가지고 있는지 확인');
    console.log('\n실제 수정을 진행하려면 아래 주석을 해제하세요.\n');
    
    // 실제 수정을 진행하려면 아래 주석을 해제
    // await fixDataAlignment();
    
    // 분석만 수행
    await analyzeCurrentData();
  } catch (error) {
    console.error('오류 발생:', error);
  }
}

// 스크립트 실행
if (require.main === module) {
  main();
}

module.exports = { analyzeCurrentData, fixDataAlignment };
