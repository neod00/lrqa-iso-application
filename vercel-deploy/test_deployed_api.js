/**
 * 배포된 Vercel API 테스트
 */

async function testDeployedAPI() {
  console.log('🚀 배포된 Vercel API 테스트 시작');
  console.log('='.repeat(50));
  
  // A회사 사례 (단일사업장)
  const testData = {
    client_name: 'A회사 (테스트)',
    sites: [{
      name: '울산공장',
      address: '울산광역시',
      standards: ['ISO14001'],
      regularEmployees: 40,
      partTimeEmployees: 10,
      business_sector: '화학',
      business_description: '나프탈렌 생산',
      management_system_maturity: 'MEDIUM'
    }],
    standards: ['ISO14001'],
    options: {
      stage1: true,
      stage2: true,
      surveillance: true,
      recert: true,
      integrated_audit: false,
      remote_audit: false
    }
  };

  try {
    console.log('📡 Vercel API 호출 중...');
    const response = await fetch('https://lrqa-iso-application.vercel.app/api/core-brain', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    
    console.log('✅ API 응답 성공!');
    console.log('\n📊 결과 요약:');
    console.log(`- 클라이언트: ${result.data.client_name}`);
    console.log(`- 총 심사일수: ${result.data.total_audit_days}일`);
    console.log(`- 총 비용: ${result.data.total_cost.toLocaleString()}원`);
    console.log(`- 일당: ${result.data.day_rate.toLocaleString()}원`);
    
    console.log('\n🏢 사업장별 상세:');
    result.data.breakdowns.forEach((breakdown, index) => {
      console.log(`  ${index + 1}. ${breakdown.site_name}:`);
      console.log(`     - ENP: ${breakdown.enp}명, 복잡도: ${breakdown.complexity}`);
      console.log(`     - EA 코드: ${breakdown.ea_code} (${breakdown.ea_matched_keyword})`);
      console.log(`     - 심사일수: ${breakdown.total_days}일`);
      console.log(`     - 비용: ${breakdown.cost.toLocaleString()}원`);
    });

    console.log('\n📋 가정사항:');
    result.data.assumptions.forEach(assumption => {
      console.log(`  - ${assumption.item}: ${assumption.description}`);
    });

    console.log('\n🎯 배포된 API가 정상 작동합니다!');
    
  } catch (error) {
    console.error('❌ API 호출 실패:', error.message);
    console.log('\n🔍 문제 해결 방법:');
    console.log('1. Vercel 배포가 완전히 완료되었는지 확인');
    console.log('2. API 엔드포인트 URL 확인');
    console.log('3. 네트워크 연결 상태 확인');
  }
}

// 테스트 실행
testDeployedAPI();