/**
 * 배포된 Vercel API 테스트
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

async function testDeployedAPI() {
  try {
    console.log('🚀 배포된 Vercel API 테스트 시작...');
    console.log('테스트 데이터:', JSON.stringify(testData, null, 2));
    
    const response = await fetch('https://vercel-deploy-oqosgyjif-dal-kims-projects.vercel.app/api/create-quotation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData)
    });
    
    console.log('📡 API 응답 상태:', response.status);
    
    if (response.ok) {
      const result = await response.json();
      console.log('✅ API 호출 성공!');
      console.log('응답 데이터:', JSON.stringify(result, null, 2));
      
      if (result.success) {
        console.log('🎉 Word 문서 생성 성공!');
        console.log('견적서 번호:', result.quotation.quotation_number);
        console.log('총 비용:', result.quotation.total_cost);
        console.log('Word 문서 URL:', result.quotation.word_document_url);
      } else {
        console.log('❌ Word 문서 생성 실패:', result.error);
      }
    } else {
      const errorText = await response.text();
      console.log('❌ API 호출 실패:', response.status, errorText);
    }
    
  } catch (error) {
    console.error('💥 테스트 오류:', error.message);
  }
}

testDeployedAPI();
