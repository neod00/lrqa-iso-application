/**
 * LRQA 견적 시스템 초기화 및 통합
 * 메인 페이지에 견적 계산기 통합
 */

class QuotationSystemManager {
    constructor() {
        this.isInitialized = false;
        this.quotationCalculator = null;
        this.init();
    }
    
    /**
     * 시스템 초기화
     */
    async init() {
        try {
            // 필요한 라이브러리 로드 확인
            await this.loadDependencies();
            
            // 견적 계산기 초기화
            this.initializeQuotationCalculator();
            
            // 이벤트 리스너 설정
            this.setupEventListeners();
            
            this.isInitialized = true;
            console.log('LRQA 견적 시스템이 성공적으로 초기화되었습니다.');
            
        } catch (error) {
            console.error('견적 시스템 초기화 실패:', error);
            this.showErrorMessage('견적 시스템 초기화에 실패했습니다.');
        }
    }
    
    /**
     * 필요한 의존성 로드
     */
    async loadDependencies() {
        // SmartQuotationSystem 클래스 확인
        if (typeof SmartQuotationSystem === 'undefined') {
            throw new Error('SmartQuotationSystem 클래스를 찾을 수 없습니다.');
        }
        
        // WordDocumentGenerator 클래스 확인
        if (typeof WordDocumentGenerator === 'undefined') {
            throw new Error('WordDocumentGenerator 클래스를 찾을 수 없습니다.');
        }
        
        // QuotationCalculator 클래스 확인
        if (typeof QuotationCalculator === 'undefined') {
            throw new Error('QuotationCalculator 클래스를 찾을 수 없습니다.');
        }
        
        // DocxGen 라이브러리 로드
        await this.loadDocxGenLibrary();
    }
    
    /**
     * DocxGen 라이브러리 로드
     */
    async loadDocxGenLibrary() {
        return new Promise((resolve, reject) => {
            if (typeof docxgen !== 'undefined') {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/docxgen@latest/dist/docxgen.js';
            script.onload = () => {
                console.log('DocxGen 라이브러리가 로드되었습니다.');
                resolve();
            };
            script.onerror = () => {
                reject(new Error('DocxGen 라이브러리 로드에 실패했습니다.'));
            };
            
            document.head.appendChild(script);
        });
    }
    
    /**
     * 견적 계산기 초기화
     */
    initializeQuotationCalculator() {
        try {
            this.quotationCalculator = new QuotationCalculator();
            console.log('견적 계산기가 초기화되었습니다.');
        } catch (error) {
            console.error('견적 계산기 초기화 실패:', error);
            throw error;
        }
    }
    
    /**
     * 이벤트 리스너 설정
     */
    setupEventListeners() {
        // 페이지 로드 완료 후 견적 계산기 표시
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.showQuotationCalculator();
            });
        } else {
            this.showQuotationCalculator();
        }
        
        // 기존 폼과의 연동
        this.integrateWithExistingForm();
    }
    
    /**
     * 견적 계산기 표시
     */
    showQuotationCalculator() {
        // 평가 요구사항 섹션 다음에 견적 계산기 삽입
        const targetSection = this.findTargetSection();
        if (targetSection) {
            this.insertQuotationCalculator(targetSection);
        } else {
            // 대체 위치에 삽입
            this.insertQuotationCalculatorAtEnd();
        }
    }
    
    /**
     * 대상 섹션 찾기
     */
    findTargetSection() {
        // 평가 요구사항 섹션 찾기
        const sections = document.querySelectorAll('.section');
        for (let i = 0; i < sections.length; i++) {
            const section = sections[i];
            const title = section.querySelector('.section-title');
            if (title && title.textContent.includes('평가 요구 사항')) {
                return section;
            }
        }
        return null;
    }
    
    /**
     * 견적 계산기 삽입
     */
    insertQuotationCalculator(targetSection) {
        // 이미 삽입되었는지 확인
        if (document.getElementById('quotationCalculator')) {
            return;
        }
        
        // 견적 계산기 HTML 생성
        const calculatorHTML = this.generateQuotationCalculatorHTML();
        
        // 대상 섹션 다음에 삽입
        targetSection.insertAdjacentHTML('afterend', calculatorHTML);
        
        // 견적 계산기 초기화
        this.initializeQuotationCalculatorUI();
    }
    
    /**
     * 페이지 끝에 견적 계산기 삽입
     */
    insertQuotationCalculatorAtEnd() {
        const container = document.querySelector('.container');
        if (container && !document.getElementById('quotationCalculator')) {
            const calculatorHTML = this.generateQuotationCalculatorHTML();
            container.insertAdjacentHTML('beforeend', calculatorHTML);
            this.initializeQuotationCalculatorUI();
        }
    }
    
    /**
     * 견적 계산기 HTML 생성
     */
    generateQuotationCalculatorHTML() {
        return `
            <div class="quotation-calculator" id="quotationCalculator">
                <div class="calculator-header">
                    <h3>🔍 LRQA 스마트 견적 계산기</h3>
                    <p>ADJ_v.2.2.xlsx 기반 정확한 견적을 제공합니다</p>
                </div>
                
                <div class="calculator-form">
                    <div class="form-section">
                        <h4>기본 정보</h4>
                        
                        <div class="form-row">
                            <label class="form-label">업종 선택 *</label>
                            <select class="form-input" name="industry" required>
                                <option value="">업종을 선택하세요</option>
                                <option value="manufacturing">제조업</option>
                                <option value="construction">건설업</option>
                                <option value="chemical">화학업</option>
                                <option value="food">식품업</option>
                                <option value="service">서비스업</option>
                                <option value="healthcare">의료/헬스케어</option>
                                <option value="energy">에너지업</option>
                                <option value="transportation">운수업</option>
                            </select>
                        </div>
                        
                        <div class="form-row">
                            <label class="form-label">업무 복잡도 *</label>
                            <select class="form-input" name="complexity" required>
                                <option value="">복잡도를 선택하세요</option>
                                <option value="simple">단순</option>
                                <option value="standard">표준</option>
                                <option value="complex">복잡</option>
                                <option value="very_complex">매우 복잡</option>
                            </select>
                        </div>
                        
                        <div class="form-row">
                            <label class="form-label">기업 규모</label>
                            <select class="form-input" name="companySize">
                                <option value="">기업 규모를 선택하세요</option>
                                <option value="small">중소기업</option>
                                <option value="medium">중견기업</option>
                                <option value="large">대기업</option>
                            </select>
                        </div>
                        
                        <div class="form-row">
                            <label class="form-label">계약 유형</label>
                            <select class="form-input" name="contractType">
                                <option value="">계약 유형을 선택하세요</option>
                                <option value="single">단일 계약</option>
                                <option value="long_term">장기 계약</option>
                                <option value="renewal">갱신 계약</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h4>ISO 표준 선택</h4>
                        <div class="iso-standards-grid">
                            <label class="checkbox-item">
                                <input type="checkbox" name="isoStandards" value="iso9001">
                                <span class="checkmark"></span>
                                <span class="label-text">ISO 9001 (품질경영시스템)</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" name="isoStandards" value="iso14001">
                                <span class="checkmark"></span>
                                <span class="label-text">ISO 14001 (환경경영시스템)</span>
                            </label>
                            <label class="checkbox-item">
                                <input type="checkbox" name="isoStandards" value="iso45001">
                                <span class="checkmark"></span>
                                <span class="label-text">ISO 45001 (안전보건경영시스템)</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h4>기업 현황</h4>
                        
                        <div class="form-row">
                            <label class="form-label">총 직원 수 *</label>
                            <input type="number" class="form-input" name="totalEmployees" min="1" required>
                        </div>
                        
                        <div class="form-row">
                            <label class="form-label">사업장 수 *</label>
                            <input type="number" class="form-input" name="siteCount" min="1" value="1" required>
                        </div>
                        
                        <div class="form-row">
                            <label class="form-label">기존 인증 보유</label>
                            <div class="radio-group">
                                <label class="radio-item">
                                    <input type="radio" name="existingCertification" value="yes">
                                    <span class="radio-mark"></span>
                                    <span>예</span>
                                </label>
                                <label class="radio-item">
                                    <input type="radio" name="existingCertification" value="no">
                                    <span class="radio-mark"></span>
                                    <span>아니요</span>
                                </label>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <label class="form-label">통합 심사 진행</label>
                            <div class="radio-group">
                                <label class="radio-item">
                                    <input type="radio" name="multiStandardSystem" value="yes">
                                    <span class="radio-mark"></span>
                                    <span>예</span>
                                </label>
                                <label class="radio-item">
                                    <input type="radio" name="multiStandardSystem" value="no">
                                    <span class="radio-mark"></span>
                                    <span>아니요</span>
                                </label>
                            </div>
                        </div>
                    </div>
                    
                    <div class="calculator-actions">
                        <button type="button" class="btn-calculate" id="calculateQuotationBtn">
                            <span class="btn-icon">🧮</span>
                            견적 계산하기
                        </button>
                        <button type="button" class="btn-reset" id="resetCalculatorBtn">
                            <span class="btn-icon">🔄</span>
                            초기화
                        </button>
                    </div>
                </div>
                
                <div class="quotation-result" id="quotationResult" style="display: none;">
                    <div class="result-header">
                        <h4>견적 결과</h4>
                        <div class="result-actions">
                            <button type="button" class="btn-detail" id="showDetailBtn">
                                <span class="btn-icon">📋</span>
                                상세 보기
                            </button>
                            <button type="button" class="btn-download" id="downloadQuotationBtn">
                                <span class="btn-icon">📄</span>
                                견적서 다운로드
                            </button>
                        </div>
                    </div>
                    
                    <div class="result-summary">
                        <div class="total-amount">
                            <span class="amount-label">총 견적 금액</span>
                            <span class="amount-value" id="totalAmount">₩0</span>
                        </div>
                        <div class="amount-details">
                            <span class="original-amount" id="originalAmount"></span>
                            <span class="validity">유효기간: 30일</span>
                        </div>
                    </div>
                    
                    <div class="result-breakdown" id="resultBreakdown">
                        <!-- 견적 세부 내역이 여기에 표시됩니다 -->
                    </div>
                    
                    <div class="result-discounts" id="resultDiscounts" style="display: none;">
                        <!-- 할인 내역이 여기에 표시됩니다 -->
                    </div>
                    
                    <div class="result-notes" id="resultNotes">
                        <!-- 견적 참고사항이 여기에 표시됩니다 -->
                    </div>
                </div>
                
                <div class="calculator-loading" id="calculatorLoading" style="display: none;">
                    <div class="loading-spinner"></div>
                    <p>견적을 계산하고 있습니다...</p>
                </div>
            </div>
        `;
    }
    
    /**
     * 견적 계산기 UI 초기화
     */
    initializeQuotationCalculatorUI() {
        // 이벤트 리스너 바인딩
        this.bindCalculatorEvents();
        
        // 기존 폼과의 연동 설정
        this.syncWithExistingForm();
    }
    
    /**
     * 계산기 이벤트 리스너 바인딩
     */
    bindCalculatorEvents() {
        // 견적 계산 버튼
        const calculateBtn = document.getElementById('calculateQuotationBtn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', () => this.calculateQuotation());
        }
        
        // 초기화 버튼
        const resetBtn = document.getElementById('resetCalculatorBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetCalculator());
        }
        
        // 상세 보기 버튼
        const detailBtn = document.getElementById('showDetailBtn');
        if (detailBtn) {
            detailBtn.addEventListener('click', () => this.showDetailedQuotation());
        }
        
        // 다운로드 버튼
        const downloadBtn = document.getElementById('downloadQuotationBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadQuotation());
        }
        
        // 폼 변경 시 자동 견적 업데이트
        this.bindFormChangeEvents();
    }
    
    /**
     * 폼 변경 이벤트 바인딩
     */
    bindFormChangeEvents() {
        const formInputs = document.querySelectorAll('#quotationCalculator input, #quotationCalculator select');
        formInputs.forEach(input => {
            input.addEventListener('change', () => {
                if (this.isFormComplete()) {
                    this.autoCalculateQuotation();
                }
            });
        });
    }
    
    /**
     * 기존 폼과의 연동
     */
    integrateWithExistingForm() {
        // 기존 폼의 ISO 표준 선택과 동기화
        this.syncISOStandards();
        
        // 기존 폼의 직원 수와 동기화
        this.syncEmployeeCount();
        
        // 기존 폼의 사업장 수와 동기화
        this.syncSiteCount();
    }
    
    /**
     * ISO 표준 동기화
     */
    syncISOStandards() {
        const existingCheckboxes = document.querySelectorAll('input[name="isoStandards"]');
        const calculatorCheckboxes = document.querySelectorAll('#quotationCalculator input[name="isoStandards"]');
        
        existingCheckboxes.forEach((checkbox, index) => {
            checkbox.addEventListener('change', () => {
                if (calculatorCheckboxes[index]) {
                    calculatorCheckboxes[index].checked = checkbox.checked;
                }
            });
        });
    }
    
    /**
     * 직원 수 동기화
     */
    syncEmployeeCount() {
        const existingInput = document.querySelector('input[name="totalEmployees"]');
        const calculatorInput = document.querySelector('#quotationCalculator input[name="totalEmployees"]');
        
        if (existingInput && calculatorInput) {
            existingInput.addEventListener('input', () => {
                calculatorInput.value = existingInput.value;
            });
        }
    }
    
    /**
     * 사업장 수 동기화
     */
    syncSiteCount() {
        const existingInput = document.querySelector('input[name="siteCount"]');
        const calculatorInput = document.querySelector('#quotationCalculator input[name="siteCount"]');
        
        if (existingInput && calculatorInput) {
            existingInput.addEventListener('input', () => {
                calculatorInput.value = existingInput.value;
            });
        }
    }
    
    /**
     * 기존 폼과의 동기화
     */
    syncWithExistingForm() {
        // 기존 폼 데이터 가져오기
        const existingFormData = this.getExistingFormData();
        
        // 견적 계산기에 데이터 설정
        this.setCalculatorFormData(existingFormData);
    }
    
    /**
     * 기존 폼 데이터 가져오기
     */
    getExistingFormData() {
        const formData = {};
        
        // ISO 표준
        const isoStandards = document.querySelectorAll('input[name="isoStandards"]:checked');
        formData.isoStandards = Array.from(isoStandards).map(input => input.value);
        
        // 직원 수
        const totalEmployees = document.querySelector('input[name="totalEmployees"]');
        if (totalEmployees) {
            formData.totalEmployees = totalEmployees.value;
        }
        
        // 사업장 수
        const siteCount = document.querySelector('input[name="siteCount"]');
        if (siteCount) {
            formData.siteCount = siteCount.value;
        }
        
        return formData;
    }
    
    /**
     * 계산기 폼에 데이터 설정
     */
    setCalculatorFormData(formData) {
        // ISO 표준 설정
        if (formData.isoStandards) {
            formData.isoStandards.forEach(standard => {
                const checkbox = document.querySelector(`#quotationCalculator input[name="isoStandards"][value="${standard}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
        
        // 직원 수 설정
        if (formData.totalEmployees) {
            const input = document.querySelector('#quotationCalculator input[name="totalEmployees"]');
            if (input) {
                input.value = formData.totalEmployees;
            }
        }
        
        // 사업장 수 설정
        if (formData.siteCount) {
            const input = document.querySelector('#quotationCalculator input[name="siteCount"]');
            if (input) {
                input.value = formData.siteCount;
            }
        }
    }
    
    /**
     * 견적 계산 실행
     */
    async calculateQuotation() {
        if (!this.quotationCalculator) {
            this.showErrorMessage('견적 계산기가 초기화되지 않았습니다.');
            return;
        }
        
        try {
            await this.quotationCalculator.calculateQuotation();
        } catch (error) {
            console.error('견적 계산 실패:', error);
            this.showErrorMessage('견적 계산 중 오류가 발생했습니다.');
        }
    }
    
    /**
     * 자동 견적 계산
     */
    autoCalculateQuotation() {
        if (this.isFormComplete()) {
            setTimeout(() => {
                this.calculateQuotation();
            }, 1000);
        }
    }
    
    /**
     * 폼 완성도 확인
     */
    isFormComplete() {
        const requiredFields = ['industry', 'complexity', 'totalEmployees', 'siteCount'];
        const hasIsoStandards = document.querySelectorAll('#quotationCalculator input[name="isoStandards"]:checked').length > 0;
        
        return requiredFields.every(field => {
            const element = document.querySelector(`#quotationCalculator [name="${field}"]`);
            return element && element.value.trim();
        }) && hasIsoStandards;
    }
    
    /**
     * 견적 계산기 초기화
     */
    resetCalculator() {
        if (confirm('입력한 모든 정보를 초기화하시겠습니까?')) {
            const formInputs = document.querySelectorAll('#quotationCalculator input, #quotationCalculator select');
            formInputs.forEach(input => {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = false;
                } else {
                    input.value = '';
                }
            });
            
            const resultDiv = document.getElementById('quotationResult');
            if (resultDiv) {
                resultDiv.style.display = 'none';
            }
            
            this.showSuccessMessage('견적 계산기가 초기화되었습니다.');
        }
    }
    
    /**
     * 상세 견적 보기
     */
    showDetailedQuotation() {
        if (this.quotationCalculator) {
            this.quotationCalculator.showDetailedQuotation();
        }
    }
    
    /**
     * 견적서 다운로드
     */
    async downloadQuotation() {
        if (this.quotationCalculator) {
            await this.quotationCalculator.downloadQuotation();
        }
    }
    
    /**
     * 성공 메시지 표시
     */
    showSuccessMessage(message) {
        if (typeof window.showMessage === 'function') {
            window.showMessage('success', '성공', message);
        } else {
            alert(message);
        }
    }
    
    /**
     * 오류 메시지 표시
     */
    showErrorMessage(message) {
        if (typeof window.showMessage === 'function') {
            window.showMessage('error', '오류', message);
        } else {
            alert(message);
        }
    }
}

// 견적 시스템 매니저 인스턴스 생성
let quotationSystemManager = null;

// 페이지 로드 시 견적 시스템 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 잠시 대기 후 초기화 (다른 스크립트와의 충돌 방지)
    setTimeout(() => {
        try {
            quotationSystemManager = new QuotationSystemManager();
        } catch (error) {
            console.error('견적 시스템 매니저 초기화 실패:', error);
        }
    }, 1000);
});

// 전역으로 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuotationSystemManager;
} else {
    window.QuotationSystemManager = QuotationSystemManager;
}
