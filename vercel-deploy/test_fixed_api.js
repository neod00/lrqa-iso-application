/**
 * 수정된 API 테스트
 */

const testData = {
  company_name: "테스트 회사",
  company_name_en: "Test Company",
  contact_name: "김테스트",
  contact_email: "test@example.com",
  contact_phone: "010-1234-5678",
  address: "서울시 강남구 테헤란로 123",
  total_employees: 50,
  standards: ["ISO 9001", "ISO 14001"]
};

async function testCreateQuotation() {
  try {
    console.log('테스트 데이터:', JSON.stringify(testData, null, 2));
    
    // 로컬에서 API 함수 직접 테스트
    const { createQuotationData } = require('./api/create-quotation.js');
    
    // createQuotationData 함수가 export되지 않았으므로 직접 import
    console.log('API 함수를 직접 테스트할 수 없습니다. Vercel 배포 후 테스트하세요.');
    
  } catch (error) {
    console.error('테스트 오류:', error.message);
  }
}

testCreateQuotation();
