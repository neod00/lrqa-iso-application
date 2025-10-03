/**
 * ADJ v2.2 기반 견적 계산 엔진 (JavaScript 버전)
 * Python adj_rules_v22.py를 JavaScript로 변환
 */

export class QuoteEngine {
  constructor() {
    this.dayRate = 1300000; // 1일 1,300,000원
    this.vatRate = 0.1; // 10% 부가세
    this.travelExpenseRate = 0.1; // 제경비 10%
    
    // KAB-AR-MD5 기준 심사일수 테이블
    this.auditDaysTable = {
      'ISO9001': {
        '1-5': 1.5,
        '6-10': 2,
        '11-15': 2.5,
        '16-25': 3,
        '26-45': 4,
        '46-65': 5,
        '66-85': 6,
        '86-125': 7,
        '126-175': 8,
        '176-275': 9,
        '276-425': 10,
        '426-625': 11,
        '626-875': 12,
        '876-1175': 13,
        '1176-1550': 14,
        '1551-2025': 15,
        '2026-2675': 16,
        '2676-3450': 17,
        '3451-4350': 18,
        '4351-5450': 19,
        '5451-6800': 20,
        '6801-8500': 21,
        '8501-10700': 22
      },
      'ISO14001': {
        'High': {
          '1-5': 3, '6-10': 3.5, '11-15': 4.5, '16-25': 5.5, '26-45': 7,
          '46-65': 8, '66-85': 9, '86-125': 11, '126-175': 12, '176-275': 13,
          '276-425': 15, '426-625': 16, '626-875': 17, '876-1175': 19,
          '1176-1550': 20, '1551-2025': 21, '2026-2675': 23, '2676-3450': 25,
          '3451-4350': 27, '4351-5450': 28, '5451-6800': 30, '6801-8500': 32,
          '8501-10700': 34
        },
        'Medium': {
          '1-5': 2.5, '6-10': 3, '11-15': 3.5, '16-25': 4.5, '26-45': 5.5,
          '46-65': 6, '66-85': 7, '86-125': 8, '126-175': 9, '176-275': 10,
          '276-425': 11, '426-625': 12, '626-875': 13, '876-1175': 15,
          '1176-1550': 16, '1551-2025': 17, '2026-2675': 18, '2676-3450': 19,
          '3451-4350': 20, '4351-5450': 21, '5451-6800': 23, '6801-8500': 25,
          '8501-10700': 27
        },
        'Low': {
          '1-5': 2.5, '6-10': 3, '11-15': 3, '16-25': 3.5, '26-45': 4,
          '46-65': 4.5, '66-85': 5, '86-125': 5.5, '126-175': 6, '176-275': 7,
          '276-425': 8, '426-625': 9, '626-875': 10, '876-1175': 11,
          '1176-1550': 12, '1551-2025': 12, '2026-2675': 13, '2676-3450': 14,
          '3451-4350': 15, '4351-5450': 16, '5451-6800': 17, '6801-8500': 19,
          '8501-10700': 20
        },
        'Limited': {
          '1-5': 2.5, '6-10': 3, '11-15': 3, '16-25': 3, '26-45': 3,
          '46-65': 3.5, '66-85': 3.5, '86-125': 4, '126-175': 4.5, '176-275': 5,
          '276-425': 5.5, '426-625': 6, '626-875': 6.5, '876-1175': 7,
          '1176-1550': 7.5, '1551-2025': 8, '2026-2675': 8.5, '2676-3450': 9,
          '3451-4350': 10, '4351-5450': 11, '5451-6800': 12, '6801-8500': 13,
          '8501-10700': 14
        }
      },
      'ISO45001': {
        'High': {
          '1-5': 3, '6-10': 3.5, '11-15': 4.5, '16-25': 5.5, '26-45': 7,
          '46-65': 8, '66-85': 9, '86-125': 11, '126-175': 12, '176-275': 13,
          '276-425': 15, '426-625': 16, '626-875': 17, '876-1175': 19,
          '1176-1550': 20, '1551-2025': 21, '2026-2675': 23, '2676-3450': 25,
          '3451-4350': 27, '4351-5450': 28, '5451-6800': 30, '6801-8500': 32,
          '8501-10700': 34
        },
        'Medium': {
          '1-5': 2.5, '6-10': 3, '11-15': 3.5, '16-25': 4.5, '26-45': 5.5,
          '46-65': 6, '66-85': 7, '86-125': 8, '126-175': 9, '176-275': 10,
          '276-425': 11, '426-625': 12, '626-875': 13, '876-1175': 15,
          '1176-1550': 16, '1551-2025': 17, '2026-2675': 18, '2676-3450': 19,
          '3451-4350': 20, '4351-5450': 21, '5451-6800': 23, '6801-8500': 25,
          '8501-10700': 27
        },
        'Low': {
          '1-5': 2.5, '6-10': 3, '11-15': 3, '16-25': 3.5, '26-45': 4,
          '46-65': 4.5, '66-85': 5, '86-125': 5.5, '126-175': 6, '176-275': 7,
          '276-425': 8, '426-625': 9, '626-875': 10, '876-1175': 11,
          '1176-1550': 12, '1551-2025': 12, '2026-2675': 13, '2676-3450': 14,
          '3451-4350': 15, '4351-5450': 16, '5451-6800': 17, '6801-8500': 19,
          '8501-10700': 20
        }
      }
    };

    // 환경복잡도 분류 (KAB-AR-MD5 기준)
    this.environmentalComplexity = {
      'High': [
        '광업', '채석업', '석유', '가스', '무두질', '종이제조', '석유정제',
        '화학', '의약품', '금속제련', '비금속제련', '석탄발전', '건설',
        '폐기물처리', '하수처리'
      ],
      'Medium': [
        '농업', '어업', '임업', '섬유', '의류', '목재', '식품', '음료',
        '고무', '플라스틱', '전력', '가스', '운송', '창고', '숙박',
        '음식', '정보통신', '금융', '보험', '부동산', '전문서비스',
        '행정', '교육', '보건', '사회복지', '예술', '스포츠', '여가'
      ],
      'Low': [
        '소매', '도매', '수리', '개인서비스'
      ],
      'Limited': [
        '사무서비스', 'IT서비스', '컨설팅', '연구개발'
      ]
    };

    // EA 코드 분류 (New Code Maps 기준)
    this.eaCodeMapping = {
      'EA1': { name: 'Agriculture, forestry and fishing', keywords: ['농업', '어업', '임업', '농림', '수산'] },
      'EA2': { name: 'Mining and quarrying', keywords: ['광업', '채석', '채굴', '광산'] },
      'EA3': { name: 'Food products, beverages and tobacco', keywords: ['식품', '음료', '담배', '식품제조', '음식'] },
      'EA4': { name: 'Textiles and textile products', keywords: ['섬유', '의류', '직물', '텍스타일'] },
      'EA5': { name: 'Leather and leather products', keywords: ['가죽', '무두질', '가죽제품'] },
      'EA6': { name: 'Wood and wood products', keywords: ['목재', '나무', '가구', '목제품'] },
      'EA7': { name: 'Pulp, paper and paper products', keywords: ['종이', '펄프', '제지', '종이제조'] },
      'EA8': { name: 'Publishing companies', keywords: ['출판', '출판사', '도서', '매체'] },
      'EA9': { name: 'Printing companies', keywords: ['인쇄', '인쇄소', '프린팅'] },
      'EA10': { name: 'Manufacture of coke and refined petroleum products', keywords: ['석유', '정제', '코크스', '석유정제', '석유화학'] },
      'EA11': { name: 'Nuclear fuel', keywords: ['핵연료', '원자력', '핵'] },
      'EA12': { name: 'Chemicals, chemical products and fibres', keywords: ['화학', '화학물질', '화학제품', '섬유', '나프탈렌', '벤젠', '톨루엔', '아세톤', 'acetone'] },
      'EA13': { name: 'Pharmaceuticals', keywords: ['의약품', '제약', '약품', '의료'] },
      'EA14': { name: 'Rubber and plastic products', keywords: ['고무', '플라스틱', '합성수지', '고무제품'] },
      'EA15': { name: 'Non-metallic mineral products', keywords: ['비금속', '세라믹', '유리', '시멘트'] },
      'EA16': { name: 'Concrete, cement, lime, plaster etc', keywords: ['콘크리트', '시멘트', '석회', '석고'] },
      'EA17': { name: 'Basic metals and fabricated metal products', keywords: ['금속', '철강', '금속제품', '금속가공'] },
      'EA18': { name: 'Machinery and equipment', keywords: ['기계', '장비', '기계제조', '설비'] },
      'EA19': { name: 'Electrical and optical equipment', keywords: ['전기', '전자', '광학', '전기제품', '전자제품'] },
      'EA20': { name: 'Shipbuilding', keywords: ['조선', '선박', '조선업'] },
      'EA21': { name: 'Aerospace', keywords: ['항공', '우주', '항공우주', '항공기'] },
      'EA22': { name: 'Other transport equipment', keywords: ['자동차', '운송장비', '교통수단'] },
      'EA23': { name: 'Manufacturing not elsewhere classified', keywords: ['기타제조', '기타제조업'] },
      'EA24': { name: 'Recycling', keywords: ['재활용', '리사이클', '폐기물처리'] },
      'EA25': { name: 'Electricity supply', keywords: ['전력', '전기공급', '발전'] },
      'EA26': { name: 'Gas supply', keywords: ['가스', '가스공급', '가스사업'] },
      'EA27': { name: 'Water supply', keywords: ['상수도', '수도', '물공급', '하수처리'] },
      'EA28': { name: 'Construction', keywords: ['건설', '건축', '토목', '건설업'] },
      'EA29': { name: 'Wholesale and retail trade', keywords: ['도매', '소매', '유통', '판매'] },
      'EA30': { name: 'Hotels and restaurants', keywords: ['호텔', '숙박', '음식', '레스토랑'] },
      'EA31': { name: 'Transport, storage and communication', keywords: ['운송', '창고', '통신', '물류'] },
      'EA32': { name: 'Financial intermediation', keywords: ['금융', '보험', '부동산', '금융업'] },
      'EA33': { name: 'Information technology', keywords: ['정보기술', 'IT', '소프트웨어', '컴퓨터', '컨설팅', 'consulting', '프로그래밍', 'programming'] },
      'EA34': { name: 'Engineering services', keywords: ['엔지니어링', '기술서비스', '컨설팅', '연구개발'] },
      'EA35': { name: 'Other services', keywords: ['기타서비스', '서비스업'] },
      'EA36': { name: 'Public administration', keywords: ['공공행정', '정부', '행정'] },
      'EA37': { name: 'Education', keywords: ['교육', '학교', '교육기관'] },
      'EA38': { name: 'Health and social work', keywords: ['보건', '의료', '사회복지', '건강'] },
      'EA39': { name: 'Other social services', keywords: ['기타사회서비스', '사회서비스'] },
      // 반도체 관련 추가
      'EA40': { name: 'Semiconductors and electronic components', keywords: ['반도체', 'semiconductor', '칩', 'chip', '웨이퍼', 'wafer', '패키징', 'packaging', '테스트', 'test', '조립', 'assembly', '검사', 'inspection'] }
    };
  }

  /**
   * ENP(유효인원수) 계산 - KAB-AR-MD5 기준
   * @param {Object} site - 사이트 정보
   * @returns {number} ENP 값
   */
  calculateENP(site) {
    const {
      regularEmployees = 0,      // 정규직
      partTimeEmployees = 0,     // 파트타임직
      contractEmployees = 0,     // 계약직
      dispatchedEmployees = 0,   // 파견직
      shiftWorkers = 0,          // 교대근무자
      temporaryWorkers = 0,      // 임시직
      seasonalWorkers = 0,       // 계절직
      // 기존 호환성을 위한 fallback
      total_headcount = 0,
      part_time_count = 0,
      contractor_count = 0,
      shift_workers = 0
    } = site;

    // KAB-AR-MD5 기준 ENP 계산
    let enp = regularEmployees || total_headcount;
    
    // 한국 고용 형태별 가중치 (KAB-AR-MD5 기준)
    enp += (partTimeEmployees || part_time_count) * 0.5;     // 파트타임 50%
    enp += (contractEmployees || contractor_count) * 0.7;    // 계약직 70%
    enp += dispatchedEmployees * 0.3;                        // 파견직 30%
    enp += (shiftWorkers || shift_workers) * 0.8;            // 교대근무 80%
    enp += temporaryWorkers * 0.4;                           // 임시직 40%
    enp += seasonalWorkers * 0.3;                            // 계절직 30%

    return Math.max(1, Math.round(enp));
  }

  /**
   * 환경복잡도 평가 (KAB-AR-MD5 기준)
   * @param {Object} site - 사이트 정보
   * @returns {string} 환경복잡도 레벨
   */
  assessEnvironmentalComplexity(site) {
    const businessSector = site.business_sector || site.businessSector || 'MANUFACTURING';
    const businessDescription = site.business_description || '';
    
    // 사업 분야와 설명을 종합하여 환경복잡도 평가
    const searchText = `${businessSector} ${businessDescription}`.toLowerCase();
    
    for (const [level, keywords] of Object.entries(this.environmentalComplexity)) {
      for (const keyword of keywords) {
        if (searchText.includes(keyword.toLowerCase())) {
          return level;
        }
      }
    }
    
    // 기본값: Medium
    return 'Medium';
  }

  /**
   * EA 코드 자동 분류 (New Code Maps 기준)
   * @param {Object} site - 사이트 정보
   * @returns {Object} EA 코드 정보
   */
  getEACode(site) {
    const businessDescription = (site.business_description || '').toLowerCase();
    const businessSector = (site.business_sector || site.businessSector || '').toLowerCase();
    const searchText = `${businessDescription} ${businessSector}`.toLowerCase();
    
    // 키워드 매칭으로 EA 코드 찾기
    for (const [code, info] of Object.entries(this.eaCodeMapping)) {
      for (const keyword of info.keywords) {
        if (searchText.includes(keyword.toLowerCase())) {
          return {
            code: code,
            name: info.name,
            matched_keyword: keyword
          };
        }
      }
    }
    
    // 기본값: EA35 (Other services)
    return {
      code: 'EA35',
      name: 'Other services',
      matched_keyword: '기본값'
    };
  }

  /**
   * 복잡도 평가 (KAB-AR-MD5 기준)
   * @param {Object} site - 사이트 정보
   * @param {string} standard - ISO 표준
   * @returns {string} 복잡도 레벨
   */
  assessComplexity(site, standard) {
    const enp = this.calculateENP(site);
    const businessSector = site.business_sector || site.businessSector || 'MANUFACTURING';
    const maturity = site.management_system_maturity || 'MEDIUM';

    // QMS: 리스크 기반 복잡도
    if (standard === 'ISO9001') {
      let complexity = 'Low';
      if (enp >= 1000) complexity = 'High';
      else if (enp >= 500) complexity = 'Medium';
      
      // 고위험 업종 조정
      if (businessSector === 'CHEMICAL' || businessSector === 'PHARMACEUTICAL' || 
          businessSector === 'AEROSPACE' || businessSector === 'AUTOMOTIVE') {
        if (complexity === 'Low') complexity = 'Medium';
        else if (complexity === 'Medium') complexity = 'High';
      }
      
      return complexity;
    }
    
    // EMS: 환경복잡도 기반
    if (standard === 'ISO14001') {
      return this.assessEnvironmentalComplexity(site);
    }
    
    // OH&SMS: 안전보건위험 기반
    if (standard === 'ISO45001') {
      let complexity = 'Low';
      if (enp >= 1000) complexity = 'High';
      else if (enp >= 500) complexity = 'Medium';
      
      // 고위험 업종 조정
      if (businessSector === 'CONSTRUCTION' || businessSector === 'MINING' || 
          businessSector === 'CHEMICAL' || businessSector === 'MANUFACTURING') {
        if (complexity === 'Low') complexity = 'Medium';
        else if (complexity === 'Medium') complexity = 'High';
      }
      
      return complexity;
    }

    // 기본값
    return 'Medium';
  }

  /**
   * ENP 범위 찾기
   * @param {number} enp - 유효인원수
   * @returns {string} ENP 범위
   */
  getENPRange(enp) {
    if (enp <= 5) return '1-5';
    if (enp <= 10) return '6-10';
    if (enp <= 15) return '11-15';
    if (enp <= 25) return '16-25';
    if (enp <= 45) return '26-45';
    if (enp <= 65) return '46-65';
    if (enp <= 85) return '66-85';
    if (enp <= 125) return '86-125';
    if (enp <= 175) return '126-175';
    if (enp <= 275) return '176-275';
    if (enp <= 425) return '276-425';
    if (enp <= 625) return '426-625';
    if (enp <= 875) return '626-875';
    if (enp <= 1175) return '876-1175';
    if (enp <= 1550) return '1176-1550';
    if (enp <= 2025) return '1551-2025';
    if (enp <= 2675) return '2026-2675';
    if (enp <= 3450) return '2676-3450';
    if (enp <= 4350) return '3451-4350';
    if (enp <= 5450) return '4351-5450';
    if (enp <= 6800) return '5451-6800';
    if (enp <= 8500) return '6801-8500';
    if (enp <= 10700) return '8501-10700';
    return '8501-10700'; // 10700명 초과시 기본값
  }

  /**
   * 심사일수 0.5일 단위 사사오입 (KAB-AR-MD5 2.2.3 기준)
   * @param {number} days - 원본 일수
   * @returns {number} 0.5일 단위로 사사오입된 일수
   */
  roundToHalfDay(days) {
    // 소수점 둘째자리에서 사사오입하여 0.5일 단위로 조정
    const rounded = Math.round(days * 2) / 2;
    return Math.max(0.5, rounded); // 최소 0.5일
  }

  /**
   * 다수사업장 샘플링 사업장 수 계산 (IAF MD1 Issue 3 기준)
   * @param {number} totalSites - 전체 사업장 수
   * @param {string} auditType - 심사 유형 (initial/surveillance/recertification)
   * @returns {number} 샘플링할 사업장 수
   */
  calculateSamplingSize(totalSites, auditType) {
    if (totalSites <= 1) return totalSites;
    
    switch (auditType) {
      case 'initial':
        return Math.ceil(Math.sqrt(totalSites));
      case 'surveillance':
        return Math.ceil(0.6 * Math.sqrt(totalSites));
      case 'recertification':
        return Math.ceil(Math.sqrt(totalSites));
      default:
        return totalSites;
    }
  }

  /**
   * 본사-사업장 관계 확인
   * @param {Array} sites - 사업장 배열
   * @returns {Object} 본사-사업장 관계 정보
   */
  identifyHeadquartersBranch(sites) {
    if (sites.length <= 1) {
      return { isMultiSite: false, headquarters: sites[0], branches: [] };
    }

    // 본사 식별 로직 (가장 큰 ENP 또는 '본사' 키워드 포함)
    const headquarters = sites.find(site => 
      site.name.includes('본사') || 
      site.name.includes('Headquarters') ||
      site.name.includes('Head Office') ||
      site.isHeadquarters === true
    ) || sites.reduce((max, site) => 
      this.calculateENP(site) > this.calculateENP(max) ? site : max
    );

    const branches = sites.filter(site => site !== headquarters);

    return {
      isMultiSite: true,
      headquarters: headquarters,
      branches: branches,
      totalSites: sites.length
    };
  }

  /**
   * 샘플링 사업장 선택 (IAF MD1 기준: 25% 무작위 + 75% 대표성)
   * @param {Array} branches - 사업장 배열
   * @param {number} samplingSize - 샘플링할 사업장 수
   * @returns {Array} 선택된 사업장 배열
   */
  selectSamplingSites(branches, samplingSize) {
    if (branches.length <= samplingSize) {
      return branches;
    }

    // 25% 무작위 선택
    const randomCount = Math.max(1, Math.ceil(samplingSize * 0.25));
    const randomSites = this.shuffleArray([...branches]).slice(0, randomCount);
    
    // 나머지는 대표성 고려하여 선택 (ENP 기준)
    const remainingCount = samplingSize - randomCount;
    const remainingSites = branches.filter(site => !randomSites.includes(site));
    
    // ENP 기준으로 정렬하여 대표성 확보
    const sortedSites = remainingSites.sort((a, b) => 
      this.calculateENP(b) - this.calculateENP(a)
    );
    
    const selectedSites = sortedSites.slice(0, remainingCount);
    
    return [...randomSites, ...selectedSites];
  }

  /**
   * 배열 셔플 (Fisher-Yates 알고리즘)
   * @param {Array} array - 셔플할 배열
   * @returns {Array} 셔플된 배열
   */
  shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * 다수사업장 샘플링 적용
   * @param {Object} site - 사업장 정보
   * @param {string} auditType - 심사 유형
   * @param {boolean} isHeadquarters - 본사 여부
   * @param {Object} samplingInfo - 샘플링 정보
   * @returns {Object} 샘플링 적용된 심사일수
   */
  applyMultiSiteSampling(site, auditType, isHeadquarters, samplingInfo) {
    const auditDays = this.calculateAuditDays(site, site.standards[0], { stage1: true, stage2: true });
    
    // 본사는 항상 전체 심사일수 적용
    if (isHeadquarters) {
      return {
        ...auditDays,
        isSampled: true,
        samplingType: 'headquarters',
        originalDays: auditDays.stage1 + auditDays.stage2
      };
    }

    // 사업장은 샘플링 적용
    const isSampled = samplingInfo.sampledSites.includes(site.name);
    
    if (!isSampled) {
      return {
        ...auditDays,
        isSampled: false,
        samplingType: 'not_selected',
        originalDays: auditDays.stage1 + auditDays.stage2,
        stage1: 0,
        stage2: 0,
        surveillance: 0,
        recert: 0
      };
    }

    // 샘플링된 사업장은 최대 50% 감축 적용 (LRMS 기준)
    const reductionRate = 0.5; // 최대 50% 감축
    const reducedStage1 = this.roundToHalfDay(auditDays.stage1 * (1 - reductionRate));
    const reducedStage2 = this.roundToHalfDay(auditDays.stage2 * (1 - reductionRate));
    const reducedSurveillance = this.roundToHalfDay(auditDays.surveillance * (1 - reductionRate));
    const reducedRecert = this.roundToHalfDay(auditDays.recert * (1 - reductionRate));

    return {
      stage1: reducedStage1,
      stage2: reducedStage2,
      surveillance: reducedSurveillance,
      recert: reducedRecert,
      isSampled: true,
      samplingType: 'sampled',
      originalDays: auditDays.stage1 + auditDays.stage2,
      reductionRate: reductionRate
    };
  }

  /**
   * 심사일수 계산 (KAB-AR-MD5 기준)
   * @param {Object} site - 사이트 정보
   * @param {string} standard - ISO 표준
   * @param {Object} options - 옵션
   * @returns {Object} 심사일수 정보
   */
  calculateAuditDays(site, standard, options) {
    const enp = this.calculateENP(site);
    const complexity = this.assessComplexity(site, standard);
    const enpRange = this.getENPRange(enp);
    
    console.log(`ENP 계산: ${enp}, 범위: ${enpRange}, 복잡도: ${complexity}`);

    // KAB-AR-MD5 기준 심사일수 조회
    let totalDays = 0;
    
    if (standard === 'ISO9001') {
      // QMS: 단순 테이블
      totalDays = this.auditDaysTable[standard][enpRange] || 1.5;
    } else if (standard === 'ISO14001') {
      // EMS: 복잡도별 테이블
      const complexityTable = this.auditDaysTable[standard][complexity];
      totalDays = complexityTable ? complexityTable[enpRange] : 2.5;
    } else if (standard === 'ISO45001') {
      // OH&SMS: 복잡도별 테이블
      const complexityTable = this.auditDaysTable[standard][complexity];
      totalDays = complexityTable ? complexityTable[enpRange] : 2.5;
    } else {
      // 기본값
      totalDays = 2.5;
    }

    // Stage별 분배 (KAB-AR-MD5 기준)
    let stage1Days, stage2Days, surveillanceDays, recertDays;
    
    if (totalDays <= 2) {
      stage1Days = 0.5;
      stage2Days = this.roundToHalfDay(totalDays - 0.5);
    } else if (totalDays <= 4) {
      stage1Days = 1;
      stage2Days = this.roundToHalfDay(totalDays - 1);
    } else {
      stage1Days = this.roundToHalfDay(totalDays * 0.3); // 30%를 0.5일 단위로 사사오입
      stage2Days = this.roundToHalfDay(totalDays - stage1Days);
    }
    
    // 사후관리: 최초심사의 1/3 (연간)
    surveillanceDays = this.roundToHalfDay(totalDays * 0.33);
    
    // 갱신심사는 별도 함수에서 계산 (IAF MD5: 최초심사의 2/3)
    recertDays = 0;

    // 통합심사 감축 (최대 20%)
    if (options.integrated_audit) {
      const reduction = Math.min(0.20, 0.05 + (enp / 1000) * 0.15);
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
      stage1: Math.max(0.5, Math.round(stage1Days * 2) / 2),
      stage2: Math.max(1, Math.round(stage2Days * 2) / 2),
      surveillance: Math.max(0.5, Math.round(surveillanceDays * 2) / 2),
      recert: Math.max(1, Math.round(recertDays * 2) / 2),
      total: totalDays
    };
  }

  /**
   * 사후관리심사 계산 (KAB-AR-MD5 기준)
   * @param {Object} organization - 조직 정보
   * @returns {Object} 사후관리심사 결과
   */
  calculateSurveillance(organization) {
    const { client_name, sites, standards, options } = organization;
    
    let totalSurveillanceDays = 0;
    let totalCost = 0;
    const breakdowns = [];

    for (const site of sites) {
      for (const standard of standards) {
        const auditDays = this.calculateAuditDays(site, standard, options);
        const surveillanceDays = auditDays.surveillance;
        
        totalSurveillanceDays += surveillanceDays;
        
        const siteCost = surveillanceDays * this.dayRate;
        totalCost += siteCost;
        
        breakdowns.push({
          site_name: site.name,
          standard: standard,
          enp: this.calculateENP(site),
          complexity: this.assessComplexity(site, standard),
          surveillance_days: surveillanceDays,
          cost: siteCost
        });
      }
    }

    const travelExpense = totalCost * this.travelExpenseRate;
    const subtotal = totalCost + travelExpense;
    const vat = subtotal * this.vatRate;
    const finalTotal = subtotal + vat;

    return {
      client_name: client_name,
      audit_type: 'Surveillance',
      total_audit_days: Math.round(totalSurveillanceDays * 10) / 10,
      total_cost: Math.round(finalTotal),
      breakdowns: breakdowns
    };
  }

  /**
   * 갱신심사 계산 (KAB-AR-MD5 기준)
   * @param {Object} organization - 조직 정보
   * @returns {Object} 갱신심사 결과
   */
  calculateRecertification(organization) {
    const { client_name, sites, standards, options } = organization;
    
    let totalRecertDays = 0;
    let totalCost = 0;
    const breakdowns = [];

    for (const site of sites) {
      for (const standard of standards) {
        const auditDays = this.calculateAuditDays(site, standard, options);
        const initialDays = auditDays.stage1 + auditDays.stage2;
        const recertDays = this.roundToHalfDay(initialDays * 2/3); // IAF MD5: 최초심사의 2/3, 0.5일 단위 사사오입
        
        totalRecertDays += recertDays;
        
        const siteCost = recertDays * this.dayRate;
        totalCost += siteCost;
        
        breakdowns.push({
          site_name: site.name,
          standard: standard,
          enp: this.calculateENP(site),
          complexity: this.assessComplexity(site, standard),
          initial_days: initialDays,
          recert_days: recertDays,
          cost: siteCost
        });
      }
    }

    const travelExpense = totalCost * this.travelExpenseRate;
    const subtotal = totalCost + travelExpense;
    const vat = subtotal * this.vatRate;
    const finalTotal = subtotal + vat;

    return {
      client_name: client_name,
      audit_type: 'Recertification',
      total_audit_days: Math.round(totalRecertDays * 10) / 10,
      total_cost: Math.round(finalTotal),
      breakdowns: breakdowns
    };
  }

  /**
   * 견적 계산 메인 함수 (KAB-AR-MD5 + 다수사업장 샘플링 기준)
   * @param {Object} organization - 조직 정보
   * @returns {Object} 견적 결과
   */
  async calculate_quote(organization) {
    console.log('=== 핵심두뇌 견적 계산 시작 (KAB-AR-MD5 + 다수사업장 샘플링 기준) ===');
    console.log('조직 정보:', organization);

    const { client_name, sites, standards, options } = organization;
    
    let totalAuditDays = 0;
    let totalCost = 0;
    const breakdowns = [];
    const assumptions = [];

    // 다수사업장 샘플링 적용 여부 확인
    const multiSiteInfo = this.identifyHeadquartersBranch(sites);
    const isMultiSite = multiSiteInfo.isMultiSite && sites.length > 1;

    if (isMultiSite) {
      console.log('다수사업장 샘플링 적용:', multiSiteInfo);
      
      // 샘플링 사업장 수 계산 (본사 제외한 사업장만 계산)
      const branchSamplingSize = this.calculateSamplingSize(multiSiteInfo.branches.length, 'initial');
      const sampledSites = this.selectSamplingSites(multiSiteInfo.branches, branchSamplingSize);
      
      const samplingInfo = {
        isApplied: true,
        totalSites: sites.length,
        samplingSize: 1 + branchSamplingSize, // 본사 + 선택된 사업장 수
        sampledSites: sampledSites.map(site => site.name)
      };

      // 각 사이트별 계산 (샘플링 적용)
      for (const site of sites) {
        console.log(`사이트 계산 (샘플링): ${site.name}`);
        
        for (const standard of standards) {
          console.log(`표준 계산: ${standard}`);
          
          const isHeadquarters = site === multiSiteInfo.headquarters;
          const samplingResult = this.applyMultiSiteSampling(site, 'initial', isHeadquarters, samplingInfo);
          
          const siteAuditDays = samplingResult.stage1 + samplingResult.stage2;
          totalAuditDays += siteAuditDays;
          
          // 비용 계산
          const siteCost = siteAuditDays * this.dayRate;
          totalCost += siteCost;
          
          // EA 코드 분류
          const eaCode = this.getEACode(site);
          
          // 상세 내역
          breakdowns.push({
            site_name: site.name,
            standard: standard,
            enp: this.calculateENP(site),
            complexity: this.assessComplexity(site, standard),
            environmental_complexity: standard === 'ISO14001' ? this.assessEnvironmentalComplexity(site) : null,
            ea_code: eaCode.code,
            ea_name: eaCode.name,
            ea_matched_keyword: eaCode.matched_keyword,
            stage1_days: samplingResult.stage1,
            stage2_days: samplingResult.stage2,
            surveillance_days: samplingResult.surveillance,
            recert_days: samplingResult.recert,
            total_days: siteAuditDays,
            cost: siteCost,
            is_sampled: samplingResult.isSampled,
            sampling_type: samplingResult.samplingType,
            original_days: samplingResult.originalDays,
            reduction_rate: samplingResult.reductionRate || 0
          });
        }
      }

      // 다수사업장 샘플링 가정사항 추가
      assumptions.push({
        item: '다수사업장 샘플링',
        description: `IAF MD1 기준: ${sites.length}개 사업장 중 ${1 + branchSamplingSize}개 샘플링 (본사 포함)`
      });
      
      assumptions.push({
        item: '사업장 감축',
        description: 'LRMS 기준: 샘플링된 사업장 최대 50% 감축 적용'
      });

    } else {
      // 단일사업장 또는 샘플링 미적용
      console.log('단일사업장 또는 샘플링 미적용');
      
      // 각 사이트별 계산 (기존 방식)
      for (const site of sites) {
        console.log(`사이트 계산: ${site.name}`);
        
        for (const standard of standards) {
          console.log(`표준 계산: ${standard}`);
          
          const auditDays = this.calculateAuditDays(site, standard, options);
          const siteAuditDays = auditDays.stage1 + auditDays.stage2;
          
          totalAuditDays += siteAuditDays;
          
          // 비용 계산
          const siteCost = siteAuditDays * this.dayRate;
          totalCost += siteCost;
          
          // EA 코드 분류
          const eaCode = this.getEACode(site);
          
          // 상세 내역
          breakdowns.push({
            site_name: site.name,
            standard: standard,
            enp: this.calculateENP(site),
            complexity: this.assessComplexity(site, standard),
            environmental_complexity: standard === 'ISO14001' ? this.assessEnvironmentalComplexity(site) : null,
            ea_code: eaCode.code,
            ea_name: eaCode.name,
            ea_matched_keyword: eaCode.matched_keyword,
            stage1_days: auditDays.stage1,
            stage2_days: auditDays.stage2,
            surveillance_days: auditDays.surveillance,
            recert_days: auditDays.recert,
            total_days: siteAuditDays,
            cost: siteCost,
            is_sampled: true,
            sampling_type: 'single_site'
          });
        }
      }
    }

    // 제경비 계산
    const travelExpense = totalCost * this.travelExpenseRate;
    const subtotal = totalCost + travelExpense;
    const vat = subtotal * this.vatRate;
    const finalTotal = subtotal + vat;

    // 가정사항 (KAB-AR-MD5 기준)
    assumptions.push({
      item: 'ENP 계산 (KAB-AR-MD5)',
      description: '정규직 100%, 파트타임 50%, 계약직 70%, 파견직 30%, 교대근무 80%, 임시직 40%, 계절직 30% 반영'
    });
    
    assumptions.push({
      item: '심사일수 기준',
      description: 'KAB-AR-MD5 기준 심사일수 테이블 적용'
    });
    
    assumptions.push({
      item: '갱신심사 기준',
      description: 'IAF MD5 기준: 최초심사의 2/3 (약 67%)'
    });
    
    assumptions.push({
      item: '심사일수 반올림',
      description: 'KAB-AR-MD5 2.2.3 기준: 소수점 둘째자리에서 사사오입하여 0.5일 단위로 조정'
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

    // 사후관리 및 갱신심사 계산
    const surveillanceResult = this.calculateSurveillance(organization);
    const recertificationResult = this.calculateRecertification(organization);

    const result = {
      client_name: client_name,
      calculation_standard: 'KAB-AR-MD5',
      total_audit_days: this.roundToHalfDay(totalAuditDays),
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
          enp: this.calculateENP(site),
          enp_range: this.getENPRange(this.calculateENP(site))
        }))
      },
      complexity_assessment: {
        overall_complexity: this.assessOverallComplexity(sites, standards),
        site_details: sites.map(site => ({
          name: site.name,
          complexity: standards.map(std => this.assessComplexity(site, std)),
          environmental_complexity: this.assessEnvironmentalComplexity(site)
        }))
      },
      stage_calculation: {
        total_stage1: breakdowns.reduce((sum, b) => sum + b.stage1_days, 0),
        total_stage2: breakdowns.reduce((sum, b) => sum + b.stage2_days, 0),
        total_surveillance: breakdowns.reduce((sum, b) => sum + b.surveillance_days, 0),
        total_recert: breakdowns.reduce((sum, b) => sum + b.recert_days, 0)
      },
      surveillance: surveillanceResult,
      recertification: recertificationResult
    };

    console.log('핵심두뇌 계산 완료 (KAB-AR-MD5):', result);
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
