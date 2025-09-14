/**
 * LRQA 스마트 견적 산출 시스템
 * ADJ_v.2.2.xlsx 기반 견적 로직 구현
 */

class SmartQuotationSystem {
    constructor() {
        // ADJ_v.2.2.xlsx 기반 기본 견적 요율
        this.baseRates = {
            iso9001: { 
                base: 1450000, 
                perEmployee: 50000, 
                perSite: 300000,
                name: 'ISO 9001 (품질경영시스템)',
                description: '품질경영시스템 인증 심사',
                auditDays: 2
            },
            iso14001: { 
                base: 1450000, 
                perEmployee: 60000, 
                perSite: 400000,
                name: 'ISO 14001 (환경경영시스템)',
                description: '환경경영시스템 인증 심사',
                auditDays: 2
            },
            iso45001: { 
                base: 1450000, 
                perEmployee: 70000, 
                perSite: 500000,
                name: 'ISO 45001 (안전보건경영시스템)',
                description: '안전보건경영시스템 인증 심사',
                auditDays: 2
            }
        };
        
        // 업종별 계수 (ADJ_v.2.2.xlsx 기준)
        this.industryMultipliers = {
            '제조업': { name: '제조업', multiplier: 1.0, risk: 'standard' },
            '건설업': { name: '건설업', multiplier: 1.2, risk: 'high' },
            '화학업': { name: '화학업', multiplier: 1.5, risk: 'very_high' },
            '식품업': { name: '식품업', multiplier: 1.3, risk: 'high' },
            '서비스업': { name: '서비스업', multiplier: 0.9, risk: 'low' },
            '무역업': { name: '무역업', multiplier: 0.8, risk: 'low' },
            '기타': { name: '기타', multiplier: 1.0, risk: 'standard' }
        };
        
        // 복잡도 계수
        this.complexityFactors = {
            '낮음': { name: '낮음', multiplier: 0.8, description: '단순한 업무 프로세스' },
            '보통': { name: '보통', multiplier: 1.0, description: '일반적인 업무 프로세스' },
            '높음': { name: '높음', multiplier: 1.3, description: '복잡한 업무 프로세스' }
        };
        
        // 할인 정책
        this.discountPolicies = {
            multiStandard: {
                2: 0.15,  // 2개 표준: 15% 할인
                3: 0.25   // 3개 표준: 25% 할인
            },
            existingCertification: 0.10,  // 기존 인증: 10% 할인
            largeCompany: 0.05,           // 대기업: 5% 할인
            longTermContract: 0.08        // 장기 계약: 8% 할인
        };
        
        // 추가 서비스 요율
        this.additionalServices = {
            preAudit: { name: '사전 심사', rate: 0.3 },
            documentReview: { name: '문서 검토', rate: 0.2 },
            training: { name: '교육', rate: 0.15 },
            consulting: { name: '컨설팅', rate: 0.25 }
        };
    }
    
    /**
     * 견적 계산 메인 메서드
     */
    calculateQuotation(formData) {
        const {
            isoStandards,
            employeeCount,
            siteCount,
            industry,
            complexity,
            existingCertifications,
            multiStandardSystem,
            companySize,
            contractType
        } = formData;
        
        // 필드명 매핑
        const totalEmployees = employeeCount;
        const existingCertification = existingCertifications;
        
        // 총 심사일수 계산
        const totalAuditDays = this.calculateTotalAuditDays(isoStandards, formData);
        
        // 사용자 요청 공식: 심사일수 × 1,450,000원 + 제경비(총 심사비의 10%)
        const baseAuditCost = totalAuditDays * 1450000; // 심사일수 × 1,450,000원
        const overhead = baseAuditCost * 0.1; // 제경비(총 심사비의 10%)
        const totalQuotation = baseAuditCost + overhead;
        
        // 견적 세부 내역 생성
        let breakdown = [];
        isoStandards.forEach(standard => {
            const standardKey = this.convertStandardToKey(standard);
            const baseRate = this.baseRates[standardKey];
            if (baseRate) {
                breakdown.push({
                    standard: standard,
                    amount: Math.round(totalQuotation / isoStandards.length), // 균등 분배
                    details: this.getStandardBreakdown(standard, Math.round(totalQuotation / isoStandards.length))
                });
            }
        });
        
        // 할인 정보 (참고용으로만 표시)
        let appliedDiscounts = [];
        if (isoStandards.length > 1) {
            appliedDiscounts.push({
                type: '다중 표준 통합 심사',
                rate: 0,
                amount: 0,
                note: '통합 심사로 인한 효율성 증대'
            });
        }
        
        return {
            totalAmount: Math.round(totalQuotation),
            originalAmount: Math.round(totalQuotation),
            breakdown: breakdown,
            appliedDiscounts: appliedDiscounts,
            totalAuditDays: totalAuditDays,
            baseAuditCost: Math.round(baseAuditCost),
            overhead: Math.round(overhead),
            currency: 'KRW',
            validity: '30일',
            notes: this.generateQuotationNotes(formData),
            calculationDate: new Date().toISOString(),
            quotationNumber: this.generateQuotationNumber()
        };
    }
    
    /**
     * 개별 표준 견적 계산
     */
    calculateStandardQuote(standard, params) {
        // 표준 코드를 baseRates 키로 변환
        const standardKey = this.convertStandardToKey(standard);
        const baseRate = this.baseRates[standardKey];
        if (!baseRate) {
            console.warn(`표준 ${standard}에 대한 기본 요율을 찾을 수 없습니다.`);
            return 0;
        }
        
        let quote = baseRate.base;
        
        // 직원 수에 따른 추가 비용
        if (params.employees > 50) {
            quote += (params.employees - 50) * baseRate.perEmployee;
        }
        
        // 사업장 수에 따른 추가 비용
        if (params.sites > 1) {
            quote += (params.sites - 1) * baseRate.perSite;
        }
        
        // 업종 계수 적용
        const industryInfo = this.industryMultipliers[params.industry];
        if (industryInfo) {
            quote *= industryInfo.multiplier;
        }
        
        // 복잡도 계수 적용
        const complexityInfo = this.complexityFactors[params.complexity];
        if (complexityInfo) {
            quote *= complexityInfo.multiplier;
        }
        
        return quote;
    }
    
    /**
     * 다중 표준 할인 계산
     */
    calculateMultiStandardDiscount(standardCount) {
        return this.discountPolicies.multiStandard[standardCount] || 0;
    }
    
    /**
     * 견적 세부 내역 생성
     */
    getStandardBreakdown(standard, amount) {
        // 표준 코드를 baseRates 키로 변환
        const standardKey = this.convertStandardToKey(standard);
        const baseRate = this.baseRates[standardKey];
        if (!baseRate) {
            console.warn(`표준 ${standard}에 대한 기본 요율을 찾을 수 없습니다.`);
            return {
                standardName: standard,
                description: '표준 정보 없음',
                baseAmount: Math.round(amount * 0.6),
                additionalServices: Math.round(amount * 0.4),
                services: [
                    '인증 심사',
                    '문서 검토',
                    '기술 지원',
                    '인증서 발급'
                ]
            };
        }
        
        const baseAmount = Math.round(amount * 0.6);
        const additionalServices = Math.round(amount * 0.4);
        
        return {
            standardName: baseRate.name || standard,
            description: baseRate.description || '표준 설명 없음',
            baseAmount: baseAmount,
            additionalServices: additionalServices,
            services: [
                '인증 심사',
                '문서 검토',
                '기술 지원',
                '인증서 발급'
            ]
        };
    }
    
    /**
     * 견적 노트 생성
     */
    generateQuotationNotes(formData) {
        const notes = [];
        
        const totalEmployees = this.parseEmployeeCount(formData.employeeCount) || 0;
        const siteCount = parseInt(formData.siteCount) || 1;
        
        if (totalEmployees > 200) {
            notes.push('대규모 조직으로 인한 추가 심사 일정 필요 (예상 2-3일 추가)');
        }
        
        if (siteCount > 3) {
            notes.push('다중 사업장으로 인한 추가 현장 심사 필요 (사업장당 0.5일 추가)');
        }
        
        const industryInfo = this.industryMultipliers[formData.industry];
        if (industryInfo && industryInfo.risk === 'very_high') {
            notes.push('고위험 업종으로 인한 추가 안전/환경 검토 필요');
        }
        
        if (formData.complexity === '높음') {
            notes.push('복잡한 업무 프로세스로 인한 추가 심사 시간 필요');
        }
        
        return notes;
    }
    
    /**
     * 직원 수 문자열을 숫자로 변환
     */
    parseEmployeeCount(employeeCountStr) {
        if (!employeeCountStr) return 0;
        
        if (typeof employeeCountStr === 'number') return employeeCountStr;
        
        const str = employeeCountStr.toString();
        if (str.includes('-')) {
            const parts = str.split('-');
            return parseInt(parts[1]) || 0;
        } else if (str.includes('+')) {
            return parseInt(str.replace('+', '')) || 0;
        } else {
            return parseInt(str) || 0;
        }
    }
    
    /**
     * 표준 코드를 baseRates 키로 변환
     */
    convertStandardToKey(standard) {
        if (typeof standard === 'string' && standard.startsWith('iso')) {
            return standard; // 이미 올바른 형식
        }
        return `iso${standard}`;
    }
    
    /**
     * 총 심사일수 계산
     */
    calculateTotalAuditDays(isoStandards, formData) {
        let totalDays = 0;
        
        // 각 ISO 표준별 기본 심사일수
        isoStandards.forEach(standard => {
            const standardKey = this.convertStandardToKey(standard);
            const baseRate = this.baseRates[standardKey];
            if (baseRate && baseRate.auditDays) {
                totalDays += baseRate.auditDays;
            }
        });
        
        // 직원 수에 따른 추가 심사일수
        const totalEmployees = this.parseEmployeeCount(formData.employeeCount);
        if (totalEmployees > 200) {
            totalDays += 1; // 대규모 조직: 1일 추가
        } else if (totalEmployees > 100) {
            totalDays += 0.5; // 중간 규모 조직: 0.5일 추가
        }
        
        // 사업장 수에 따른 추가 심사일수
        const siteCount = parseInt(formData.siteCount) || 1;
        if (siteCount > 3) {
            totalDays += Math.ceil((siteCount - 3) * 0.5); // 3개소 초과시 사업장당 0.5일 추가
        }
        
        // 업종별 추가 심사일수
        const industryInfo = this.industryMultipliers[formData.industry];
        if (industryInfo && industryInfo.risk === 'very_high') {
            totalDays += 0.5; // 고위험 업종: 0.5일 추가
        }
        
        // 복잡도에 따른 추가 심사일수
        if (formData.complexity === '높음') {
            totalDays += 1; // 높음: 1일 추가
        }
        
        return Math.ceil(totalDays); // 소수점 올림
    }
    
    /**
     * 견적 번호 생성
     */
    generateQuotationNumber() {
        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        
        return `LRQA-QUO-${year}${month}${day}-${random}`;
    }
    
    /**
     * 견적 요약 정보 생성
     */
    generateQuotationSummary(quotation, formData) {
        return {
            companyName: formData.companyNameKo || formData.companyName || '미입력',
            contactPerson: formData.contactName || '미입력',
            contactEmail: formData.contactEmail || '미입력',
            contactPhone: formData.contactPhone || '미입력',
            totalEmployees: formData.employeeCount || '미입력',
            siteCount: formData.siteCount || '미입력',
            industry: this.industryMultipliers[formData.industry]?.name || '미입력',
            complexity: this.complexityFactors[formData.complexity]?.name || '미입력',
            selectedStandards: formData.isoStandards?.map(s => {
                const standardKey = this.convertStandardToKey(s);
                return this.baseRates[standardKey]?.name || s;
            }).join(', ') || '미입력',
            quotationAmount: quotation.totalAmount,
            validityPeriod: quotation.validity
        };
    }
}

// 전역으로 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SmartQuotationSystem;
} else {
    window.SmartQuotationSystem = SmartQuotationSystem;
}
