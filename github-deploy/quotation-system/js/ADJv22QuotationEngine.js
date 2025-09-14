/**
 * ADJ v2.2 기반 정확한 견적 계산 엔진
 * Python 백엔드와 연동하여 정확한 ADJ v2.2 규칙 적용
 */

class ADJv22QuotationEngine {
    constructor() {
        this.apiEndpoint = '/.netlify/functions/adj-quote-calculator';
        this.fallbackEngine = new SmartQuotationSystem(); // 기존 엔진을 백업으로 사용
        this.isOnline = true;
    }

    /**
     * ADJ v2.2 기반 견적 계산
     * @param {Object} formData - 신청서 폼 데이터
     * @returns {Promise<Object>} 견적 결과
     */
    async calculateQuotation(formData) {
        try {
            console.log('=== ADJ v2.2 견적 계산 시작 ===');
            console.log('입력 데이터:', formData);

            // Python 백엔드로 데이터 전송
            const response = await this.callPythonBackend(formData);
            
            if (response.success) {
                console.log('ADJ v2.2 계산 성공:', response.data);
                return this.formatQuotationResult(response.data);
            } else {
                console.warn('ADJ v2.2 계산 실패, 기존 엔진 사용:', response.error);
                return this.fallbackEngine.calculateQuotation(formData);
            }

        } catch (error) {
            console.error('ADJ v2.2 계산 오류:', error);
            console.log('기존 엔진으로 폴백');
            return this.fallbackEngine.calculateQuotation(formData);
        }
    }

    /**
     * Python 백엔드 호출
     * @param {Object} formData - 폼 데이터
     * @returns {Promise<Object>} 백엔드 응답
     */
    async callPythonBackend(formData) {
        try {
            // JavaScript 데이터를 Python 엔진 형식으로 변환
            const pythonData = this.convertToPythonFormat(formData);
            
            console.log('Python 백엔드로 전송할 데이터:', pythonData);

            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(pythonData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Python 백엔드 응답:', result);
            return result;

        } catch (error) {
            console.error('Python 백엔드 호출 실패:', error);
            throw error;
        }
    }

    /**
     * JavaScript 폼 데이터를 Python 엔진 형식으로 변환
     * @param {Object} formData - JavaScript 폼 데이터
     * @returns {Object} Python 엔진 형식 데이터
     */
    convertToPythonFormat(formData) {
        return {
            client_name: formData.companyNameKo || formData.companyName || 'Unknown',
            client_name_en: formData.companyNameEn || '',
            standards: this.extractStandards(formData),
            sites: this.extractSites(formData),
            integration: this.extractIntegration(formData),
            options: this.extractOptions(formData)
        };
    }

    /**
     * ISO 표준 추출
     * @param {Object} formData - 폼 데이터
     * @returns {Array} 표준 배열
     */
    extractStandards(formData) {
        const standards = [];
        const isoStandards = formData.isoStandards || '';
        
        if (typeof isoStandards === 'string') {
            const stdArray = isoStandards.split(',').map(s => s.trim().toLowerCase());
            const standardMapping = {
                'iso9001': 'ISO9001',
                'iso14001': 'ISO14001',
                'iso45001': 'ISO45001',
                'iso27001': 'ISO27001',
                'iso22000': 'ISO22000',
                'iso13485': 'ISO13485'
            };
            
            stdArray.forEach(std => {
                if (standardMapping[std]) {
                    standards.push(standardMapping[std]);
                }
            });
        }
        
        return standards.length > 0 ? standards : ['ISO9001'];
    }

    /**
     * 사업장 정보 추출
     * @param {Object} formData - 폼 데이터
     * @returns {Array} 사업장 배열
     */
    extractSites(formData) {
        return [{
            name: '본사',
            address: formData.headOfficeAddress || '',
            standards: this.extractStandards(formData),
            total_headcount: this.safeInt(formData.employee_총직원수) || 0,
            part_time_count: this.safeInt(formData.employee_비정규직수) || 0,
            contractor_count: 0, // JavaScript에서 제공하지 않음
            shift_workers: 0,    // JavaScript에서 제공하지 않음
            seasonal_factor: 1.0,
            repetitive_process: false,
            remote_audit_ratio: 0.0
        }];
    }

    /**
     * 통합심사 정보 추출
     * @param {Object} formData - 폼 데이터
     * @returns {Object} 통합심사 정보
     */
    extractIntegration(formData) {
        const isIntegrated = (formData.standardIntegration || '').toLowerCase() === 'yes';
        return {
            is_integrated: isIntegrated,
            integration_level: isIntegrated ? 0.8 : 0.0,
            shared_management_system: true,
            common_processes: true,
            same_audit_team: true
        };
    }

    /**
     * 옵션 정보 추출
     * @param {Object} formData - 폼 데이터
     * @returns {Object} 옵션 정보
     */
    extractOptions(formData) {
        return {
            stage1: true,
            stage2: true,
            surveillance: true,
            recert: false,
            remote_audit_ratio: 0.0,
            day_rate: 1300000.0,
            vat_rate: 0.1
        };
    }

    /**
     * 안전한 정수 변환
     * @param {*} value - 변환할 값
     * @returns {number} 정수 값
     */
    safeInt(value) {
        try {
            return parseInt(value) || 0;
        } catch (e) {
            return 0;
        }
    }

    /**
     * Python 엔진 결과를 JavaScript 형식으로 변환
     * @param {Object} pythonResult - Python 엔진 결과
     * @returns {Object} JavaScript 견적 결과
     */
    formatQuotationResult(pythonResult) {
        const result = {
            success: true,
            totalAmount: pythonResult.total_cost,
            baseAuditCost: pythonResult.subtotal_cost,
            overheadCost: pythonResult.vat_amount,
            totalAuditDays: pythonResult.total_audit_days,
            dayRate: pythonResult.day_rate,
            vatRate: pythonResult.vat_rate,
            breakdowns: [],
            assumptions: pythonResult.assumptions || [],
            justification: pythonResult.justification || [],
            created_at: pythonResult.created_at,
            engine: 'ADJ v2.2 Python Engine'
        };

        // 표준별 breakdown 변환
        if (pythonResult.breakdowns) {
            pythonResult.breakdowns.forEach(bd => {
                result.breakdowns.push({
                    standard: bd.standard,
                    enp: bd.enp,
                    complexity: bd.complexity,
                    stage1_days: bd.stage1_days,
                    stage2_days: bd.stage2_days,
                    surveillance_days: bd.surveillance_days,
                    recert_days: bd.recert_days,
                    total_days: bd.total_days,
                    subtotal_cost: bd.total_days * pythonResult.day_rate,
                    vat_amount: bd.total_days * pythonResult.day_rate * pythonResult.vat_rate,
                    total_cost: bd.total_days * pythonResult.day_rate * (1 + pythonResult.vat_rate)
                });
            });
        }

        return result;
    }

    /**
     * Word 문서 생성
     * @param {Object} formData - 폼 데이터
     * @returns {Promise<Object>} 문서 생성 결과
     */
    async generateWordDocument(formData) {
        try {
            const pythonData = this.convertToPythonFormat(formData);
            
            const response = await fetch('/.netlify/functions/adj-quote-docx', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(pythonData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('Word 문서 생성 실패:', error);
            return {
                success: false,
                error: error.message,
                message: 'Word 문서 생성 중 오류가 발생했습니다.'
            };
        }
    }

    /**
     * 엔진 상태 확인
     * @returns {Promise<boolean>} 온라인 상태
     */
    async checkEngineStatus() {
        try {
            const response = await fetch('/.netlify/functions/adj-quote-status', {
                method: 'GET'
            });
            this.isOnline = response.ok;
            return this.isOnline;
        } catch (error) {
            console.warn('ADJ v2.2 엔진 상태 확인 실패:', error);
            this.isOnline = false;
            return false;
        }
    }
}

// 전역 인스턴스 생성
window.ADJv22QuotationEngine = ADJv22QuotationEngine;
