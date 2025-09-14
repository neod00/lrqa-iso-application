/**
 * LRQA 견적 계산기 UI 컴포넌트
 * 견적 계산 및 결과 표시 기능
 */
class QuotationCalculator {
    constructor() {
        this.quotationSystem = new SmartQuotationSystem(); // 기존 엔진 (백업용)
        this.adjEngine = new ADJv22QuotationEngine(); // 새로운 ADJ v2.2 엔진
        this.wordGenerator = new WordDocumentGenerator();
        this.currentQuotation = null;
        this.currentFormData = null;
        this.quotationStatus = 'draft'; // 'draft', 'approved', 'sent'
        this.useADJEngine = true; // ADJ v2.2 엔진 사용 여부
        this.init();
    }

    init() {
        console.log('=== QuotationCalculator init() 메서드 호출됨 ===');
        this.createCalculatorUI();
        console.log('=== createCalculatorUI 완료 ===');
        this.bindEvents();
        console.log('=== bindEvents 완료 ===');
        this.bindFormChangeEvents();
        console.log('=== bindFormChangeEvents 완료 ===');
        console.log('=== QuotationCalculator 초기화 완료 ===');
    }

    // 견적 계산기 초기화 메서드 추가
    initialize() {
        console.log('견적 계산기 초기화 완료');
    }

    createCalculatorUI() {
        const calculatorDiv = document.createElement('div');
        calculatorDiv.className = 'quotation-calculator';
        calculatorDiv.style.display = 'none';
        calculatorDiv.innerHTML = `
                <div class="calculator-header">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3>📋 LRQA 스마트 견적 계산기</h3>
                            <p class="calculator-description">
                                신청서 작성 완료 후 견적서 초안을 확인할 수 있습니다.<br>
                                <strong>정식 견적서는 LRQA 담당자 승인 후 발송됩니다.</strong>
                            </p>
                        </div>
                        <button type="button" class="btn btn-secondary" id="closeQuotationCalculatorBtn" style="background-color: #6c757d; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 12px; margin-left: 10px;">
                            ✕ 닫기
                        </button>
                    </div>
                </div>
                
                <!-- 견적 계산 폼 -->
                <form class="quotation-form">
                    <div class="form-section">
                        <h4>기본 정보</h4>
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">회사명</label>
                                <input type="text" class="form-input" name="companyName" placeholder="신청서에서 자동 입력" readonly>
                            </div>
                            <div class="form-group">
                                <label class="form-label">직원 수</label>
                                <select class="form-input" name="employeeCount" disabled>
                                    <option value="">선택하세요</option>
                                    <option value="1-10">1-10명</option>
                                    <option value="11-50">11-50명</option>
                                    <option value="51-100">51-100명</option>
                                    <option value="101-200">101-200명</option>
                                    <option value="201-500">201-500명</option>
                                    <option value="500+">500명 이상</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">사업장 수</label>
                                <select class="form-input" name="siteCount" disabled>
                                    <option value="">선택하세요</option>
                                    <option value="1">1개소</option>
                                    <option value="2-5">2-5개소</option>
                                    <option value="6-10">6-10개소</option>
                                    <option value="10+">10개소 이상</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">업종</label>
                                <select class="form-input" name="industry" disabled>
                                    <option value="">선택하세요</option>
                                    <option value="manufacturing">제조업</option>
                                    <option value="construction">건설업</option>
                                    <option value="service">서비스업</option>
                                    <option value="trade">무역업</option>
                                    <option value="other">기타</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">업무 복잡도</label>
                                <select class="form-input" name="complexity" disabled>
                                    <option value="">선택하세요</option>
                                    <option value="low">낮음</option>
                                    <option value="medium">보통</option>
                                    <option value="high">높음</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">기존 인증 현황</label>
                                <select class="form-input" name="existingCertifications" disabled>
                                    <option value="">선택하세요</option>
                                    <option value="none">없음</option>
                                    <option value="partial">일부 보유</option>
                                    <option value="full">완전 보유</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-section">
                        <h4>ISO 표준 선택 (신청서 기반 자동 선택)</h4>
                        <div class="iso-standards-grid">
                            <div class="checkbox-item">
                                <input type="checkbox" id="iso9001" name="isoStandards" value="9001" disabled>
                                <label for="iso9001">ISO 9001 (품질경영시스템)</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="iso14001" name="isoStandards" value="14001" disabled>
                                <label for="iso14001">ISO 14001 (환경경영시스템)</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="iso45001" name="isoStandards" value="45001" disabled>
                                <label for="iso45001">ISO 45001 (직업건강안전경영시스템)</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="iso27001" name="isoStandards" value="27001" disabled>
                                <label for="iso27001">ISO 27001 (정보보안경영시스템)</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="iso22000" name="isoStandards" value="22000" disabled>
                                <label for="iso14001">ISO 22000 (식품안전경영시스템)</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="iso13485" name="isoStandards" value="13485" disabled>
                                <label for="iso13485">ISO 13485 (의료기기 품질경영시스템)</label>
                            </div>
                        </div>
                    </div>
                    

                </form>
                
                <!-- 견적 계산 버튼 -->
                <div class="calculate-section">
                    <button type="button" class="btn btn-primary btn-calculate" id="calculateQuotationBtn">
                        🧮 견적 계산하기
                    </button>
                    <div class="calculation-note">
                        <small>신청서 데이터를 기반으로 자동 계산됩니다.</small>
                    </div>
                </div>
                
                <!-- 견적서 초안 요청 버튼 -->
                <div class="draft-request-section" style="display: none;">
                    <div class="alert alert-info">
                        <strong>📋 신청서 작성 완료!</strong><br>
                        견적서 초안을 확인하시겠습니까?
                    </div>
                    <button type="button" class="btn btn-primary btn-request-draft">
                        📋 견적서 초안 요청
                    </button>
                </div>
                
                <!-- 견적서 초안 결과 (사용자용 약식) -->
                <div class="quotation-draft-result" style="display: none;">
                    <div class="draft-header">
                        <h4>📋 견적서 초안 (참고용)</h4>
                        <div class="draft-status">
                            <span class="status-badge status-draft">초안</span>
                            <small>이 견적서는 참고용이며, 정식 견적서가 아닙니다.</small>
                        </div>
                    </div>
                    
                    <div class="draft-summary">
                        <div class="summary-card">
                            <div class="summary-header">
                                <h5>견적 요약</h5>
                            </div>
                            <div class="summary-content">
                                <div class="summary-item">
                                    <span class="label">총 견적 금액:</span>
                                    <span class="value total-amount">₩0</span>
                                </div>
                                <div class="summary-item">
                                    <span class="label">기본 심사비:</span>
                                    <span class="value base-audit-cost">-</span>
                                </div>
                                <div class="summary-item">
                                    <span class="label">제경비 (10%):</span>
                                    <span class="value overhead-cost">-</span>
                                </div>
                                <div class="summary-item">
                                    <span class="label">예상 심사일수:</span>
                                    <span class="value total-audit-days">-</span>
                                </div>
                                <div class="summary-item">
                                    <span class="label">선택된 ISO 표준:</span>
                                    <span class="value selected-standards">-</span>
                                </div>
                                <div class="summary-item">
                                    <span class="label">적용 할인:</span>
                                    <span class="value applied-discounts">-</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="calculation-formula">
                            <h5>계산 공식</h5>
                            <div class="formula-card">
                                <div class="formula-main">
                                    <strong>총 견적 금액 = 심사일수 × 1,450,000원 + 제경비(총 심사비의 10%)</strong>
                                </div>
                                <div class="formula-breakdown">
                                    <div class="formula-item">
                                        <span class="formula-label">기본 심사비:</span>
                                        <span class="formula-value">심사일수 × 1,450,000원</span>
                                    </div>
                                    <div class="formula-item">
                                        <span class="formula-label">제경비:</span>
                                        <span class="formula-value">기본 심사비 × 10%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="draft-breakdown">
                            <h5>견적 상세 내역</h5>
                            <div class="breakdown-items">
                                <!-- 견적 상세 내역이 여기에 동적으로 생성됩니다 -->
                            </div>
                        </div>
                        
                                                 <div class="draft-notes">
                             <h5>참고사항</h5>
                             <ul class="notes-list">
                                 <li>이 견적서는 참고용이며, 정식 견적서가 아닙니다.</li>
                                 <li>실제 견적서는 LRQA 담당자 검토 후 발송됩니다.</li>
                                 <li>견적서 초안과 실제 견적서는 다를 수 있습니다.</li>
                                 <li>심사일수는 조직 규모와 복잡도에 따라 조정될 수 있습니다.</li>
                                 <li>문의사항이 있으시면 LRQA 담당자에게 연락하시기 바랍니다.</li>
                             </ul>
                         </div>
                    </div>
                    
                    <div class="draft-actions">
                        <button type="button" class="btn btn-secondary btn-edit-draft">
                            ✏️ 견적 수정
                        </button>
                        <button type="button" class="btn btn-info btn-generate-lrqa-document">
                            📋 LRQA 담당자용 정식 견적서 생성
                        </button>
                    </div>
                    
                    <div class="formal-quotation-info">
                        <div class="alert alert-warning">
                            <strong>⚠️ 정식 견적서 안내</strong><br>
                            • 정식 견적서는 LRQA 담당자 검토 후 승인됩니다<br>
                            • 승인된 견적서는 별도로 발송됩니다<br>
                            • 견적서 초안과 실제 견적서는 다를 수 있습니다
                        </div>
                    </div>
                </div>
                
                <!-- 정식 견적서 상태 -->
                <div class="formal-quotation-status" style="display: none;">
                    <div class="status-header">
                        <h4>📋 정식 견적서 상태</h4>
                    </div>
                    
                    <div class="status-timeline">
                        <div class="timeline-item completed">
                            <div class="timeline-icon">✅</div>
                            <div class="timeline-content">
                                <strong>견적서 초안 제출 완료</strong>
                                <small>${new Date().toLocaleDateString()}</small>
                            </div>
                        </div>
                        
                        <div class="timeline-item pending">
                            <div class="timeline-icon">⏳</div>
                            <div class="timeline-content">
                                <strong>LRQA 담당자 검토 중</strong>
                                <small>검토 완료 예정: 3-5 영업일</small>
                            </div>
                        </div>
                        
                        <div class="timeline-item">
                            <div class="timeline-icon">📧</div>
                            <div class="timeline-content">
                                <strong>정식 견적서 발송</strong>
                                <small>승인 후 이메일로 발송</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- LRQA 담당자용 정식 견적서 다운로드 -->
                <div class="lrqa-document-section" style="display: none;">
                    <div class="alert alert-success">
                        <strong>📋 LRQA 담당자용 정식 견적서 생성 완료</strong><br>
                        아래 버튼을 클릭하여 워드 문서를 다운로드하세요.
                    </div>
                    <button type="button" class="btn btn-success btn-download-lrqa-document">
                        📥 LRQA 담당자용 정식 견적서 다운로드 (.docx)
                    </button>
                    <div class="lrqa-notes">
                        <h5>LRQA 담당자 안내사항</h5>
                        <ul class="notes-list">
                            <li>다운로드된 워드 문서를 검토하고 필요시 수정하세요.</li>
                            <li>수정 완료 후 고객에게 정식 견적서로 발송하세요.</li>
                            <li>견적서 번호와 승인 정보를 포함하여 발송하세요.</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        return calculatorDiv;
    }

    bindEvents() {
        console.log('=== bindEvents 메서드 호출됨 ===');
        
        // 견적 계산
        document.addEventListener('click', (e) => {
            console.log('클릭된 요소:', e.target);
            console.log('클릭된 요소의 클래스:', e.target.className);
            
            if (e.target.classList.contains('btn-calculate')) {
                console.log('견적 계산하기 버튼 클릭됨!');
                this.handleCalculateQuotation();
            }
            
            if (e.target.classList.contains('btn-request-draft')) {
                this.requestDraftQuotation();
            }
            
            if (e.target.classList.contains('btn-edit-draft')) {
                this.editDraftQuotation();
            }
            
            if (e.target.classList.contains('btn-generate-lrqa-document')) {
                this.generateLRQADocument();
            }
            
            if (e.target.classList.contains('btn-download-lrqa-document')) {
                this.downloadLRQADocument();
            }
            
            // 견적 계산기 닫기
            if (e.target.id === 'closeQuotationCalculatorBtn') {
                this.closeQuotationCalculator();
            }
        });
        
        console.log('=== 이벤트 리스너 등록 완료 ===');
    }

    bindFormChangeEvents() {
        const form = document.querySelector('.quotation-calculator form');
        if (form) {
            form.addEventListener('change', () => {
                this.autoCalculateQuotation();
            });
        }
    }

    async calculateQuotation() {
        try {
            const formData = this.collectFormData();
            if (!this.isFormComplete(formData)) {
                this.showMessage('warning', '입력 정보 부족', '모든 필수 항목을 입력해주세요.');
                return null;
            }

            this.currentFormData = formData;
            
            // ADJ v2.2 엔진 사용 여부 확인
            if (this.useADJEngine) {
                console.log('ADJ v2.2 엔진으로 견적 계산');
                try {
                    const quotation = await this.adjEngine.calculateQuotation(formData);
                    if (quotation && quotation.success) {
                        console.log('ADJ v2.2 계산 성공');
                        return quotation;
                    } else {
                        throw new Error('ADJ v2.2 엔진 계산 실패');
                    }
                } catch (adjError) {
                    console.warn('ADJ v2.2 엔진 실패, 기존 엔진으로 폴백:', adjError);
                    // 폴백: 기존 엔진 사용
                    const quotation = this.quotationSystem.calculateQuotation(formData);
                    quotation.engine = 'Fallback Engine';
                    return quotation;
                }
            } else {
                console.log('기존 엔진으로 견적 계산');
                const quotation = this.quotationSystem.calculateQuotation(formData);
                quotation.engine = 'Legacy Engine';
                return quotation;
            }
        } catch (error) {
            console.error('견적 계산 실패:', error);
            this.showMessage('error', '오류 발생', '견적 계산 중 오류가 발생했습니다.');
            return null;
        }
    }

    autoCalculateQuotation() {
        // 실시간 견적 계산 (사용자에게는 표시하지 않음)
        this.calculateQuotation();
    }
    
    async handleCalculateQuotation() {
        try {
            const quotation = await this.calculateQuotation();
            if (quotation) {
                this.showQuotationResult(quotation);
                this.showDraftRequestSection();
            }
        } catch (error) {
            console.error('견적 계산 처리 실패:', error);
            this.showMessage('error', '오류 발생', '견적 계산 중 오류가 발생했습니다.');
        }
    }

    validateForm() {
        const form = document.querySelector('.quotation-calculator form');
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                isValid = false;
            } else {
                field.classList.remove('error');
            }
        });

        return isValid;
    }

    getFieldLabel(fieldName) {
        const labels = {
            companyName: '회사명',
            employeeCount: '직원 수',
            siteCount: '사업장 수',
            industry: '업종',
            complexity: '업무 복잡도',
            existingCertifications: '기존 인증 현황',
            isoStandards: 'ISO 표준',
            additionalServices: '추가 서비스'
        };
        return labels[fieldName] || fieldName;
    }

    collectFormData() {
        const data = {};
        
        // 회사명
        const companyNameInput = document.querySelector('.quotation-calculator input[name="companyName"]');
        if (companyNameInput) {
            data.companyName = companyNameInput.value;
            console.log('회사명 수집됨:', data.companyName);
        }
        
        // 직원 수
        const employeeCountSelect = document.querySelector('.quotation-calculator select[name="employeeCount"]');
        if (employeeCountSelect) {
            data.employeeCount = employeeCountSelect.value;
            console.log('직원 수 수집됨:', data.employeeCount);
        }
        
        // 사업장 수
        const siteCountSelect = document.querySelector('.quotation-calculator select[name="siteCount"]');
        if (siteCountSelect) {
            data.siteCount = siteCountSelect.value;
            console.log('사업장 수 수집됨:', data.siteCount);
        }
        
        // ISO 표준
        const isoStandards = document.querySelectorAll('.quotation-calculator input[name="isoStandards"]:checked');
        if (isoStandards.length > 0) {
            data.isoStandards = Array.from(isoStandards).map(input => input.value);
            console.log('ISO 표준 수집됨:', data.isoStandards);
        }
        
        // 업종
        const industrySelect = document.querySelector('.quotation-calculator select[name="industry"]');
        if (industrySelect) {
            data.industry = industrySelect.value;
            console.log('업종 수집됨:', data.industry);
        }
        
        // 복잡도
        const complexitySelect = document.querySelector('.quotation-calculator select[name="complexity"]');
        if (complexitySelect) {
            data.complexity = complexitySelect.value;
            console.log('복잡도 수집됨:', data.complexity);
        }
        
        // 기존 인증 현황
        const existingCertificationsSelect = document.querySelector('.quotation-calculator select[name="existingCertifications"]');
        if (existingCertificationsSelect) {
            data.existingCertifications = existingCertificationsSelect.value;
            console.log('기존 인증 현황 수집됨:', data.existingCertifications);
        }
        
        console.log('=== 견적 계산기 폼에서 수집된 최종 데이터 ===');
        console.log('회사명:', data.companyName);
        console.log('직원 수:', data.employeeCount);
        console.log('사업장 수:', data.siteCount);
        console.log('ISO 표준:', data.isoStandards);
        console.log('업종:', data.industry);
        console.log('복잡도:', data.complexity);
        console.log('기존 인증 현황:', data.existingCertifications);
        console.log('===============================');
        
        return data;
    }

    // 신청서 데이터를 기반으로 견적 계산기 폼을 자동으로 채움
    populateFormFromApplication() {
        // 신청서에서 데이터 수집
        const applicationData = this.collectApplicationData();
        console.log('수집된 신청서 데이터:', applicationData);
        
        // 견적 계산기 폼에 데이터 적용
        this.populateCalculatorForm(applicationData);
        
        // 데이터가 제대로 적용되었는지 확인
        setTimeout(() => {
            console.log('견적 계산기 폼 상태 확인:');
            console.log('회사명:', document.querySelector('.quotation-calculator input[name="companyName"]')?.value);
            console.log('직원 수:', document.querySelector('.quotation-calculator select[name="employeeCount"]')?.value);
            console.log('사업장 수:', document.querySelector('.quotation-calculator select[name="siteCount"]')?.value);
            console.log('ISO 표준:', document.querySelectorAll('.quotation-calculator input[name="isoStandards"]:checked').length);
        }, 100);
    }

    // 신청서에서 데이터 수집
    collectApplicationData() {
        const data = {};
        
        // 회사명
        const companyNameInput = document.querySelector('input[name="companyNameKo"]');
        if (companyNameInput) {
            data.companyName = companyNameInput.value;
            console.log('회사명 수집됨:', data.companyName);
        }
        
        // 직원 수
        const employeeCountInput = document.querySelector('input[name="totalEmployees"]');
        if (employeeCountInput && employeeCountInput.value) {
            data.employeeCount = this.mapEmployeeCount(employeeCountInput.value);
            console.log('직원 수 수집됨:', data.employeeCount);
        }
        
        // 사업장 수
        const siteCountInput = document.querySelector('input[name="siteCount"]');
        if (siteCountInput && siteCountInput.value) {
            data.siteCount = siteCountInput.value;
            console.log('사업장 수 수집됨:', data.siteCount);
        } else {
            // 기본값으로 1개소 설정
            data.siteCount = '1';
            console.log('사업장 수 기본값 설정:', data.siteCount);
        }
        
        // ISO 표준 선택 - 신청서의 ISO 표준 체크박스 찾기
        const isoStandards = document.querySelectorAll('input[name="isoStandards"]:checked');
        if (isoStandards.length > 0) {
            data.isoStandards = Array.from(isoStandards).map(input => {
                // ISO 표준 값을 견적 계산기 형식으로 변환
                const value = input.value;
                if (value === 'iso9001') return '9001';
                if (value === 'iso14001') return '14001';
                if (value === 'iso45001') return '45001';
                return value;
            });
            console.log('ISO 표준 수집됨:', data.isoStandards);
        } else {
            // ISO 표준이 선택되지 않은 경우 기본값 설정
            data.isoStandards = ['9001'];
            console.log('ISO 표준 기본값 설정:', data.isoStandards);
        }
        
        // 업종 기본값 설정
        data.industry = 'manufacturing';
        
        // 복잡도 기본값 설정
        data.complexity = 'medium';
        
        // 기존 인증 현황 기본값 설정
        data.existingCertifications = 'none';
        
        console.log('수집된 신청서 데이터:', data);
        return data;
    }

    // 직원 수 매핑
    mapEmployeeCount(value) {
        // 숫자 값을 범위로 변환
        const numValue = parseInt(value);
        if (numValue <= 10) return '1-10';
        if (numValue <= 50) return '11-50';
        if (numValue <= 100) return '51-100';
        if (numValue <= 200) return '101-200';
        if (numValue <= 500) return '201-500';
        return '500+';
    }

    // 사업장 수 매핑
    mapSiteCount(value) {
        const mapping = {
            '1': '1',
            '2-5': '2-5',
            '6-10': '6-10',
            '10+': '10+'
        };
        return mapping[value] || value;
    }

    // 견적 계산기 폼에 데이터 적용
    populateCalculatorForm(data) {
        console.log('견적 계산기 폼에 데이터 적용 중:', data);
        
        // 회사명
        const companyNameInput = document.querySelector('.quotation-calculator input[name="companyName"]');
        if (companyNameInput && data.companyName) {
            companyNameInput.value = data.companyName;
            console.log('회사명 설정됨:', data.companyName);
        }
        
        // 직원 수
        const employeeCountSelect = document.querySelector('.quotation-calculator select[name="employeeCount"]');
        if (employeeCountSelect && data.employeeCount) {
            employeeCountSelect.value = data.employeeCount;
            console.log('직원 수 설정됨:', data.employeeCount);
        }
        
        // 사업장 수
        const siteCountSelect = document.querySelector('.quotation-calculator select[name="siteCount"]');
        if (siteCountSelect && data.siteCount) {
            siteCountSelect.value = data.siteCount;
            console.log('사업장 수 설정됨:', data.siteCount);
        }
        
        // 업종
        const industrySelect = document.querySelector('.quotation-calculator select[name="industry"]');
        if (industrySelect && data.industry) {
            industrySelect.value = data.industry;
            console.log('업종 설정됨:', data.industry);
        }
        
        // 복잡도
        const complexitySelect = document.querySelector('.quotation-calculator select[name="complexity"]');
        if (complexitySelect && data.complexity) {
            complexitySelect.value = data.complexity;
            console.log('복잡도 설정됨:', data.complexity);
        }
        
        // 기존 인증 현황
        const existingCertificationsSelect = document.querySelector('.quotation-calculator select[name="existingCertifications"]');
        if (existingCertificationsSelect && data.existingCertifications) {
            existingCertificationsSelect.value = data.existingCertifications;
            console.log('기존 인증 현황 설정됨:', data.existingCertifications);
        }
        
        // ISO 표준 선택
        if (data.isoStandards && data.isoStandards.length > 0) {
            data.isoStandards.forEach(standard => {
                const checkbox = document.querySelector(`.quotation-calculator input[name="isoStandards"][value="${standard}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                    console.log('ISO 표준 체크됨:', standard);
                }
            });
        }
        
        // 모든 필드가 제대로 설정되었는지 확인
        setTimeout(() => {
            console.log('=== 견적 계산기 폼 상태 최종 확인 ===');
            console.log('회사명:', document.querySelector('.quotation-calculator input[name="companyName"]')?.value);
            console.log('직원 수:', document.querySelector('.quotation-calculator select[name="employeeCount"]')?.value);
            console.log('사업장 수:', document.querySelector('.quotation-calculator select[name="siteCount"]')?.value);
            console.log('업종:', document.querySelector('.quotation-calculator select[name="industry"]')?.value);
            console.log('복잡도:', document.querySelector('.quotation-calculator select[name="complexity"]')?.value);
            console.log('기존 인증 현황:', document.querySelector('.quotation-calculator select[name="existingCertifications"]')?.value);
            console.log('ISO 표준 체크된 개수:', document.querySelectorAll('.quotation-calculator input[name="isoStandards"]:checked').length);
        }, 200);
        
        console.log('견적 계산기 폼 데이터 적용 완료');
    }

    isFormComplete(formData) {
        console.log('=== isFormComplete 검증 시작 ===');
        console.log('검증할 폼 데이터:', formData);
        
        // 필수 필드만 검증 (업종, 복잡도는 기본값으로 설정되므로 제외)
        const requiredFields = ['companyName', 'employeeCount', 'siteCount', 'isoStandards'];
        console.log('필수 필드:', requiredFields);
        
        const result = requiredFields.every(field => {
            if (field === 'isoStandards') {
                const isValid = formData[field] && formData[field].length > 0;
                console.log(`필드 ${field} (ISO 표준): ${formData[field]} - 유효성: ${isValid}`);
                return isValid;
            }
            const isValid = formData[field] && formData[field].trim() !== '';
            console.log(`필드 ${field}: ${formData[field]} - 유효성: ${isValid}`);
            return isValid;
        });
        
        console.log('=== 최종 검증 결과 ===');
        console.log('모든 필수 필드 유효:', result);
        console.log('========================');
        
        return result;
    }

    showQuotationResult(quotation) {
        // 견적 결과를 화면에 표시
        const totalAmountElement = document.querySelector('.total-amount');
        const selectedStandardsElement = document.querySelector('.selected-standards');
        const totalAuditDaysElement = document.querySelector('.total-audit-days');
        
        if (totalAmountElement) {
            totalAmountElement.textContent = `₩${quotation.totalAmount.toLocaleString()}`;
        }
        
        if (selectedStandardsElement) {
            const standards = this.currentFormData.isoStandards.map(code => {
                const standardNames = {
                    '9001': 'ISO 9001',
                    '14001': 'ISO 14001',
                    '45001': 'ISO 45001',
                    '27001': 'ISO 27001',
                    '22000': 'ISO 22000',
                    '13485': 'ISO 13485'
                };
                return standardNames[code] || code;
            }).join(', ');
            selectedStandardsElement.textContent = standards;
        }
        
        if (totalAuditDaysElement && quotation.totalAuditDays) {
            totalAuditDaysElement.textContent = `${quotation.totalAuditDays}일`;
        }
        
        // 견적 상세 내역 표시
        this.showQuotationBreakdown(quotation);
    }
    
    showQuotationBreakdown(quotation) {
        const breakdownContainer = document.querySelector('.breakdown-items');
        if (!breakdownContainer) return;
        
        let breakdownHTML = '';
        
        if (quotation.standardQuotes) {
            quotation.standardQuotes.forEach(quote => {
                breakdownHTML += `
                    <div class="breakdown-item">
                        <div class="item-header">
                            <strong>${quote.standardName}</strong>
                            <span class="item-amount">₩${quote.totalAmount.toLocaleString()}</span>
                        </div>
                        <div class="item-details">
                            <div class="detail-row">
                                <span class="label">기본 인증 비용:</span>
                                <span class="value">₩${quote.baseAmount.toLocaleString()}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">추가 서비스:</span>
                                <span class="value">₩${quote.additionalServices.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        if (quotation.additionalServices) {
            quotation.additionalServices.forEach(service => {
                breakdownHTML += `
                    <div class="breakdown-item">
                        <div class="item-header">
                            <strong>${service.name}</strong>
                            <span class="item-amount">₩${service.amount.toLocaleString()}</span>
                        </div>
                    </div>
                `;
            });
        }
        
        breakdownContainer.innerHTML = breakdownHTML;
    }
    
    showDraftRequestSection() {
        const draftRequestSection = document.querySelector('.draft-request-section');
        if (draftRequestSection) {
            draftRequestSection.style.display = 'block';
            draftRequestSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // 견적서 초안 요청
    async requestDraftQuotation() {
        try {
            this.showLoading(true);
            
            // 견적 계산
            const quotation = await this.calculateQuotation();
            
            if (quotation) {
                this.currentQuotation = quotation;
                this.quotationStatus = 'draft';
                
                // 견적서 초안 표시 (사용자용 약식)
                this.showDraftQuotation(quotation);
                
                // 정식 견적서 상태 표시
                this.showFormalQuotationStatus();
                
                this.showMessage('success', '견적서 초안 생성 완료', 
                    '견적서 초안이 생성되었습니다. 정식 견적서는 LRQA 담당자 승인 후 발송됩니다.');
            }
        } catch (error) {
            console.error('견적서 초안 생성 실패:', error);
            this.showMessage('error', '오류 발생', '견적서 초안 생성 중 오류가 발생했습니다.');
        } finally {
            this.showLoading(false);
        }
    }

    // 견적서 초안 표시 (사용자용 약식)
    showDraftQuotation(quotation) {
        const draftSection = document.querySelector('.quotation-draft-result');
        if (draftSection) {
            draftSection.style.display = 'block';
            this.displayDraftQuotation(quotation);
        }
    }

    // 사용자용 약식 견적서 표시
    displayDraftQuotation(quotation) {
        try {
            // 총 견적 금액 표시
            const totalAmount = document.querySelector('.total-amount');
            if (totalAmount) {
                totalAmount.textContent = `₩${quotation.totalAmount.toLocaleString()}`;
            }

            // 기본 심사비 표시
            const baseAuditCost = document.querySelector('.base-audit-cost');
            if (baseAuditCost && quotation.baseAuditCost) {
                baseAuditCost.textContent = `₩${quotation.baseAuditCost.toLocaleString()}`;
            }

            // 제경비 표시
            const overheadCost = document.querySelector('.overhead-cost');
            if (overheadCost && quotation.overhead) {
                overheadCost.textContent = `₩${quotation.overhead.toLocaleString()}`;
            }

            // 선택된 ISO 표준 표시
            const selectedStandards = document.querySelector('.selected-standards');
            if (selectedStandards) {
                if (this.currentFormData && this.currentFormData.isoStandards && Array.isArray(this.currentFormData.isoStandards)) {
                    const standards = this.currentFormData.isoStandards.map(std => {
                        const standardNames = {
                            '9001': 'ISO 9001',
                            '14001': 'ISO 14001',
                            '45001': 'ISO 45001',
                            '27001': 'ISO 27001',
                            '22000': 'ISO 22000',
                            '13485': 'ISO 13485'
                        };
                        return standardNames[std] || std;
                    }).join(', ');
                    selectedStandards.textContent = standards;
                } else {
                    selectedStandards.textContent = 'ISO 45001'; // 기본값
                }
            }

            // 적용 할인 표시
            const appliedDiscounts = document.querySelector('.applied-discounts');
            if (appliedDiscounts) {
                if (quotation.appliedDiscounts && Array.isArray(quotation.appliedDiscounts) && quotation.appliedDiscounts.length > 0) {
                    const discountText = quotation.appliedDiscounts.map(d => d.type).join(', ');
                    appliedDiscounts.textContent = discountText;
                } else {
                    appliedDiscounts.textContent = '적용 없음';
                }
            }
            
            // 심사일수 표시
            const totalAuditDays = document.querySelector('.total-audit-days');
            if (totalAuditDays && quotation.totalAuditDays) {
                totalAuditDays.textContent = `${quotation.totalAuditDays}일`;
            }
            
            // 견적 상세 내역 표시
            this.displayDraftBreakdown(quotation);
        } catch (error) {
            console.error('견적서 초안 표시 중 오류:', error);
            // 오류 발생 시 기본 정보만 표시
            const totalAmount = document.querySelector('.total-amount');
            if (totalAmount && quotation.totalAmount) {
                totalAmount.textContent = `₩${quotation.totalAmount.toLocaleString()}`;
            }
        }
    }

    // 견적 상세 내역 표시 (사용자용)
    displayDraftBreakdown(quotation) {
        try {
            const breakdownContainer = document.querySelector('.breakdown-items');
            if (!breakdownContainer) return;

            let html = '';
            
            // 기본 심사비와 제경비 표시 (우선 표시)
            if (quotation.baseAuditCost && quotation.overhead) {
                html += `
                    <div class="breakdown-item">
                        <span class="item-name">기본 심사비 (${quotation.totalAuditDays || 0}일)</span>
                        <span class="item-amount">₩${quotation.baseAuditCost.toLocaleString()}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="item-name">제경비 (10%)</span>
                        <span class="item-amount">₩${quotation.overhead.toLocaleString()}</span>
                    </div>
                `;
            }

            // ISO 표준별 견적
            if (quotation.breakdown && Array.isArray(quotation.breakdown) && quotation.breakdown.length > 0) {
                quotation.breakdown.forEach(item => {
                    if (item && item.standard && item.amount) {
                        html += `
                            <div class="breakdown-item">
                                <span class="item-name">${item.standard}</span>
                                <span class="item-amount">₩${item.amount.toLocaleString()}</span>
                            </div>
                        `;
                    }
                });
            }

            // 할인 내역
            if (quotation.appliedDiscounts && Array.isArray(quotation.appliedDiscounts) && quotation.appliedDiscounts.length > 0) {
                quotation.appliedDiscounts.forEach(discount => {
                    if (discount && discount.type && discount.amount > 0) {
                        html += `
                            <div class="breakdown-item discount">
                                <span class="item-name">${discount.type}</span>
                                <span class="item-amount">-₩${discount.amount.toLocaleString()}</span>
                            </div>
                        `;
                    }
                });
            }

            breakdownContainer.innerHTML = html;
        } catch (error) {
            console.error('견적 상세 내역 표시 중 오류:', error);
            // 오류 발생 시 기본 정보만 표시
            const breakdownContainer = document.querySelector('.breakdown-items');
            if (breakdownContainer) {
                breakdownContainer.innerHTML = `
                    <div class="breakdown-item">
                        <span class="item-name">기본 심사비</span>
                        <span class="item-amount">₩${quotation.baseAuditCost ? quotation.baseAuditCost.toLocaleString() : '0'}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="item-name">제경비 (10%)</span>
                        <span class="item-amount">₩${quotation.overhead ? quotation.overhead.toLocaleString() : '0'}</span>
                    </div>
                `;
            }
        }
    }

    // LRQA 담당자용 정식 견적서 생성
    async generateLRQADocument() {
        try {
            this.showLoading(true);
            
            if (!this.currentQuotation || !this.currentFormData) {
                this.showMessage('error', '오류 발생', '견적 정보가 없습니다. 먼저 견적서 초안을 생성해주세요.');
                return;
            }

            // LRQA 담당자용 정식 견적서 생성
            const docx = await this.wordGenerator.generateQuotationDocument(
                this.currentQuotation, 
                this.currentFormData,
                'formal' // 정식 견적서
            );
            
            // LRQA 담당자용 섹션 표시
            this.showLRQADocumentSection();
            
            this.showMessage('success', '정식 견적서 생성 완료', 
                'LRQA 담당자용 정식 견적서가 생성되었습니다. 다운로드하여 검토하세요.');
                
        } catch (error) {
            console.error('정식 견적서 생성 실패:', error);
            this.showMessage('error', '오류 발생', '정식 견적서 생성 중 오류가 발생했습니다.');
        } finally {
            this.showLoading(false);
        }
    }

    // LRQA 담당자용 섹션 표시
    showLRQADocumentSection() {
        const lrqaSection = document.querySelector('.lrqa-document-section');
        if (lrqaSection) {
            lrqaSection.style.display = 'block';
        }
    }

    // LRQA 담당자용 정식 견적서 다운로드
    async downloadLRQADocument() {
        try {
            const docx = await this.wordGenerator.generateQuotationDocument(
                this.currentQuotation, 
                this.currentFormData,
                'formal' // 정식 견적서
            );
            
            const blob = new Blob([docx], { 
                type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `LRQA_${this.currentFormData.companyName}_정식견적서_${new Date().toISOString().split('T')[0]}.docx`;
            a.click();
            
            this.showMessage('success', '다운로드 완료', 
                'LRQA 담당자용 정식 견적서가 다운로드되었습니다.');
        } catch (error) {
            console.error('정식 견적서 다운로드 실패:', error);
            this.showMessage('error', '다운로드 실패', '정식 견적서 다운로드 중 오류가 발생했습니다.');
        }
    }

    // 정식 견적서 상태 표시
    showFormalQuotationStatus() {
        const statusSection = document.querySelector('.formal-quotation-status');
        if (statusSection) {
            statusSection.style.display = 'block';
        }
    }

    // 견적서 초안 수정
    editDraftQuotation() {
        const draftSection = document.querySelector('.quotation-draft-result');
        const statusSection = document.querySelector('.formal-quotation-status');
        const lrqaSection = document.querySelector('.lrqa-document-section');
        
        if (draftSection) draftSection.style.display = 'none';
        if (statusSection) statusSection.style.display = 'none';
        if (lrqaSection) lrqaSection.style.display = 'none';
        
        // 폼 편집 모드로 전환
        this.enableFormEditing();
    }

    // 폼 편집 모드 활성화
    enableFormEditing() {
        const form = document.querySelector('.quotation-calculator form');
        if (form) {
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.disabled = false;
            });
        }
    }

    // 견적 계산기 닫기
    closeQuotationCalculator() {
        const calculator = document.querySelector('.quotation-calculator');
        if (calculator) {
            calculator.remove();
            console.log('견적 계산기가 닫혔습니다.');
        }
    }

    // 견적 계산기 초기화
    resetCalculator() {
        const form = document.querySelector('.quotation-calculator form');
        if (form) {
            form.reset();
        }
        
        // 모든 결과 섹션 숨기기
        const sections = [
            '.quotation-draft-result',
            '.formal-quotation-status',
            '.lrqa-document-section'
        ];
        
        sections.forEach(selector => {
            const section = document.querySelector(selector);
            if (section) {
                section.style.display = 'none';
            }
        });
        
        this.currentQuotation = null;
        this.currentFormData = null;
        this.quotationStatus = 'draft';
    }

    showLoading(show) {
        const loadingElement = document.querySelector('.calculator-loading');
        if (loadingElement) {
            loadingElement.style.display = show ? 'block' : 'none';
        }
    }

    showDetailedModal(content) {
        const modal = document.createElement('div');
        modal.className = 'quotation-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close">&times;</span>
                <div class="modal-body">${content}</div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('.close').onclick = () => {
            document.body.removeChild(modal);
        };
        
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
    }

    showMessage(type, title, content) {
        const alertClass = `alert-${type}`;
        const message = `
            <div class="alert ${alertClass}">
                <strong>${title}</strong><br>
                ${content}
            </div>
        `;
        
        // 메시지를 견적 계산기 상단에 표시
        const calculator = document.querySelector('.quotation-calculator');
        if (calculator) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message-container';
            messageDiv.innerHTML = message;
            
            calculator.insertBefore(messageDiv, calculator.firstChild);
            
            // 5초 후 메시지 제거
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 5000);
        }
    }

    loadDocxGenLibrary() {
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

    getIndustryName(industryCode) {
        const industries = {
            'manufacturing': '제조업',
            'construction': '건설업',
            'service': '서비스업',
            'trade': '무역업',
            'other': '기타'
        };
        return industries[industryCode] || industryCode;
    }

    getComplexityName(complexityCode) {
        const complexities = {
            'low': '낮음',
            'medium': '보통',
            'high': '높음'
        };
        return complexities[complexityCode] || complexityCode;
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuotationCalculator;
} else {
    window.QuotationCalculator = QuotationCalculator;
}
