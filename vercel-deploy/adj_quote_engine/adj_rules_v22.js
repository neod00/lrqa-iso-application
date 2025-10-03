/**
 * ADJ v2.2 기반 견적 계산 엔진 (JavaScript 버전)
 * Python adj_rules_v22.py를 JavaScript로 변환
 */

export class QuoteEngine {
  constructor() {
    this.dayRate = 1300000; // 1일 1,300,000원
    this.vatRate = 0.1; // 10% 부가세
    this.travelExpenseRate = 0.1; // 제경비 10%
    
    // ADJ v2.2 규칙 테이블
    this.auditDaysTable = {
      'ISO9001': {
        'Low': { 'Stage1': 0.5, 'Stage2': 1, 'Surveillance': 0.5, 'Recert': 1 },
        'Medium': { 'Stage1': 1, 'Stage2': 2, 'Surveillance': 1, 'Recert': 2 },
        'High': { 'Stage1': 1.5, 'Stage2': 3, 'Surveillance': 1.5, 'Recert': 3 },
        'Very High': { 'Stage1': 2, 'Stage2': 4, 'Surveillance': 2, 'Recert': 4 }
      },
      'ISO14001': {
        'Low': { 'Stage1': 0.5, 'Stage2': 1, 'Surveillance': 0.5, 'Recert': 1 },
        'Medium': { 'Stage1': 1, 'Stage2': 2, 'Surveillance': 1, 'Recert': 2 },
        'High': { 'Stage1': 1.5, 'Stage2': 3, 'Surveillance': 1.5, 'Recert': 3 },
        'Very High': { 'Stage1': 2, 'Stage2': 4, 'Surveillance': 2, 'Recert': 4 }
      },
      'ISO45001': {
        'Low': { 'Stage1': 0.5, 'Stage2': 1, 'Surveillance': 0.5, 'Recert': 1 },
        'Medium': { 'Stage1': 1, 'Stage2': 2, 'Surveillance': 1, 'Recert': 2 },
        'High': { 'Stage1': 1.5, 'Stage2': 3, 'Surveillance': 1.5, 'Recert': 3 },
        'Very High': { 'Stage1': 2, 'Stage2': 4, 'Surveillance': 2, 'Recert': 4 }
      }
    };
  }

  /**
   * ENP(유효인원수) 계산
   * @param {Object} site - 사이트 정보
   * @returns {number} ENP 값
   */
  calculateENP(site) {
    const totalHeadcount = site.total_headcount || 0;
    const partTimeCount = site.part_time_count || 0;
    const contractorCount = site.contractor_count || 0;
    const shiftWorkers = site.shift_workers || 0;

    // ENP 계산 공식
    let enp = totalHeadcount;
    
    // 파트타임 직원 조정 (0.5배)
    enp += partTimeCount * 0.5;
    
    // 외주직원 조정 (0.3배)
    enp += contractorCount * 0.3;
    
    // 교대근무자 조정 (0.8배)
    enp += shiftWorkers * 0.8;

    return Math.max(1, Math.round(enp));
  }

  /**
   * 복잡도 평가
   * @param {Object} site - 사이트 정보
   * @param {string} standard - ISO 표준
   * @returns {string} 복잡도 레벨
   */
  assessComplexity(site, standard) {
    const enp = this.calculateENP(site);
    const businessSector = site.business_sector || 'MANUFACTURING';
    const maturity = site.management_system_maturity || 'MEDIUM';

    // ENP 기반 복잡도
    let complexity = 'Low';
    if (enp >= 1000) complexity = 'Very High';
    else if (enp >= 500) complexity = 'High';
    else if (enp >= 100) complexity = 'Medium';

    // 사업 분야별 조정
    if (businessSector === 'CHEMICAL' || businessSector === 'PHARMACEUTICAL') {
      if (complexity === 'Low') complexity = 'Medium';
      else if (complexity === 'Medium') complexity = 'High';
    }

    return complexity;
  }

  /**
   * 심사일수 계산
   * @param {Object} site - 사이트 정보
   * @param {string} standard - ISO 표준
   * @param {Object} options - 옵션
   * @returns {Object} 심사일수 정보
   */
  calculateAuditDays(site, standard, options) {
    const enp = this.calculateENP(site);
    const complexity = this.assessComplexity(site, standard);
    
    console.log(`ENP 계산: ${enp}, 복잡도: ${complexity}`);

    // 기본 심사일수 테이블에서 조회
    const baseDays = this.auditDaysTable[standard]?.[complexity] || 
                    this.auditDaysTable['ISO9001'][complexity];

    let stage1Days = baseDays.Stage1;
    let stage2Days = baseDays.Stage2;
    let surveillanceDays = baseDays.Surveillance;
    let recertDays = baseDays.Recert;

    // ENP에 따른 조정
    if (enp > 100) {
      const multiplier = Math.min(2.0, 1 + (enp - 100) / 200);
      stage1Days *= multiplier;
      stage2Days *= multiplier;
      surveillanceDays *= multiplier;
      recertDays *= multiplier;
    }

    // 통합심사 감축 (최대 15%)
    if (options.integrated_audit) {
      const reduction = Math.min(0.15, 0.05 + (enp / 1000) * 0.1);
      stage1Days *= (1 - reduction);
      stage2Days *= (1 - reduction);
      surveillanceDays *= (1 - reduction);
      recertDays *= (1 - reduction);
    }

    // 원격심사 감축 (최대 30%)
    if (options.remote_audit) {
      const reduction = Math.min(0.30, 0.1 + (enp / 500) * 0.2);
      stage1Days *= (1 - reduction);
      stage2Days *= (1 - reduction);
      surveillanceDays *= (1 - reduction);
      recertDays *= (1 - reduction);
    }

    return {
      stage1: Math.max(0.5, Math.round(stage1Days * 10) / 10),
      stage2: Math.max(1, Math.round(stage2Days * 10) / 10),
      surveillance: Math.max(0.5, Math.round(surveillanceDays * 10) / 10),
      recert: Math.max(1, Math.round(recertDays * 10) / 10)
    };
  }

  /**
   * 견적 계산 메인 함수
   * @param {Object} organization - 조직 정보
   * @returns {Object} 견적 결과
   */
  async calculate_quote(organization) {
    console.log('=== 핵심두뇌 견적 계산 시작 ===');
    console.log('조직 정보:', organization);

    const { client_name, sites, standards, options } = organization;
    
    let totalAuditDays = 0;
    let totalCost = 0;
    const breakdowns = [];
    const assumptions = [];

    // 각 사이트별 계산
    for (const site of sites) {
      console.log(`사이트 계산: ${site.name}`);
      
      for (const standard of standards) {
        console.log(`표준 계산: ${standard}`);
        
        const auditDays = this.calculateAuditDays(site, standard, options);
        const siteAuditDays = auditDays.stage1 + auditDays.stage2 + auditDays.surveillance;
        
        totalAuditDays += siteAuditDays;
        
        // 비용 계산
        const siteCost = siteAuditDays * this.dayRate;
        totalCost += siteCost;
        
        // 상세 내역
        breakdowns.push({
          site_name: site.name,
          standard: standard,
          enp: this.calculateENP(site),
          complexity: this.assessComplexity(site, standard),
          stage1_days: auditDays.stage1,
          stage2_days: auditDays.stage2,
          surveillance_days: auditDays.surveillance,
          recert_days: auditDays.recert,
          total_days: siteAuditDays,
          cost: siteCost
        });
      }
    }

    // 제경비 계산
    const travelExpense = totalCost * this.travelExpenseRate;
    const subtotal = totalCost + travelExpense;
    const vat = subtotal * this.vatRate;
    const finalTotal = subtotal + vat;

    // 가정사항
    assumptions.push({
      item: 'ENP 계산',
      description: '정규직 100%, 파트타임 50%, 외주 30%, 교대근무 80% 반영'
    });
    
    if (options.integrated_audit) {
      assumptions.push({
        item: '통합심사',
        description: '최대 15% 감축 적용'
      });
    }
    
    if (options.remote_audit) {
      assumptions.push({
        item: '원격심사',
        description: '최대 30% 감축 적용'
      });
    }

    const result = {
      client_name: client_name,
      total_audit_days: Math.round(totalAuditDays * 10) / 10,
      total_cost: Math.round(finalTotal),
      subtotal_cost: Math.round(subtotal),
      travel_expense: Math.round(travelExpense),
      vat: Math.round(vat),
      day_rate: this.dayRate,
      vat_rate: this.vatRate,
      breakdowns: breakdowns,
      assumptions: assumptions,
      enp_calculation: {
        total_enp: sites.reduce((sum, site) => sum + this.calculateENP(site), 0),
        site_details: sites.map(site => ({
          name: site.name,
          enp: this.calculateENP(site)
        }))
      },
      complexity_assessment: {
        overall_complexity: this.assessOverallComplexity(sites, standards),
        site_details: sites.map(site => ({
          name: site.name,
          complexity: standards.map(std => this.assessComplexity(site, std))
        }))
      },
      stage_calculation: {
        total_stage1: breakdowns.reduce((sum, b) => sum + b.stage1_days, 0),
        total_stage2: breakdowns.reduce((sum, b) => sum + b.stage2_days, 0),
        total_surveillance: breakdowns.reduce((sum, b) => sum + b.surveillance_days, 0),
        total_recert: breakdowns.reduce((sum, b) => sum + b.recert_days, 0)
      }
    };

    console.log('핵심두뇌 계산 완료:', result);
    return result;
  }

  /**
   * 전체 복잡도 평가
   * @param {Array} sites - 사이트 배열
   * @param {Array} standards - 표준 배열
   * @returns {string} 전체 복잡도
   */
  assessOverallComplexity(sites, standards) {
    const totalENP = sites.reduce((sum, site) => sum + this.calculateENP(site), 0);
    
    if (totalENP >= 2000) return 'Very High';
    if (totalENP >= 1000) return 'High';
    if (totalENP >= 500) return 'Medium';
    return 'Low';
  }
}
