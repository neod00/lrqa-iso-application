/**
 * ADJ v2.2 견적 계산 엔진 (JavaScript)
 * IAF MD5 + ADJ v2.2 기준 구현
 */

class QuoteCalculator {
    constructor() {
        this.mandayTables = this.initializeMandayTables();
        this.baseAuditRate = 1450000; // 일당 1,450,000원
        this.expenseRate = 0.1; // 10% 제경비
    }

    /**
     * IAF MD5 만데이 테이블 초기화
     */
    initializeMandayTables() {
        return {
            'ISO9001': {
                'SMALL': [
                    { min: 1, max: 10, days: 2.0 },
                    { min: 11, max: 25, days: 3.0 },
                    { min: 26, max: 45, days: 4.0 },
                    { min: 46, max: 65, days: 5.0 },
                    { min: 66, max: 85, days: 6.0 },
                    { min: 86, max: 125, days: 7.0 },
                    { min: 126, max: 175, days: 8.0 },
                    { min: 176, max: 275, days: 9.0 },
                    { min: 276, max: 425, days: 10.0 },
                    { min: 426, max: 625, days: 11.0 },
                    { min: 626, max: 875, days: 12.0 },
                    { min: 876, max: 1175, days: 13.0 },
                    { min: 1176, max: 1550, days: 14.0 },
                    { min: 1551, max: 2025, days: 15.0 },
                    { min: 2026, max: 2675, days: 16.0 },
                    { min: 2676, max: 3500, days: 17.0 },
                    { min: 3501, max: 4625, days: 18.0 },
                    { min: 4626, max: 6100, days: 19.0 },
                    { min: 6101, max: 8075, days: 20.0 },
                    { min: 8076, max: 10700, days: 21.0 },
                    { min: 10701, max: 14200, days: 22.0 },
                    { min: 14201, max: 18800, days: 23.0 },
                    { min: 18801, max: 25000, days: 24.0 }
                ],
                'MEDIUM': [
                    { min: 1, max: 10, days: 3.0 },
                    { min: 11, max: 25, days: 4.0 },
                    { min: 26, max: 45, days: 5.0 },
                    { min: 46, max: 65, days: 6.0 },
                    { min: 66, max: 85, days: 7.0 },
                    { min: 86, max: 125, days: 8.0 },
                    { min: 126, max: 175, days: 9.0 },
                    { min: 176, max: 275, days: 10.0 },
                    { min: 276, max: 425, days: 11.0 },
                    { min: 426, max: 625, days: 12.0 },
                    { min: 626, max: 875, days: 13.0 },
                    { min: 876, max: 1175, days: 14.0 },
                    { min: 1176, max: 1550, days: 15.0 },
                    { min: 1551, max: 2025, days: 16.0 },
                    { min: 2026, max: 2675, days: 17.0 },
                    { min: 2676, max: 3500, days: 18.0 },
                    { min: 3501, max: 4625, days: 19.0 },
                    { min: 4626, max: 6100, days: 20.0 },
                    { min: 6101, max: 8075, days: 21.0 },
                    { min: 8076, max: 10700, days: 22.0 },
                    { min: 10701, max: 14200, days: 23.0 },
                    { min: 14201, max: 18800, days: 24.0 },
                    { min: 18801, max: 25000, days: 25.0 }
                ],
                'LARGE': [
                    { min: 1, max: 10, days: 4.0 },
                    { min: 11, max: 25, days: 5.0 },
                    { min: 26, max: 45, days: 6.0 },
                    { min: 46, max: 65, days: 7.0 },
                    { min: 66, max: 85, days: 8.0 },
                    { min: 86, max: 125, days: 9.0 },
                    { min: 126, max: 175, days: 10.0 },
                    { min: 176, max: 275, days: 11.0 },
                    { min: 276, max: 425, days: 12.0 },
                    { min: 426, max: 625, days: 13.0 },
                    { min: 626, max: 875, days: 14.0 },
                    { min: 876, max: 1175, days: 15.0 },
                    { min: 1176, max: 1550, days: 16.0 },
                    { min: 1551, max: 2025, days: 17.0 },
                    { min: 2026, max: 2675, days: 18.0 },
                    { min: 2676, max: 3500, days: 19.0 },
                    { min: 3501, max: 4625, days: 20.0 },
                    { min: 4626, max: 6100, days: 21.0 },
                    { min: 6101, max: 8075, days: 22.0 },
                    { min: 8076, max: 10700, days: 23.0 },
                    { min: 10701, max: 14200, days: 24.0 },
                    { min: 14201, max: 18800, days: 25.0 },
                    { min: 18801, max: 25000, days: 26.0 }
                ]
            },
            'ISO14001': {
                'LIMITED': [
                    { min: 1, max: 10, days: 1.5 },
                    { min: 11, max: 25, days: 2.0 },
                    { min: 26, max: 45, days: 2.5 },
                    { min: 46, max: 65, days: 3.0 },
                    { min: 66, max: 85, days: 3.5 },
                    { min: 86, max: 125, days: 4.0 },
                    { min: 126, max: 175, days: 4.5 },
                    { min: 176, max: 275, days: 5.0 },
                    { min: 276, max: 425, days: 5.5 },
                    { min: 426, max: 625, days: 6.0 },
                    { min: 626, max: 875, days: 6.5 },
                    { min: 876, max: 1175, days: 7.0 },
                    { min: 1176, max: 1550, days: 7.5 },
                    { min: 1551, max: 2025, days: 8.0 },
                    { min: 2026, max: 2675, days: 8.5 },
                    { min: 2676, max: 3500, days: 9.0 },
                    { min: 3501, max: 4625, days: 9.5 },
                    { min: 4626, max: 6100, days: 10.0 },
                    { min: 6101, max: 8075, days: 10.5 },
                    { min: 8076, max: 10700, days: 11.0 },
                    { min: 10701, max: 14200, days: 11.5 },
                    { min: 14201, max: 18800, days: 12.0 },
                    { min: 18801, max: 25000, days: 12.5 }
                ],
                'LOW': [
                    { min: 1, max: 10, days: 2.0 },
                    { min: 11, max: 25, days: 2.5 },
                    { min: 26, max: 45, days: 3.0 },
                    { min: 46, max: 65, days: 3.5 },
                    { min: 66, max: 85, days: 4.0 },
                    { min: 86, max: 125, days: 4.5 },
                    { min: 126, max: 175, days: 5.0 },
                    { min: 176, max: 275, days: 5.5 },
                    { min: 276, max: 425, days: 6.0 },
                    { min: 426, max: 625, days: 6.5 },
                    { min: 626, max: 875, days: 7.0 },
                    { min: 876, max: 1175, days: 7.5 },
                    { min: 1176, max: 1550, days: 8.0 },
                    { min: 1551, max: 2025, days: 8.5 },
                    { min: 2026, max: 2675, days: 9.0 },
                    { min: 2676, max: 3500, days: 9.5 },
                    { min: 3501, max: 4625, days: 10.0 },
                    { min: 4626, max: 6100, days: 10.5 },
                    { min: 6101, max: 8075, days: 11.0 },
                    { min: 8076, max: 10700, days: 11.5 },
                    { min: 10701, max: 14200, days: 12.0 },
                    { min: 14201, max: 18800, days: 12.5 },
                    { min: 18801, max: 25000, days: 13.0 }
                ],
                'MEDIUM': [
                    { min: 1, max: 10, days: 2.5 },
                    { min: 11, max: 25, days: 3.0 },
                    { min: 26, max: 45, days: 3.5 },
                    { min: 46, max: 65, days: 4.0 },
                    { min: 66, max: 85, days: 4.5 },
                    { min: 86, max: 125, days: 5.0 },
                    { min: 126, max: 175, days: 5.5 },
                    { min: 176, max: 275, days: 6.0 },
                    { min: 276, max: 425, days: 6.5 },
                    { min: 426, max: 625, days: 7.0 },
                    { min: 626, max: 875, days: 7.5 },
                    { min: 876, max: 1175, days: 8.0 },
                    { min: 1176, max: 1550, days: 8.5 },
                    { min: 1551, max: 2025, days: 9.0 },
                    { min: 2026, max: 2675, days: 9.5 },
                    { min: 2676, max: 3500, days: 10.0 },
                    { min: 3501, max: 4625, days: 10.5 },
                    { min: 4626, max: 6100, days: 11.0 },
                    { min: 6101, max: 8075, days: 11.5 },
                    { min: 8076, max: 10700, days: 12.0 },
                    { min: 10701, max: 14200, days: 12.5 },
                    { min: 14201, max: 18800, days: 13.0 },
                    { min: 18801, max: 25000, days: 13.5 }
                ],
                'HIGH': [
                    { min: 1, max: 10, days: 3.0 },
                    { min: 11, max: 25, days: 3.5 },
                    { min: 26, max: 45, days: 4.0 },
                    { min: 46, max: 65, days: 4.5 },
                    { min: 66, max: 85, days: 5.0 },
                    { min: 86, max: 125, days: 5.5 },
                    { min: 126, max: 175, days: 6.0 },
                    { min: 176, max: 275, days: 6.5 },
                    { min: 276, max: 425, days: 7.0 },
                    { min: 426, max: 625, days: 7.5 },
                    { min: 626, max: 875, days: 8.0 },
                    { min: 876, max: 1175, days: 8.5 },
                    { min: 1176, max: 1550, days: 9.0 },
                    { min: 1551, max: 2025, days: 9.5 },
                    { min: 2026, max: 2675, days: 10.0 },
                    { min: 2676, max: 3500, days: 10.5 },
                    { min: 3501, max: 4625, days: 11.0 },
                    { min: 4626, max: 6100, days: 11.5 },
                    { min: 6101, max: 8075, days: 12.0 },
                    { min: 8076, max: 10700, days: 12.5 },
                    { min: 10701, max: 14200, days: 13.0 },
                    { min: 14201, max: 18800, days: 13.5 },
                    { min: 18801, max: 25000, days: 14.0 }
                ]
            },
            'ISO45001': {
                'LIMITED': [
                    { min: 1, max: 10, days: 1.5 },
                    { min: 11, max: 25, days: 2.0 },
                    { min: 26, max: 45, days: 2.5 },
                    { min: 46, max: 65, days: 3.0 },
                    { min: 66, max: 85, days: 3.5 },
                    { min: 86, max: 125, days: 4.0 },
                    { min: 126, max: 175, days: 4.5 },
                    { min: 176, max: 275, days: 5.0 },
                    { min: 276, max: 425, days: 5.5 },
                    { min: 426, max: 625, days: 6.0 },
                    { min: 626, max: 875, days: 6.5 },
                    { min: 876, max: 1175, days: 7.0 },
                    { min: 1176, max: 1550, days: 7.5 },
                    { min: 1551, max: 2025, days: 8.0 },
                    { min: 2026, max: 2675, days: 8.5 },
                    { min: 2676, max: 3500, days: 9.0 },
                    { min: 3501, max: 4625, days: 9.5 },
                    { min: 4626, max: 6100, days: 10.0 },
                    { min: 6101, max: 8075, days: 10.5 },
                    { min: 8076, max: 10700, days: 11.0 },
                    { min: 10701, max: 14200, days: 11.5 },
                    { min: 14201, max: 18800, days: 12.0 },
                    { min: 18801, max: 25000, days: 12.5 }
                ],
                'LOW': [
                    { min: 1, max: 10, days: 2.0 },
                    { min: 11, max: 25, days: 2.5 },
                    { min: 26, max: 45, days: 3.0 },
                    { min: 46, max: 65, days: 3.5 },
                    { min: 66, max: 85, days: 4.0 },
                    { min: 86, max: 125, days: 4.5 },
                    { min: 126, max: 175, days: 5.0 },
                    { min: 176, max: 275, days: 5.5 },
                    { min: 276, max: 425, days: 6.0 },
                    { min: 426, max: 625, days: 6.5 },
                    { min: 626, max: 875, days: 7.0 },
                    { min: 876, max: 1175, days: 7.5 },
                    { min: 1176, max: 1550, days: 8.0 },
                    { min: 1551, max: 2025, days: 8.5 },
                    { min: 2026, max: 2675, days: 9.0 },
                    { min: 2676, max: 3500, days: 9.5 },
                    { min: 3501, max: 4625, days: 10.0 },
                    { min: 4626, max: 6100, days: 10.5 },
                    { min: 6101, max: 8075, days: 11.0 },
                    { min: 8076, max: 10700, days: 11.5 },
                    { min: 10701, max: 14200, days: 12.0 },
                    { min: 14201, max: 18800, days: 12.5 },
                    { min: 18801, max: 25000, days: 13.0 }
                ],
                'MEDIUM': [
                    { min: 1, max: 10, days: 2.5 },
                    { min: 11, max: 25, days: 3.0 },
                    { min: 26, max: 45, days: 3.5 },
                    { min: 46, max: 65, days: 4.0 },
                    { min: 66, max: 85, days: 4.5 },
                    { min: 86, max: 125, days: 5.0 },
                    { min: 126, max: 175, days: 5.5 },
                    { min: 176, max: 275, days: 6.0 },
                    { min: 276, max: 425, days: 6.5 },
                    { min: 426, max: 625, days: 7.0 },
                    { min: 626, max: 875, days: 7.5 },
                    { min: 876, max: 1175, days: 8.0 },
                    { min: 1176, max: 1550, days: 8.5 },
                    { min: 1551, max: 2025, days: 9.0 },
                    { min: 2026, max: 2675, days: 9.5 },
                    { min: 2676, max: 3500, days: 10.0 },
                    { min: 3501, max: 4625, days: 10.5 },
                    { min: 4626, max: 6100, days: 11.0 },
                    { min: 6101, max: 8075, days: 11.5 },
                    { min: 8076, max: 10700, days: 12.0 },
                    { min: 10701, max: 14200, days: 12.5 },
                    { min: 14201, max: 18800, days: 13.0 },
                    { min: 18801, max: 25000, days: 13.5 }
                ],
                'HIGH': [
                    { min: 1, max: 10, days: 3.0 },
                    { min: 11, max: 25, days: 3.5 },
                    { min: 26, max: 45, days: 4.0 },
                    { min: 46, max: 65, days: 4.5 },
                    { min: 66, max: 85, days: 5.0 },
                    { min: 86, max: 125, days: 5.5 },
                    { min: 126, max: 175, days: 6.0 },
                    { min: 176, max: 275, days: 6.5 },
                    { min: 276, max: 425, days: 7.0 },
                    { min: 426, max: 625, days: 7.5 },
                    { min: 626, max: 875, days: 8.0 },
                    { min: 876, max: 1175, days: 8.5 },
                    { min: 1176, max: 1550, days: 9.0 },
                    { min: 1551, max: 2025, days: 9.5 },
                    { min: 2026, max: 2675, days: 10.0 },
                    { min: 2676, max: 3500, days: 10.5 },
                    { min: 3501, max: 4625, days: 11.0 },
                    { min: 4626, max: 6100, days: 11.5 },
                    { min: 6101, max: 8075, days: 12.0 },
                    { min: 8076, max: 10700, days: 12.5 },
                    { min: 10701, max: 14200, days: 13.0 },
                    { min: 14201, max: 18800, days: 13.5 },
                    { min: 18801, max: 25000, days: 14.0 }
                ]
            }
        };
    }

    /**
     * 신청서 데이터를 견적서 데이터로 변환
     */
    convertApplicationToQuotation(applicationData) {
        try {
            // 기본 정보 추출
            const clientName = applicationData['법인명(국문)'] || applicationData['법인명(영문)'] || 'Unknown';
            const contactPerson = applicationData['담당자명'] || '';
            const phone = applicationData['담당자전화'] || '';
            const email = applicationData['담당자이메일'] || '';
            const address = applicationData['주소'] || '';
            
            // 사업장 정보 추출
            const sites = this.extractSiteData(applicationData);
            
            // 표준 정보 추출
            const standards = this.extractStandardsData(applicationData);
            
            // ENP 계산
            const totalENP = sites.reduce((sum, site) => sum + this.calculateENP(site), 0);
            
            // 표준별 견적 계산
            const quotationBreakdown = [];
            let totalAuditDays = 0;
            
            for (const standard of standards) {
                const standardQuote = this.calculateStandardQuote(totalENP, standard, sites);
                quotationBreakdown.push(standardQuote);
                totalAuditDays += standardQuote.totalDays;
            }
            
            // 통합심사 할인 적용
            if (standards.length > 1) {
                const discount = this.calculateIntegratedAuditDiscount(standards.length);
                totalAuditDays *= (1 - discount);
                
                quotationBreakdown.push({
                    standard: 'INTEGRATED_DISCOUNT',
                    description: `통합심사 할인 (${Math.round(discount * 100)}%)`,
                    stage1Days: 0,
                    stage2Days: 0,
                    surveillanceDays: 0,
                    recertificationDays: 0,
                    totalDays: -totalAuditDays * discount,
                    complexity: 'N/A'
                });
            }
            
            // 0.5일 단위로 반올림
            totalAuditDays = this.roundToHalfDay(totalAuditDays);
            
            // 비용 계산
            const auditFee = totalAuditDays * this.baseAuditRate;
            const expenses = auditFee * this.expenseRate;
            const totalCost = auditFee + expenses;
            
            return {
                client_name: clientName,
                contact_person: contactPerson,
                phone: phone,
                email: email,
                address: address,
                standards: standards,
                sites: sites,
                total_enp: totalENP,
                quotation_breakdown: quotationBreakdown,
                total_audit_days: totalAuditDays,
                audit_fee: auditFee,
                expenses: expenses,
                total_cost: totalCost,
                created_at: new Date().toISOString(),
                assumptions: this.generateAssumptions(sites, standards),
                justification: this.generateJustification(quotationBreakdown, totalENP)
            };
            
        } catch (error) {
            console.error('견적서 변환 오류:', error);
            throw new Error('신청서 데이터를 견적서로 변환하는 중 오류가 발생했습니다.');
        }
    }

    /**
     * 사업장 데이터 추출
     */
    extractSiteData(applicationData) {
        const sites = [];
        
        // 본사 사업장
        const mainSite = {
            name: applicationData['법인명(국문)'] || applicationData['법인명(영문)'] || '본사',
            address: applicationData['주소'] || '',
            totalHeadcount: parseInt(applicationData['상시종업원수'] || '0'),
            contractorCount: 0,
            partTimeCount: 0,
            shiftWorkers: 0,
            repetitiveProcess: false,
            seasonalFactor: 1.0,
            isMainSite: true
        };
        sites.push(mainSite);
        
        // 추가 사업장이 있다면 추출 (신청서 구조에 따라 조정 필요)
        // 현재는 단일 사업장으로 가정
        
        return sites;
    }

    /**
     * 표준 정보 추출
     */
    extractStandardsData(applicationData) {
        const standards = [];
        const certificationScope = applicationData['인증범위'] || '';
        
        // 인증범위에서 표준 추출 (키워드 기반)
        if (certificationScope.includes('ISO 9001') || certificationScope.includes('9001')) {
            standards.push('ISO9001');
        }
        if (certificationScope.includes('ISO 14001') || certificationScope.includes('14001')) {
            standards.push('ISO14001');
        }
        if (certificationScope.includes('ISO 45001') || certificationScope.includes('45001')) {
            standards.push('ISO45001');
        }
        
        // 기본값으로 ISO 9001 설정 (표준이 없는 경우)
        if (standards.length === 0) {
            standards.push('ISO9001');
        }
        
        return standards;
    }

    /**
     * ENP (유효인원수) 계산
     */
    calculateENP(site) {
        let enp = site.totalHeadcount + site.contractorCount;
        
        // 파트타임 50% 감축
        enp -= site.partTimeCount * 0.5;
        
        // 반복공정 10% 감축
        if (site.repetitiveProcess) {
            enp *= 0.9;
        }
        
        // 계절성 가중치 적용
        enp *= site.seasonalFactor;
        
        // 교대근무자 50% 가산
        enp += site.shiftWorkers * 0.5;
        
        return Math.max(1, Math.round(enp));
    }

    /**
     * 표준별 견적 계산
     */
    calculateStandardQuote(totalENP, standard, sites) {
        // 복잡도 결정
        const complexity = this.determineComplexity(totalENP, standard, sites);
        
        // 기본 심사일수 조회 (Stage1 + Stage2 총합)
        const baseDays = this.getBaseDays(totalENP, standard, complexity);
        
        // Stage별 분할
        const stage1Days = baseDays * 0.3; // 30%
        const stage2Days = baseDays * 0.7; // 70%
        const surveillanceDays = baseDays * 0.6; // 60%
        const recertificationDays = baseDays; // 100%
        
        return {
            standard: standard,
            complexity: complexity,
            enp: totalENP,
            stage1Days: this.roundToHalfDay(stage1Days),
            stage2Days: this.roundToHalfDay(stage2Days),
            surveillanceDays: this.roundToHalfDay(surveillanceDays),
            recertificationDays: this.roundToHalfDay(recertificationDays),
            totalDays: this.roundToHalfDay(baseDays)
        };
    }

    /**
     * 복잡도 결정
     */
    determineComplexity(enp, standard, sites) {
        if (standard === 'ISO9001') {
            // QMS는 Small/Medium/Large 분류
            if (enp <= 125) return 'SMALL';
            if (enp <= 875) return 'MEDIUM';
            return 'LARGE';
        } else {
            // EMS/OH&SMS는 Limited/Low/Medium/High 분류
            // 간단한 기준으로 구현 (실제로는 환경영향/안전위험 평가 필요)
            if (enp <= 85) return 'LIMITED';
            if (enp <= 425) return 'LOW';
            if (enp <= 1550) return 'MEDIUM';
            return 'HIGH';
        }
    }

    /**
     * 기본 심사일수 조회
     */
    getBaseDays(enp, standard, complexity) {
        const table = this.mandayTables[standard][complexity];
        if (!table) {
            console.warn(`Unknown standard or complexity: ${standard}, ${complexity}`);
            return 3.0; // 기본값
        }
        
        const entry = table.find(row => enp >= row.min && enp <= row.max);
        if (!entry) {
            // ENP가 범위를 벗어나는 경우 가장 큰 값 사용
            const lastEntry = table[table.length - 1];
            return lastEntry.days;
        }
        
        return entry.days;
    }

    /**
     * 통합심사 할인율 계산
     */
    calculateIntegratedAuditDiscount(standardCount) {
        if (standardCount === 2) return 0.15; // 15% 할인
        if (standardCount >= 3) return 0.20; // 20% 할인
        return 0; // 단일 표준은 할인 없음
    }

    /**
     * 0.5일 단위 반올림
     */
    roundToHalfDay(days) {
        return Math.round(days * 2) / 2;
    }

    /**
     * 가정사항 생성
     */
    generateAssumptions(sites, standards) {
        const assumptions = [
            '본 견적은 IAF MD5 및 ADJ v2.2 기준에 따라 산정되었습니다.',
            '심사일수는 Stage1(30%) + Stage2(70%) 기준으로 분할됩니다.',
            '감시심사는 Stage2 기준일수의 60%로 산정됩니다.',
            '갱신심사는 Stage2 기준일수의 100%로 산정됩니다.',
            '심사비는 일당 1,450,000원(VAT 별도)으로 산정됩니다.',
            '제경비는 심사비의 10%로 산정됩니다.'
        ];
        
        if (standards.length > 1) {
            assumptions.push(`통합심사 할인(${standards.length}개 표준): ${standards.length === 2 ? '15%' : '20%'} 적용`);
        }
        
        return assumptions;
    }

    /**
     * 근거자료 생성
     */
    generateJustification(quotationBreakdown, totalENP) {
        const justification = [
            `총 유효인원수(ENP): ${totalENP}명`,
            'IAF MD5 표준 심사일수 적용',
            'ADJ v2.2 계산 규칙 준수'
        ];
        
        quotationBreakdown.forEach(breakdown => {
            if (breakdown.standard !== 'INTEGRATED_DISCOUNT') {
                justification.push(
                    `${breakdown.standard}: ${breakdown.complexity} 복잡도, ` +
                    `Stage1+2 총 ${breakdown.totalDays}일`
                );
            }
        });
        
        return justification;
    }
}

// 전역 견적 계산기 인스턴스
const quoteCalculator = new QuoteCalculator();
