/**
 * 최종 사례 분석 테스트 - 수정된 핵심두뇌 검증
 */

import { QuoteEngine } from './adj_quote_engine/adj_rules_v22.js';

// 테스트 사례 1: 중소기업 단일사업장 (ISO 9001만)
const scenario1 = {
  client_name: 'G회사 (중소기업 단일사업장)',
  sites: [{
    name: '대전공장',
    address: '대전광역시',
    standards: ['ISO9001'],
    regularEmployees: 25,
    partTimeEmployees: 8,
    contractEmployees: 3,
    dispatchedEmployees: 0,
    shiftWorkers: 0,
    temporaryWorkers: 0,
    seasonalWorkers: 0,
    business_sector: '제조업',
    business_description: '기계부품 제조',
    management_system_maturity: 'MEDIUM'
  }],
  standards: ['ISO9001'],
  options: {
    stage1: true,
    stage2: true,
    surveillance: true,
    recert: true,
    integrated_audit: false,
    remote_audit: false
  }
};

// 테스트 사례 2: 대기업 다수사업장 (ISO 9001 + 14001 + 45001)
const scenario2 = {
  client_name: 'H회사 (대기업 다수사업장)',
  sites: [
    {
      name: '서울본사',
      address: '서울특별시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 300,
      partTimeEmployees: 30,
      contractEmployees: 20,
      dispatchedEmployees: 10,
      shiftWorkers: 50,
      temporaryWorkers: 5,
      seasonalWorkers: 3,
      business_sector: '제조업',
      business_description: '자동차 엔진 제조',
      management_system_maturity: 'HIGH',
      isHeadquarters: true
    },
    {
      name: '울산사업장',
      address: '울산광역시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 150,
      partTimeEmployees: 15,
      contractEmployees: 10,
      dispatchedEmployees: 5,
      shiftWorkers: 25,
      temporaryWorkers: 3,
      seasonalWorkers: 2,
      business_sector: '제조업',
      business_description: '자동차 부품 제조',
      management_system_maturity: 'HIGH',
      isHeadquarters: false
    },
    {
      name: '창원사업장',
      address: '창원시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 100,
      partTimeEmployees: 10,
      contractEmployees: 5,
      dispatchedEmployees: 3,
      shiftWorkers: 15,
      temporaryWorkers: 2,
      seasonalWorkers: 1,
      business_sector: '제조업',
      business_description: '자동차 조립',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '광주사업장',
      address: '광주광역시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 80,
      partTimeEmployees: 8,
      contractEmployees: 4,
      dispatchedEmployees: 2,
      shiftWorkers: 12,
      temporaryWorkers: 1,
      seasonalWorkers: 1,
      business_sector: '제조업',
      business_description: '자동차 검사',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    }
  ],
  standards: ['ISO9001', 'ISO14001', 'ISO45001'],
  options: {
    stage1: true,
    stage2: true,
    surveillance: true,
    recert: true,
    integrated_audit: true,
    remote_audit: false
  }
};

// 테스트 사례 3: IT 서비스업 다수사업장 (ISO 9001만, 원격심사)
const scenario3 = {
  client_name: 'I회사 (IT 서비스업 다수사업장)',
  sites: [
    {
      name: '강남본사',
      address: '서울특별시 강남구',
      standards: ['ISO9001'],
      regularEmployees: 200,
      partTimeEmployees: 30,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: '소프트웨어 개발',
      management_system_maturity: 'HIGH',
      isHeadquarters: true
    },
    {
      name: '판교지사',
      address: '성남시 분당구',
      standards: ['ISO9001'],
      regularEmployees: 80,
      partTimeEmployees: 12,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: 'AI 솔루션 개발',
      management_system_maturity: 'HIGH',
      isHeadquarters: false
    },
    {
      name: '부산지사',
      address: '부산광역시',
      standards: ['ISO9001'],
      regularEmployees: 50,
      partTimeEmployees: 8,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: '웹 개발',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '대구지사',
      address: '대구광역시',
      standards: ['ISO9001'],
      regularEmployees: 40,
      partTimeEmployees: 6,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: '모바일 앱 개발',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '대전지사',
      address: '대전광역시',
      standards: ['ISO9001'],
      regularEmployees: 30,
      partTimeEmployees: 5,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: '데이터 분석',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    }
  ],
  standards: ['ISO9001'],
  options: {
    stage1: true,
    stage2: true,
    surveillance: true,
    recert: true,
    integrated_audit: false,
    remote_audit: true
  }
};

// 테스트 사례 4: 화학업 대규모 단일사업장 (ISO 14001 + 45001)
const scenario4 = {
  client_name: 'J회사 (화학업 대규모 단일사업장)',
  sites: [{
    name: '여수공장',
    address: '여수시',
    standards: ['ISO14001', 'ISO45001'],
    regularEmployees: 800,
    partTimeEmployees: 80,
    contractEmployees: 40,
    dispatchedEmployees: 25,
    shiftWorkers: 150,
    temporaryWorkers: 20,
    seasonalWorkers: 10,
    business_sector: '화학',
    business_description: '석유화학 제품 제조',
    management_system_maturity: 'HIGH'
  }],
  standards: ['ISO14001', 'ISO45001'],
  options: {
    stage1: true,
    stage2: true,
    surveillance: true,
    recert: true,
    integrated_audit: true,
    remote_audit: false
  }
};

// 테스트 사례 5: 건설업 다수사업장 (ISO 9001 + 45001)
const scenario5 = {
  client_name: 'K회사 (건설업 다수사업장)',
  sites: [
    {
      name: '서울본사',
      address: '서울특별시',
      standards: ['ISO9001', 'ISO45001'],
      regularEmployees: 150,
      partTimeEmployees: 20,
      contractEmployees: 10,
      dispatchedEmployees: 5,
      shiftWorkers: 30,
      temporaryWorkers: 8,
      seasonalWorkers: 5,
      business_sector: '건설업',
      business_description: '건축 공사',
      management_system_maturity: 'HIGH',
      isHeadquarters: true
    },
    {
      name: '인천사업장',
      address: '인천광역시',
      standards: ['ISO9001', 'ISO45001'],
      regularEmployees: 80,
      partTimeEmployees: 10,
      contractEmployees: 5,
      dispatchedEmployees: 3,
      shiftWorkers: 15,
      temporaryWorkers: 4,
      seasonalWorkers: 3,
      business_sector: '건설업',
      business_description: '토목 공사',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '부산사업장',
      address: '부산광역시',
      standards: ['ISO9001', 'ISO45001'],
      regularEmployees: 60,
      partTimeEmployees: 8,
      contractEmployees: 4,
      dispatchedEmployees: 2,
      shiftWorkers: 12,
      temporaryWorkers: 3,
      seasonalWorkers: 2,
      business_sector: '건설업',
      business_description: '해상 공사',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '대구사업장',
      address: '대구광역시',
      standards: ['ISO9001', 'ISO45001'],
      regularEmployees: 40,
      partTimeEmployees: 6,
      contractEmployees: 3,
      dispatchedEmployees: 2,
      shiftWorkers: 8,
      temporaryWorkers: 2,
      seasonalWorkers: 1,
      business_sector: '건설업',
      business_description: '도로 공사',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    }
  ],
  standards: ['ISO9001', 'ISO45001'],
  options: {
    stage1: true,
    stage2: true,
    surveillance: true,
    recert: true,
    integrated_audit: true,
    remote_audit: false
  }
};

async function testScenario(scenario, scenarioNumber) {
  console.log(`\n${'='.repeat(70)}`);
  console.log(`🔍 최종 사례 분석 ${scenarioNumber}: ${scenario.client_name}`);
  console.log(`${'='.repeat(70)}`);
  
  const engine = new QuoteEngine();
  
  try {
    const result = await engine.calculate_quote(scenario);
    
    console.log(`\n📊 기본 정보:`);
    console.log(`- 사업장 수: ${scenario.sites.length}개`);
    console.log(`- 표준: ${scenario.standards.join(', ')}`);
    console.log(`- 통합심사: ${scenario.options.integrated_audit ? '✅ 적용' : '❌ 미적용'}`);
    console.log(`- 원격심사: ${scenario.options.remote_audit ? '✅ 적용' : '❌ 미적용'}`);
    
    console.log(`\n💰 견적 결과:`);
    console.log(`- 총 심사일수: ${result.total_audit_days}일`);
    console.log(`- 총 비용: ${result.total_cost.toLocaleString()}원`);
    console.log(`- 일당: ${result.day_rate.toLocaleString()}원`);
    
    console.log(`\n🏢 사업장별 상세:`);
    result.breakdowns.forEach((breakdown, index) => {
      console.log(`  ${index + 1}. ${breakdown.site_name}:`);
      console.log(`     - ENP: ${breakdown.enp}명, 복잡도: ${breakdown.complexity}`);
      if (breakdown.environmental_complexity) {
        console.log(`     - 환경복잡도: ${breakdown.environmental_complexity}`);
      }
      console.log(`     - EA 코드: ${breakdown.ea_code} (${breakdown.ea_matched_keyword})`);
      console.log(`     - 샘플링: ${breakdown.is_sampled ? '✅ 적용' : '❌ 미적용'} (${breakdown.sampling_type})`);
      if (breakdown.original_days) {
        console.log(`     - 원본: ${breakdown.original_days}일 → 실제: ${breakdown.total_days}일`);
        if (breakdown.reduction_rate) {
          console.log(`     - 감축률: ${(breakdown.reduction_rate * 100).toFixed(0)}%`);
        }
      } else {
        console.log(`     - 심사일수: ${breakdown.total_days}일`);
      }
      console.log(`     - 비용: ${breakdown.cost.toLocaleString()}원`);
    });
    
    console.log(`\n📋 가정사항:`);
    result.assumptions.forEach(assumption => {
      console.log(`  - ${assumption.item}: ${assumption.description}`);
    });
    
    // 절약 효과 계산
    if (result.breakdowns.some(b => b.original_days && b.original_days > b.total_days)) {
      const totalOriginalDays = result.breakdowns.reduce((sum, b) => sum + (b.original_days || 0), 0);
      const totalActualDays = result.breakdowns.reduce((sum, b) => sum + b.total_days, 0);
      const savedDays = totalOriginalDays - totalActualDays;
      const savedCost = savedDays * result.day_rate;
      
      console.log(`\n💡 절약 효과:`);
      console.log(`- 절약된 심사일수: ${savedDays}일`);
      console.log(`- 절약된 비용: ${savedCost.toLocaleString()}원`);
      console.log(`- 절약률: ${((savedDays / totalOriginalDays) * 100).toFixed(1)}%`);
    }
    
    return {
      success: true,
      scenario: scenarioNumber,
      client_name: scenario.client_name,
      total_days: result.total_audit_days,
      total_cost: result.total_cost,
      sites_count: scenario.sites.length,
      standards: scenario.standards.length,
      breakdowns: result.breakdowns,
      assumptions: result.assumptions
    };
    
  } catch (error) {
    console.error(`❌ 테스트 사례 ${scenarioNumber} 오류:`, error.message);
    return {
      success: false,
      scenario: scenarioNumber,
      client_name: scenario.client_name,
      error: error.message
    };
  }
}

async function runFinalTests() {
  console.log('🎯 핵심두뇌 최종 사례 분석 테스트');
  console.log('='.repeat(70));
  
  const scenarios = [scenario1, scenario2, scenario3, scenario4, scenario5];
  const results = [];
  
  for (let i = 0; i < scenarios.length; i++) {
    const result = await testScenario(scenarios[i], i + 1);
    results.push(result);
  }
  
  console.log(`\n${'='.repeat(70)}`);
  console.log('📈 최종 테스트 결과 요약');
  console.log(`${'='.repeat(70)}`);
  
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);
  
  console.log(`✅ 성공: ${successful.length}개`);
  console.log(`❌ 실패: ${failed.length}개`);
  
  if (successful.length > 0) {
    console.log(`\n📊 성공한 사례들:`);
    successful.forEach(result => {
      console.log(`  ${result.scenario}. ${result.client_name}: ${result.total_days}일, ${result.total_cost.toLocaleString()}원`);
    });
    
    // 통계 분석
    const totalDays = successful.reduce((sum, r) => sum + r.total_days, 0);
    const totalCost = successful.reduce((sum, r) => sum + r.total_cost, 0);
    const avgDays = totalDays / successful.length;
    const avgCost = totalCost / successful.length;
    
    console.log(`\n📈 통계:`);
    console.log(`- 평균 심사일수: ${avgDays.toFixed(1)}일`);
    console.log(`- 평균 비용: ${avgCost.toLocaleString()}원`);
    console.log(`- 총 심사일수: ${totalDays}일`);
    console.log(`- 총 비용: ${totalCost.toLocaleString()}원`);
  }
  
  if (failed.length > 0) {
    console.log(`\n❌ 실패한 사례들:`);
    failed.forEach(result => {
      console.log(`  ${result.scenario}. ${result.client_name}: ${result.error}`);
    });
  }
  
  console.log(`\n🎯 최종 테스트 완료!`);
}

// 테스트 실행
runFinalTests();
