/**
 * Google Sheets 데이터 정렬 문제 수정 스크립트
 * 기존 데이터가 한 칸씩 밀린 문제를 해결합니다.
 */

const { GoogleSpreadsheet } = require('google-spreadsheet');
require('dotenv').config();

// 환경 변수
const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SHEET_NAME = process.env.GOOGLE_SHEET_NAME || '신청서데이터';

// Google Sheets 클라이언트 초기화
async function getGoogleSheetsClient() {
  const doc = new GoogleSpreadsheet(SHEET_ID);
  
  // 서비스 계정 인증
  await doc.useServiceAccountAuth({
    client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
  });
  
  await doc.loadInfo();
  return doc;
}

// 현재 데이터 분석
async function analyzeCurrentData() {
  console.log('=== Google Sheets 데이터 분석 시작 ===');
  
  const doc = await getGoogleSheetsClient();
  const sheet = doc.sheetsByTitle[SHEET_NAME];
  
  if (!sheet) {
    throw new Error(`시트 '${SHEET_NAME}'을 찾을 수 없습니다.`);
  }
  
  // 모든 데이터 읽기
  const rows = await sheet.getRows();
  console.log(`총 ${rows.length}개의 행이 있습니다.`);
  
  if (rows.length === 0) {
    console.log('데이터가 없습니다.');
    return;
  }
  
  // 헤더 정보
  const headerRow = sheet.headerValues;
  console.log('헤더 정보:');
  console.log('인증만료일 위치:', headerRow.indexOf('인증만료일'));
  console.log('총직원수 위치:', headerRow.indexOf('총직원수'));
  console.log('정규직수 위치:', headerRow.indexOf('정규직수'));
  console.log('비정규직수 위치:', headerRow.indexOf('비정규직수'));
  
  // 첫 번째 데이터 행 분석
  if (rows.length > 0) {
    const firstRow = rows[0];
    console.log('\n첫 번째 데이터 행 분석:');
    console.log('인증만료일 값:', firstRow.get('인증만료일'));
    console.log('총직원수 값:', firstRow.get('총직원수'));
    console.log('정규직수 값:', firstRow.get('정규직수'));
    console.log('비정규직수 값:', firstRow.get('비정규직수'));
    console.log('하청업체직원수 값:', firstRow.get('하청업체직원수'));
    console.log('임시직수 값:', firstRow.get('임시직수'));
  }
  
  return { sheet, rows, headerRow };
}

// 데이터 정렬 수정
async function fixDataAlignment() {
  console.log('=== 데이터 정렬 수정 시작 ===');
  
  const { sheet, rows, headerRow } = await analyzeCurrentData();
  
  if (rows.length === 0) {
    console.log('수정할 데이터가 없습니다.');
    return;
  }
  
  // 각 행에 대해 데이터 정렬 수정
  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    console.log(`\n행 ${i + 1} 수정 중...`);
    
    // 현재 값들 저장
    const currentValues = {
      certExpiryDate: row.get('인증만료일'),
      totalEmployees: row.get('총직원수'),
      permanentEmployees: row.get('정규직수'),
      temporaryEmployees: row.get('비정규직수'),
      contractorEmployees: row.get('하청업체직원수'),
      casualEmployees: row.get('임시직수')
    };
    
    console.log('현재 값들:', currentValues);
    
    // 데이터가 한 칸씩 밀린 경우를 확인
    // 인증만료일에 총직원수가 들어있고, 총직원수에 정규직수가 들어있는 경우
    if (currentValues.certExpiryDate && !isNaN(currentValues.certExpiryDate) && 
        currentValues.totalEmployees && !isNaN(currentValues.totalEmployees)) {
      
      console.log('데이터 정렬 문제 발견, 수정 중...');
      
      // 올바른 위치로 데이터 이동
      row.set('인증만료일', ''); // 인증만료일은 보통 비어있어야 함
      row.set('총직원수', currentValues.certExpiryDate);
      row.set('정규직수', currentValues.totalEmployees);
      row.set('비정규직수', currentValues.permanentEmployees);
      row.set('하청업체직원수', currentValues.temporaryEmployees);
      row.set('임시직수', currentValues.contractorEmployees);
      
      // 변경사항 저장
      await row.save();
      console.log('수정 완료');
    } else {
      console.log('이 행은 수정이 필요하지 않습니다.');
    }
  }
  
  console.log('\n=== 데이터 정렬 수정 완료 ===');
}

// 메인 실행
async function main() {
  try {
    await fixDataAlignment();
  } catch (error) {
    console.error('오류 발생:', error);
  }
}

// 스크립트 실행
if (require.main === module) {
  main();
}

module.exports = { analyzeCurrentData, fixDataAlignment };
