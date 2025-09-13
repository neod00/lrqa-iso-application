/**
 * LRQA 견적 시스템 초기화 및 통합
 * 메인 페이지에 견적 계산기 통합
 */
class QuotationSystemManager {
    constructor() {
        this.isInitialized = false;
        this.quotationCalculator = null;
        // 견적 시스템 표시 버튼만 자동으로 생성
        this.setupQuotationSystemButton();
        console.log('견적 시스템 매니저 생성됨 (견적 계산기는 사용자 요청 시에만 표시)');
    }

    async init() {
        if (this.isInitialized) {
            console.log('견적 시스템이 이미 초기화되어 있습니다.');
            return;
        }
        
        try {
            await this.loadDependencies();
            this.initializeQuotationCalculator();
            this.setupEventListeners();
            this.isInitialized = true;
            console.log('견적 시스템 매니저 초기화 완료');
        } catch (error) {
            console.error('견적 시스템 매니저 초기화 실패:', error);
        }
    }

    async loadDependencies() {
        try {
            // DocxGen 라이브러리 로드
            await this.loadDocxGenLibrary();
            console.log('의존성 로드 완료');
        } catch (error) {
            console.error('의존성 로드 실패:', error);
        }
    }

    async loadDocxGenLibrary() {
        return new Promise((resolve, reject) => {
            if (window.PizZip && window.Docxtemplater) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://unpkg.com/pizzip@3.1.4/dist/pizzip.min.js';
            script.onload = () => {
                const docxScript = document.createElement('script');
                docxScript.src = 'https://unpkg.com/docxtemplater@3.37.9/build/docxtemplater.js';
                docxScript.onload = resolve;
                docxScript.onerror = reject;
                document.head.appendChild(docxScript);
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    initializeQuotationCalculator() {
        try {
            this.quotationCalculator = new QuotationCalculator();
            console.log('견적 계산기 초기화 완료');
        } catch (error) {
            console.error('견적 계산기 초기화 실패:', error);
        }
    }

    setupEventListeners() {
        // 메인 폼 변경 감지 제거 - 원래 신청서 디자인 유지
        // this.setupFormMonitoring();
        
        // 견적 계산기 표시/숨김
        this.setupQuotationCalculatorToggle();
        
        // 견적 시스템 표시 버튼 이벤트 리스너
        this.setupQuotationSystemButton();
    }

    // 메인 폼 변경 감지하여 견적서 초안 요청 버튼 표시/숨김
    setupFormMonitoring() {
        const form = document.querySelector('#isoApplicationForm');
        if (form) {
            form.addEventListener('change', () => {
                this.checkApplicationCompletion();
            });
        }
    }

    // 견적 계산기 표시/숨김 설정
    setupQuotationCalculatorToggle() {
        // 견적 계산기 토글 버튼이 있다면 이벤트 바인딩
        const toggleBtn = document.querySelector('.toggle-quotation-calculator');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleQuotationCalculator();
            });
        }
    }

    // 견적 계산기 토글
    toggleQuotationCalculator() {
        const calculator = document.querySelector('.quotation-calculator');
        if (calculator) {
            if (calculator.style.display === 'none' || calculator.style.display === '') {
                calculator.style.display = 'block';
            } else {
                calculator.style.display = 'none';
            }
        }
    }

    // 신청서 완료 상태 확인
    checkApplicationCompletion() {
        const requiredFields = [
            'companyName', 'isoStandards', 'employeeCount', 
            'siteCount', 'industry', 'complexity'
        ];
        
        const formData = this.getExistingFormData();
        const isComplete = requiredFields.every(field => {
            if (field === 'isoStandards') {
                return formData[field] && formData[field].length > 0;
            }
            return formData[field] && formData[field].trim() !== '';
        });
        
        if (isComplete) {
            this.showDraftRequestSection();
        }
        
        return isComplete;
    }

    // 견적서 초안 요청 섹션 표시
    showDraftRequestSection() {
        const draftSection = document.querySelector('.draft-request-section');
        if (draftSection) {
            draftSection.style.display = 'block';
        }
    }

    // 견적 계산기 UI를 메인 페이지에 삽입
    async showQuotationCalculator() {
        try {
            // 견적 계산기가 이미 표시되어 있는지 확인
            const existingCalculator = document.querySelector('.quotation-calculator');
            if (existingCalculator) {
                console.log('견적 계산기가 이미 표시되어 있습니다.');
                return;
            }
            
            // 견적 시스템이 초기화되지 않은 경우 초기화
            if (!this.isInitialized) {
                console.log('견적 시스템 초기화 중...');
                await this.init();
            }
            
            const targetSection = this.findTargetSection();
            if (targetSection) {
                this.insertQuotationCalculator(targetSection);
            } else {
                this.insertQuotationCalculatorAtEnd();
            }
        } catch (error) {
            console.error('견적 계산기 표시 실패:', error);
        }
    }

    // 대상 섹션 찾기
    findTargetSection() {
        // "평가 요구 사항" 섹션을 찾음
        const sections = document.querySelectorAll('.form-section, .section');
        for (let section of sections) {
            const heading = section.querySelector('h3, h4');
            if (heading && heading.textContent.includes('평가 요구 사항')) {
                return section;
            }
        }
        return null;
    }

    // 견적 계산기를 대상 섹션 다음에 삽입
    insertQuotationCalculator(targetSection) {
        try {
            const calculatorHTML = this.generateQuotationCalculatorHTML();
            targetSection.insertAdjacentHTML('afterend', calculatorHTML);
            this.initializeQuotationCalculatorUI();
            console.log('견적 계산기 삽입 완료');
        } catch (error) {
            console.error('견적 계산기 삽입 실패:', error);
        }
    }

    // 견적 계산기를 페이지 끝에 삽입
    insertQuotationCalculatorAtEnd() {
        try {
            const calculatorHTML = this.generateQuotationCalculatorHTML();
            const container = document.querySelector('.container, main, #main');
            if (container) {
                container.insertAdjacentHTML('beforeend', calculatorHTML);
                this.initializeQuotationCalculatorUI();
                console.log('견적 계산기 페이지 끝에 삽입 완료');
            }
        } catch (error) {
            console.error('견적 계산기 삽입 실패:', error);
        }
    }

    // 견적 계산기 HTML 생성
    generateQuotationCalculatorHTML() {
        if (this.quotationCalculator) {
            return this.quotationCalculator.createCalculatorUI();
        }
        return '<div class="quotation-calculator">견적 계산기를 로드할 수 없습니다.</div>';
    }

    // 견적 계산기 UI 초기화
    initializeQuotationCalculatorUI() {
        // 견적 계산기가 초기화되지 않았다면 먼저 초기화
        if (!this.quotationCalculator) {
            this.initializeQuotationCalculator();
        }
        
        // 견적 계산기 UI를 동적으로 삽입
        const calculator = this.quotationCalculator.createCalculatorUI();
        
        // 견적 계산기를 숨김 상태로 설정
        calculator.style.display = 'none';
        
        // 메인 컨테이너에 견적 계산기 삽입
        const mainContainer = document.querySelector('.main-container') || document.body;
        mainContainer.appendChild(calculator);
        
        // 견적 계산기 표시 버튼에 이벤트 리스너 추가
        const showButton = document.querySelector('.quotation-show-btn');
        if (showButton) {
            showButton.addEventListener('click', () => {
                if (calculator.style.display === 'none') {
                    calculator.style.display = 'block';
                    // 견적 계산기를 표시할 때 신청서 데이터로 자동 입력
                    this.quotationCalculator.populateFormFromApplication();
                } else {
                    calculator.style.display = 'none';
                }
            });
        }
        
        // 견적 계산기 초기화
        console.log('견적 계산기 초기화 완료');
    }

    // 견적 계산기 이벤트 바인딩
    bindCalculatorEvents() {
        if (this.quotationCalculator) {
            // 견적 계산기 내부 이벤트는 QuotationCalculator에서 처리
            // 여기서는 메인 폼과의 연동 이벤트만 처리
        }
    }

    // 기존 폼과 견적 계산기 연동
    integrateWithExistingForm() {
        // 기존 폼 데이터를 견적 계산기에 동기화
        this.syncWithExistingForm();
        
        // 견적 계산기 폼 변경 시 메인 폼과 동기화
        this.bindFormChangeEvents();
    }

    // 기존 폼 데이터를 견적 계산기에 동기화
    syncWithExistingForm() {
        try {
            const existingData = this.getExistingFormData();
            if (existingData && this.quotationCalculator) {
                this.setCalculatorFormData(existingData);
            }
        } catch (error) {
            console.error('폼 데이터 동기화 실패:', error);
        }
    }

    // 견적 계산기 폼에 데이터 설정
    setCalculatorFormData(formData) {
        if (!this.quotationCalculator) return;

        try {
            // 회사명 동기화
            this.syncCompanyName(formData.companyName);
            
            // ISO 표준 동기화
            this.syncISOStandards(formData.isoStandards);
            
            // 직원 수 동기화
            this.syncEmployeeCount(formData.employeeCount);
            
            // 사업장 수 동기화
            this.syncSiteCount(formData.siteCount);
            
            // 업종 동기화
            this.syncIndustry(formData.industry);
            
            // 복잡도 동기화
            this.syncComplexity(formData.complexity);
            
        } catch (error) {
            console.error('견적 계산기 폼 데이터 설정 실패:', error);
        }
    }

    // 회사명 동기화
    syncCompanyName(companyName) {
        if (companyName) {
            const input = document.querySelector('.quotation-calculator input[name="companyName"]');
            if (input) {
                input.value = companyName;
            }
        }
    }

    // ISO 표준 동기화
    syncISOStandards(isoStandards) {
        if (isoStandards && Array.isArray(isoStandards)) {
            isoStandards.forEach(standard => {
                const checkbox = document.querySelector(`.quotation-calculator input[value="${standard}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
    }

    // 직원 수 동기화
    syncEmployeeCount(employeeCount) {
        if (employeeCount) {
            const select = document.querySelector('.quotation-calculator select[name="employeeCount"]');
            if (select) {
                select.value = employeeCount;
            }
        }
    }

    // 사업장 수 동기화
    syncSiteCount(siteCount) {
        if (siteCount) {
            const select = document.querySelector('.quotation-calculator select[name="siteCount"]');
            if (select) {
                select.value = siteCount;
            }
        }
    }

    // 업종 동기화
    syncIndustry(industry) {
        if (industry) {
            const select = document.querySelector('.quotation-calculator select[name="industry"]');
            if (select) {
                select.value = industry;
            }
        }
    }

    // 복잡도 동기화
    syncComplexity(complexity) {
        if (complexity) {
            const select = document.querySelector('.quotation-calculator select[name="complexity"]');
            if (select) {
                select.value = complexity;
            }
        }
    }

    // 폼 변경 이벤트 바인딩
    bindFormChangeEvents() {
        const calculatorForm = document.querySelector('.quotation-calculator form');
        if (calculatorForm) {
            calculatorForm.addEventListener('change', () => {
                // 견적 계산기 폼 변경 시 메인 폼과 동기화
                this.syncToMainForm();
            });
        }
    }

    // 견적 계산기 데이터를 메인 폼에 동기화
    syncToMainForm() {
        try {
            const calculatorData = this.getCalculatorFormData();
            if (calculatorData) {
                this.updateMainForm(calculatorData);
            }
        } catch (error) {
            console.error('메인 폼 동기화 실패:', error);
        }
    }

    // 견적 계산기 폼 데이터 수집
    getCalculatorFormData() {
        if (!this.quotationCalculator) return null;
        
        try {
            return this.quotationCalculator.collectFormData();
        } catch (error) {
            console.error('견적 계산기 폼 데이터 수집 실패:', error);
            return null;
        }
    }

    // 메인 폼 업데이트
    updateMainForm(calculatorData) {
        try {
            // 메인 폼의 해당 필드들을 업데이트
            if (calculatorData.companyName) {
                const mainCompanyInput = document.querySelector('#companyName, input[name="companyName"]');
                if (mainCompanyInput) {
                    mainCompanyInput.value = calculatorData.companyName;
                }
            }
            
            // ISO 표준 업데이트
            if (calculatorData.isoStandards) {
                calculatorData.isoStandards.forEach(standard => {
                    const mainCheckbox = document.querySelector(`input[value="${standard}"]`);
                    if (mainCheckbox) {
                        mainCheckbox.checked = true;
                    }
                });
            }
            
        } catch (error) {
            console.error('메인 폼 업데이트 실패:', error);
        }
    }

    // 기존 폼 데이터 수집
    getExistingFormData() {
        try {
            const form = document.querySelector('#isoApplicationForm, form');
            if (!form) return null;

            const formData = new FormData(form);
            const data = {};

            for (let [key, value] of formData.entries()) {
                if (key === 'isoStandards' || key === 'additionalServices') {
                    if (!data[key]) data[key] = [];
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }

            return data;
        } catch (error) {
            console.error('기존 폼 데이터 수집 실패:', error);
            return null;
        }
    }

    // 견적 계산 실행
    calculateQuotation() {
        if (this.quotationCalculator) {
            return this.quotationCalculator.calculateQuotation();
        }
        return null;
    }

    // 자동 견적 계산
    autoCalculateQuotation() {
        if (this.quotationCalculator) {
            this.quotationCalculator.autoCalculateQuotation();
        }
    }

    // 폼 완성도 확인
    isFormComplete() {
        if (this.quotationCalculator) {
            const formData = this.quotationCalculator.collectFormData();
            return this.quotationCalculator.isFormComplete(formData);
        }
        return false;
    }

    // 견적 계산기 초기화
    resetCalculator() {
        if (this.quotationCalculator) {
            this.quotationCalculator.resetCalculator();
        }
    }

    // 상세 견적 보기
    showDetailedQuotation() {
        if (this.quotationCalculator) {
            this.quotationCalculator.showDetailedQuotation();
        }
    }

    // 견적서 다운로드
    downloadQuotation() {
        if (this.quotationCalculator) {
            this.quotationCalculator.downloadLRQADocument();
        }
    }

    // 성공 메시지 표시
    showSuccessMessage(message) {
        if (this.quotationCalculator) {
            this.quotationCalculator.showMessage('success', '성공', message);
        }
    }

    // 오류 메시지 표시
    showErrorMessage(message) {
        if (this.quotationCalculator) {
            this.quotationCalculator.showMessage('error', '오류', message);
        }
    }

    // 견적 계산기 표시 상태 확인
    isCalculatorVisible() {
        const calculator = document.querySelector('.quotation-calculator');
        return calculator && calculator.style.display !== 'none';
    }

    // 견적 계산기 숨기기
    hideQuotationCalculator() {
        try {
            const calculator = document.querySelector('.quotation-calculator');
            if (calculator) {
                calculator.remove();
                console.log('견적 계산기 숨김 완료');
            }
        } catch (error) {
            console.error('견적 계산기 숨김 실패:', error);
        }
    }

    // 견적 계산기 표시
    showCalculator() {
        const calculator = document.querySelector('.quotation-calculator');
        if (calculator) {
            calculator.style.display = 'block';
        }
    }

    // 견적 시스템 표시 버튼 이벤트 리스너 설정
    setupQuotationSystemButton() {
        // 페이지 로드 후 버튼에 이벤트 리스너 추가
        setTimeout(() => {
            let showButton = document.getElementById('showQuotationCalculatorBtn');
            
            // 버튼이 없으면 자동으로 생성
            if (!showButton) {
                console.log('견적 시스템 표시 버튼을 찾을 수 없습니다. 자동으로 생성합니다.');
                showButton = this.createQuotationSystemButton();
            }
            
            if (showButton) {
                showButton.addEventListener('click', () => {
                    this.showQuotationCalculator();
                });
                console.log('견적 시스템 표시 버튼 이벤트 리스너 설정 완료');
            }
        }, 2000); // 페이지 로드 후 2초 대기
    }

    // 견적 시스템 표시 버튼 생성
    createQuotationSystemButton() {
        try {
            // "평가 요구 사항" 섹션을 찾아서 버튼 추가
            const targetSection = this.findTargetSection();
            if (targetSection) {
                const buttonHTML = `
                    <div class="form-row" style="margin-top: 20px;">
                        <button type="button" class="btn btn-primary" id="showQuotationCalculatorBtn" style="background-color: #00d4aa; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 14px;">
                            🧮 견적 계산기 표시
                        </button>
                    </div>
                `;
                targetSection.insertAdjacentHTML('beforeend', buttonHTML);
                
                const button = document.getElementById('showQuotationCalculatorBtn');
                console.log('견적 시스템 표시 버튼이 자동으로 생성되었습니다.');
                return button;
            }
        } catch (error) {
            console.error('견적 시스템 표시 버튼 생성 실패:', error);
        }
        return null;
    }
}

// 견적 시스템 매니저 인스턴스 생성
let quotationSystemManager = null;

// DOM 로드 완료 후 견적 시스템 초기화
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        try {
            quotationSystemManager = new QuotationSystemManager();
            
            // 견적 계산기 자동 표시하지 않음 - 사용자가 명시적으로 요청할 때만 표시
            console.log('견적 시스템 매니저 초기화 완료. 견적 계산기는 사용자 요청 시에만 표시됩니다.');
            
        } catch (error) {
            console.error('견적 시스템 매니저 초기화 실패:', error);
        }
    }, 1000);
});

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuotationSystemManager;
} else {
    window.QuotationSystemManager = QuotationSystemManager;
}
