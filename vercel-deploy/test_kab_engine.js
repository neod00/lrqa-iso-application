/**
 * KAB-AR-MD5 업데이트된 핵심두뇌 테스트
 */

import { QuoteEngine } from './adj_quote_engine/adj_rules_v22.js';

// 테스트 데이터 - 다수사업장 사례 (본사-사업장 관계)
const testOrganization = {
  client_name: 'A회사 (본사-사업장)',
  sites: [
    {
      name: '울산본사',
      address: '울산광역시',
      standards: ['ISO14001'],
      regularEmployees: 40,      // 정규직 40명
      partTimeEmployees: 10,     // 파트타임 10명
      contractEmployees: 0,      // 계약직 0명
      dispatchedEmployees: 0,    // 파견직 0명
      shiftWorkers: 0,           // 교대근무 0명
      temporaryWorkers: 0,       // 임시직 0명
      seasonalWorkers: 0,        // 계절직 0명
      business_sector: '화학',
      business_description: '나프탈렌 생산',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: true       // 본사 표시
    },
    {
      name: '천안사업장',
      address: '천안시',
      standards: ['ISO14001'],
      regularEmployees: 90,      // 정규직 90명
      partTimeEmployees: 10,     // 비정규직 10명 (파트타임으로 간주)
      contractEmployees: 0,      // 계약직 0명
      dispatchedEmployees: 0,    // 파견직 0명
      shiftWorkers: 0,           // 교대근무 0명
      temporaryWorkers: 0,       // 임시직 0명
      seasonalWorkers: 0,        // 계절직 0명
      business_sector: '화학',
      business_description: '아세톤 생산',
      management_system_maturity: 'MEDIUM',
      isHeadquarters: false      // 사업장 표시
    }
  ],
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

async function testKABEngine() {
  console.log('=== KAB-AR-MD5 업데이트된 핵심두뇌 테스트 ===');
  
  const engine = new QuoteEngine();
  
  try {
    const result = await engine.calculate_quote(testOrganization);
    
    console.log('\n=== 테스트 결과 ===');
    console.log('회사명:', result.client_name);
    console.log('계산 기준:', result.calculation_standard);
    console.log('총 심사일수:', result.total_audit_days);
    console.log('총 비용:', result.total_cost.toLocaleString() + '원');
    
    console.log('\n=== ENP 계산 ===');
    console.log('총 ENP:', result.enp_calculation.total_enp);
    console.log('ENP 범위:', result.enp_calculation.site_details[0].enp_range);
    
    console.log('\n=== 복잡도 평가 ===');
    console.log('전체 복잡도:', result.complexity_assessment.overall_complexity);
    console.log('환경복잡도:', result.complexity_assessment.site_details[0].environmental_complexity);
    
    console.log('\n=== 단계별 심사일수 ===');
    console.log('Stage1:', result.stage_calculation.total_stage1 + '일');
    console.log('Stage2:', result.stage_calculation.total_stage2 + '일');
    console.log('사후관리:', result.stage_calculation.total_surveillance + '일');
    console.log('갱신심사:', result.stage_calculation.total_recert + '일');
    
    console.log('\n=== 사후관리심사 ===');
    console.log('심사일수:', result.surveillance.total_audit_days + '일');
    console.log('비용:', result.surveillance.total_cost.toLocaleString() + '원');
    
    console.log('\n=== 갱신심사 ===');
    console.log('심사일수:', result.recertification.total_audit_days + '일');
    console.log('비용:', result.recertification.total_cost.toLocaleString() + '원');
    
    console.log('\n=== 가정사항 ===');
    result.assumptions.forEach(assumption => {
      console.log(`- ${assumption.item}: ${assumption.description}`);
    });
    
    console.log('\n=== 상세 내역 ===');
    result.breakdowns.forEach(breakdown => {
      console.log(`${breakdown.site_name} (${breakdown.standard}):`);
      console.log(`  ENP: ${breakdown.enp}, 복잡도: ${breakdown.complexity}`);
      if (breakdown.environmental_complexity) {
        console.log(`  환경복잡도: ${breakdown.environmental_complexity}`);
      }
      console.log(`  EA 코드: ${breakdown.ea_code} (${breakdown.ea_name})`);
      console.log(`  매칭 키워드: ${breakdown.ea_matched_keyword}`);
      console.log(`  샘플링: ${breakdown.is_sampled ? '적용' : '미적용'} (${breakdown.sampling_type})`);
      if (breakdown.original_days) {
        console.log(`  원본 일수: ${breakdown.original_days}일`);
      }
      if (breakdown.reduction_rate) {
        console.log(`  감축률: ${(breakdown.reduction_rate * 100).toFixed(0)}%`);
      }
      console.log(`  Stage1: ${breakdown.stage1_days}일, Stage2: ${breakdown.stage2_days}일`);
      console.log(`  사후관리: ${breakdown.surveillance_days}일, 갱신: ${breakdown.recert_days}일`);
      console.log(`  비용: ${breakdown.cost.toLocaleString()}원`);
    });
    
    console.log('\n=== 테스트 완료 ===');
    
  } catch (error) {
    console.error('테스트 오류:', error);
  }
}

// 테스트 실행
testKABEngine();
