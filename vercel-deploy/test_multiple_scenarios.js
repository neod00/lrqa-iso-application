/**
 * 다양한 사례 테스트 - 핵심두뇌 검증
 */

import { QuoteEngine } from './adj_quote_engine/adj_rules_v22.js';

// 테스트 사례 1: 단일사업장 (소규모)
const scenario1 = {
  client_name: 'B회사 (단일사업장 소규모)',
  sites: [{
    name: '서울공장',
    address: '서울특별시',
    standards: ['ISO9001'],
    regularEmployees: 15,
    partTimeEmployees: 5,
    contractEmployees: 0,
    dispatchedEmployees: 0,
    shiftWorkers: 0,
    temporaryWorkers: 0,
    seasonalWorkers: 0,
    business_sector: '제조업',
    business_description: '전자부품 제조',
    management_system_maturity: 'LOW'
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

// 테스트 사례 2: 다수사업장 (3개 사업장)
const scenario2 = {
  client_name: 'C회사 (다수사업장 3개)',
  sites: [
    {
      name: '부산본사',
      address: '부산광역시',
      standards: ['ISO14001', 'ISO45001'],
      regularEmployees: 200,
      partTimeEmployees: 20,
      contractEmployees: 10,
      dispatchedEmployees: 5,
      shiftWorkers: 15,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '화학',
      business_description: '플라스틱 제조',
      management_system_maturity: 'HIGH',
      isHeadquarters: true
    },
    {
      name: '대구사업장',
      address: '대구광역시',
      standards: ['ISO14001', 'ISO45001'],
      regularEmployees: 80,
      partTimeEmployees: 10,
      contractEmployees: 5,
      dispatchedEmployees: 2,
      shiftWorkers: 8,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '화학',
      business_description: '플라스틱 가공',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '광주사업장',
      address: '광주광역시',
      standards: ['ISO14001', 'ISO45001'],
      regularEmployees: 50,
      partTimeEmployees: 8,
      contractEmployees: 3,
      dispatchedEmployees: 1,
      shiftWorkers: 5,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '화학',
      business_description: '플라스틱 포장',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    }
  ],
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

// 테스트 사례 3: 대규모 단일사업장
const scenario3 = {
  client_name: 'D회사 (대규모 단일사업장)',
  sites: [{
    name: '인천공장',
    address: '인천광역시',
    standards: ['ISO9001', 'ISO14001', 'ISO45001'],
    regularEmployees: 500,
    partTimeEmployees: 50,
    contractEmployees: 30,
    dispatchedEmployees: 20,
    shiftWorkers: 100,
    temporaryWorkers: 15,
    seasonalWorkers: 10,
    business_sector: '자동차',
    business_description: '자동차 부품 제조',
    management_system_maturity: 'HIGH'
  }],
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

// 테스트 사례 4: 서비스업 다수사업장
const scenario4 = {
  client_name: 'E회사 (서비스업 다수사업장)',
  sites: [
    {
      name: '서울본사',
      address: '서울특별시',
      standards: ['ISO9001'],
      regularEmployees: 100,
      partTimeEmployees: 20,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: 'IT 컨설팅',
      management_system_maturity: 'HIGH',
      isHeadquarters: true
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
      business_description: 'IT 컨설팅',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '대구지사',
      address: '대구광역시',
      standards: ['ISO9001'],
      regularEmployees: 25,
      partTimeEmployees: 3,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: 'IT 컨설팅',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false
    },
    {
      name: '부산지사',
      address: '부산광역시',
      standards: ['ISO9001'],
      regularEmployees: 20,
      partTimeEmployees: 2,
      contractEmployees: 0,
      dispatchedEmployees: 0,
      shiftWorkers: 0,
      temporaryWorkers: 0,
      seasonalWorkers: 0,
      business_sector: '서비스업',
      business_description: 'IT 컨설팅',
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

// 테스트 사례 5: 복합업종 대규모 다수사업장
const scenario5 = {
  client_name: 'F회사 (복합업종 대규모)',
  sites: [
    {
      name: '수원본사',
      address: '수원시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 1000,
      partTimeEmployees: 100,
      contractEmployees: 50,
      dispatchedEmployees: 30,
      shiftWorkers: 200,
      temporaryWorkers: 25,
      seasonalWorkers: 15,
      business_sector: '제조업',
      business_description: '반도체 제조',
      management_system_maturity: 'HIGH',
      isHeadquarters: true
    },
    {
      name: '평택사업장',
      address: '평택시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 800,
      partTimeEmployees: 80,
      contractEmployees: 40,
      dispatchedEmployees: 25,
      shiftWorkers: 150,
      temporaryWorkers: 20,
      seasonalWorkers: 10,
      business_sector: '제조업',
      business_description: '반도체 패키징',
      management_system_maturity: 'HIGH',
      isHeadquarters: false
    },
    {
      name: '안산사업장',
      address: '안산시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 600,
      partTimeEmployees: 60,
      contractEmployees: 30,
      dispatchedEmployees: 20,
      shiftWorkers: 120,
      temporaryWorkers: 15,
      seasonalWorkers: 8,
      business_sector: '제조업',
      business_description: '반도체 테스트',
      management_system_maturity: 'HIGH',
      isHeadquarters: false
    },
    {
      name: '오창사업장',
      address: '오창읍',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 400,
      partTimeEmployees: 40,
      contractEmployees: 20,
      dispatchedEmployees: 15,
      shiftWorkers: 80,
      temporaryWorkers: 10,
      seasonalWorkers: 5,
      business_sector: '제조업',
      business_description: '반도체 조립',
      management_system_maturity: 'HIGH',
      isHeadquarters: false
    },
    {
      name: '구미사업장',
      address: '구미시',
      standards: ['ISO9001', 'ISO14001', 'ISO45001'],
      regularEmployees: 300,
      partTimeEmployees: 30,
      contractEmployees: 15,
      dispatchedEmployees: 10,
      shiftWorkers: 60,
      temporaryWorkers: 8,
      seasonalWorkers: 4,
      business_sector: '제조업',
      business_description: '반도체 검사',
      management_system_maturity: 'HIGH',
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

async function testScenario(scenario, scenarioNumber) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`테스트 사례 ${scenarioNumber}: ${scenario.client_name}`);
  console.log(`${'='.repeat(60)}`);
  
  const engine = new QuoteEngine();
  
  try {
    const result = await engine.calculate_quote(scenario);
    
    console.log(`\n📊 기본 정보:`);
    console.log(`- 사업장 수: ${scenario.sites.length}개`);
    console.log(`- 표준: ${scenario.standards.join(', ')}`);
    console.log(`- 통합심사: ${scenario.options.integrated_audit ? '적용' : '미적용'}`);
    console.log(`- 원격심사: ${scenario.options.remote_audit ? '적용' : '미적용'}`);
    
    console.log(`\n💰 견적 결과:`);
    console.log(`- 총 심사일수: ${result.total_audit_days}일`);
    console.log(`- 총 비용: ${result.total_cost.toLocaleString()}원`);
    
    console.log(`\n🏢 사업장별 상세:`);
    result.breakdowns.forEach((breakdown, index) => {
      console.log(`  ${index + 1}. ${breakdown.site_name}:`);
      console.log(`     - ENP: ${breakdown.enp}명, 복잡도: ${breakdown.complexity}`);
      console.log(`     - EA 코드: ${breakdown.ea_code} (${breakdown.ea_matched_keyword})`);
      console.log(`     - 샘플링: ${breakdown.is_sampled ? '적용' : '미적용'} (${breakdown.sampling_type})`);
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
    
    return {
      success: true,
      scenario: scenarioNumber,
      client_name: scenario.client_name,
      total_days: result.total_audit_days,
      total_cost: result.total_cost,
      sites_count: scenario.sites.length,
      standards: scenario.standards.length,
      breakdowns: result.breakdowns
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

async function runAllTests() {
  console.log('🧪 핵심두뇌 다양한 사례 테스트 시작');
  console.log('='.repeat(60));
  
  const scenarios = [scenario1, scenario2, scenario3, scenario4, scenario5];
  const results = [];
  
  for (let i = 0; i < scenarios.length; i++) {
    const result = await testScenario(scenarios[i], i + 1);
    results.push(result);
  }
  
  console.log(`\n${'='.repeat(60)}`);
  console.log('📈 테스트 결과 요약');
  console.log(`${'='.repeat(60)}`);
  
  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);
  
  console.log(`✅ 성공: ${successful.length}개`);
  console.log(`❌ 실패: ${failed.length}개`);
  
  if (successful.length > 0) {
    console.log(`\n📊 성공한 사례들:`);
    successful.forEach(result => {
      console.log(`  ${result.scenario}. ${result.client_name}: ${result.total_days}일, ${result.total_cost.toLocaleString()}원`);
    });
  }
  
  if (failed.length > 0) {
    console.log(`\n❌ 실패한 사례들:`);
    failed.forEach(result => {
      console.log(`  ${result.scenario}. ${result.client_name}: ${result.error}`);
    });
  }
  
  console.log(`\n🎯 테스트 완료!`);
}

// 테스트 실행
runAllTests();
