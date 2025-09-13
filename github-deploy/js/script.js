// LRQA 인증 심사 신청서 - 갭분석 통합 버전 JavaScript

// 테마 관련 변수
let currentTheme = 'light';

// 갭분석 관련 변수
let isGapAnalysisInProgress = false;
let analysisSteps = [
    { id: 'step1', text: '신청서 데이터 처리중...', duration: 2000 },
    { id: 'step2', text: '기업 정보 수집중...', duration: 3000 },
    { id: 'step3', text: 'AI 리스크 분석중...', duration: 4000 },
    { id: 'step4', text: '갭분석 보고서 생성중...', duration: 2000 },
    { id: 'step5', text: '이메일 발송중...', duration: 1500 }
];

// 테마 초기화
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    currentTheme = savedTheme;
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeToggleButton();
}

// 테마 토글 버튼 업데이트
function updateThemeToggleButton() {
    const toggleButton = document.getElementById('themeToggle');
    if (!toggleButton) return;
    
    const icon = toggleButton.querySelector('.theme-toggle-icon');
    const text = toggleButton.querySelector('.theme-toggle-text');
    
    if (currentTheme === 'dark') {
        icon.textContent = '☀️';
        text.textContent = '라이트모드';
    } else {
        icon.textContent = '🌙';
        text.textContent = '다크모드';
    }
}

// 테마 토글 기능
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    updateThemeToggleButton();
    
    // 부드러운 전환 효과
    document.body.classList.add('theme-transitioning');
    setTimeout(() => {
        document.body.classList.remove('theme-transitioning');
    }, 300);
}

// 전역 변수
let currentPage = 1;
const totalPages = 7;

// 전역 변수에 debounce 플래그 추가
let isNavigating = false;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing form...');
    
    // 잠깐 기다렸다가 초기화 (다른 스크립트와의 충돌 방지)
    setTimeout(() => {
        initializeForm();
        setupEventListeners();
        initializeTheme(); // 테마 초기화 함수 호출
        restoreFormData(); // 저장된 데이터 복원
        autoSave(); // 자동 저장 시작
    }, 100);
});

// 폼 초기화
function initializeForm() {
    showPage(1);
    updateNavigationButtons();
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 테마 토글 버튼 이벤트
    const themeToggleBtn = document.getElementById('themeToggle');
    if (themeToggleBtn) {
        // 기존 이벤트 리스너 제거 후 새로 등록
        themeToggleBtn.removeEventListener('click', toggleTheme);
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // 네비게이션 버튼 이벤트
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const submitBtn = document.querySelector('.submit-btn');
    const gapAnalysisBtn = document.getElementById('gapAnalysisBtn');

    if (prevBtn) {
        prevBtn.removeEventListener('click', handlePrevClick);
        prevBtn.addEventListener('click', handlePrevClick);
    }
    
    if (nextBtn) {
        nextBtn.removeEventListener('click', handleNextClick);
        nextBtn.addEventListener('click', handleNextClick);
    }
    
    if (submitBtn) {
        submitBtn.removeEventListener('click', handleSubmitClick);
        submitBtn.addEventListener('click', handleSubmitClick);
    }

    // 🆕 갭분석 버튼 이벤트
    if (gapAnalysisBtn) {
        gapAnalysisBtn.removeEventListener('click', handleGapAnalysisClick);
        gapAnalysisBtn.addEventListener('click', handleGapAnalysisClick);
    }

    // 임시저장 버튼 이벤트
    const tempSaveBtn = document.getElementById('tempSaveBtn');
    if (tempSaveBtn) {
        tempSaveBtn.removeEventListener('click', handleTempSave);
        tempSaveBtn.addEventListener('click', handleTempSave);
    }

    // 폼 필드 이벤트 리스너
    setupFormFieldListeners();
}

// 이전 버튼 클릭 핸들러
function handlePrevClick(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (isNavigating) {
        console.log('Navigation in progress, ignoring click');
        return;
    }
    
    isNavigating = true;
    console.log('Previous button clicked');
    
    previousPage();
    
    // 500ms 후 다시 활성화
    setTimeout(() => {
        isNavigating = false;
    }, 500);
}

// 다음 버튼 클릭 핸들러
function handleNextClick(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (isNavigating) {
        console.log('Navigation in progress, ignoring click');
        return;
    }
    
    isNavigating = true;
    console.log('Next button clicked');
    
    nextPage();
    
    // 500ms 후 다시 활성화
    setTimeout(() => {
        isNavigating = false;
    }, 500);
}

// 제출 버튼 클릭 핸들러
function handleSubmitClick(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (isNavigating) {
        console.log('Navigation in progress, ignoring click');
        return;
    }
    
    isNavigating = true;
    console.log('Submit button clicked');
    
    submitForm();
    
    // 1초 후 다시 활성화
    setTimeout(() => {
        isNavigating = false;
    }, 1000);
}

// 🆕 갭분석 버튼 클릭 핸들러
function handleGapAnalysisClick(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (isGapAnalysisInProgress || isNavigating) {
        console.log('Gap analysis in progress or navigation in progress, ignoring click');
        return;
    }
    
    console.log('Gap Analysis button clicked');
    startGapAnalysis();
}

// 🆕 갭분석 시작 함수
async function startGapAnalysis() {
    try {
        // 최종 유효성 검사
        if (!validateAllPages()) {
            showMessage('모든 필수 항목을 입력해주세요.', 'error');
            return;
        }

        // 필수 정보 체크 (회사명, 웹사이트, ISO 표준 선택)
        const companyName = document.getElementById('companyName')?.value?.trim();
        const companyWebsite = document.getElementById('companyWebsite')?.value?.trim();
        const selectedISO = getSelectedISOStandards();

        if (!companyName) {
            showMessage('회사명을 입력해주세요.', 'error');
            showPage(1);
            return;
        }

        if (!companyWebsite) {
            showMessage('회사 홈페이지 URL을 입력해주세요.', 'error');
            showPage(1);
            return;
        }

        if (!selectedISO || selectedISO.length === 0) {
            showMessage('희망하는 ISO 인증 표준을 선택해주세요.', 'error');
            showPage(2);
            return;
        }

        isGapAnalysisInProgress = true;
        
        // 갭분석 모달 표시
        showGapAnalysisModal();
        
        // 폼 데이터 수집
        const formData = gatherFormData();
        formData.requestGapAnalysis = true;
        formData.selectedISOStandards = selectedISO;
        
        // 갭분석 진행 애니메이션 시작
        await runGapAnalysisSteps();
        
        // 실제 갭분석 API 호출
        const response = await fetch('/.netlify/functions/submit-application-with-gap-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const result = await response.json();
            
            // 성공 메시지와 함께 모달 완료 표시
            showGapAnalysisSuccess(result);
            
            // 저장된 임시 데이터 삭제
            clearSavedData();
            
        } else {
            throw new Error('서버 오류가 발생했습니다.');
        }
        
    } catch (error) {
        console.error('Gap Analysis error:', error);
        showGapAnalysisError(error.message);
    }
}

// 🆕 선택된 ISO 표준 가져오기
function getSelectedISOStandards() {
    const selectedStandards = [];
    const isoCheckboxes = document.querySelectorAll('input[name="isoStandards"]:checked');
    
    isoCheckboxes.forEach(checkbox => {
        selectedStandards.push(checkbox.value);
    });
    
    return selectedStandards;
}

// 🆕 갭분석 모달 표시
function showGapAnalysisModal() {
    const modal = document.getElementById('gapAnalysisModal');
    if (modal) {
        modal.style.display = 'flex';
        
        // 진행바 초기화
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            progressFill.style.width = '0%';
        }
        
        // 모든 스텝 초기화
        analysisSteps.forEach((_, index) => {
            const step = document.getElementById(`step${index + 1}`);
            if (step) {
                step.classList.remove('active', 'completed');
            }
        });
    }
}

// 🆕 갭분석 단계별 실행
async function runGapAnalysisSteps() {
    let totalDuration = 0;
    const totalTime = analysisSteps.reduce((sum, step) => sum + step.duration, 0);
    
    for (let i = 0; i < analysisSteps.length; i++) {
        const step = analysisSteps[i];
        const stepElement = document.getElementById(step.id);
        
        // 현재 스텝 활성화
        if (stepElement) {
            stepElement.classList.add('active');
        }
        
        // 진행률 업데이트
        const progressFill = document.getElementById('progressFill');
        if (progressFill) {
            const progress = ((totalDuration + step.duration) / totalTime) * 100;
            progressFill.style.width = `${progress}%`;
        }
        
        // 예상 시간 업데이트
        const estimatedTime = document.getElementById('estimatedTime');
        if (estimatedTime && i < analysisSteps.length - 1) {
            const remainingTime = analysisSteps.slice(i + 1).reduce((sum, s) => sum + s.duration, 0);
            const minutes = Math.ceil(remainingTime / 1000 / 60);
            estimatedTime.textContent = `약 ${minutes}분`;
        }
        
        // 스텝 대기
        await new Promise(resolve => setTimeout(resolve, step.duration));
        
        // 스텝 완료 처리
        if (stepElement) {
            stepElement.classList.remove('active');
            stepElement.classList.add('completed');
        }
        
        totalDuration += step.duration;
    }
}

// 🆕 갭분석 성공 처리
function showGapAnalysisSuccess(result) {
    const modal = document.getElementById('gapAnalysisModal');
    const modalContent = modal?.querySelector('.modal-content');
    
    if (modalContent) {
        modalContent.innerHTML = `
            <div class="modal-header" style="text-align: center;">
                <h3 style="color: #10b981; margin-bottom: 20px;">
                    ✅ ISO 갭분석 완료!
                </h3>
            </div>
            <div class="modal-body" style="text-align: center;">
                <div style="background: linear-gradient(135deg, #f0fdf4, #ecfdf5); padding: 30px; border-radius: 15px; margin-bottom: 25px;">
                    <div style="font-size: 48px; margin-bottom: 15px;">🎉</div>
                    <h4 style="color: #059669; margin-bottom: 15px;">신청서 제출 및 갭분석 완료</h4>
                    <p style="color: #374151; line-height: 1.6;">
                        귀하의 ISO 인증 신청서가 성공적으로 제출되었으며,<br>
                        맞춤형 갭분석 보고서가 이메일로 발송됩니다.
                    </p>
                </div>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                    <h5 style="color: #1f2937; margin-bottom: 15px;">📧 발송 예정 내용</h5>
                    <ul style="text-align: left; color: #4b5563; line-height: 1.8;">
                        <li>ISO ${getSelectedISOStandards().join(', ')} 갭분석 보고서</li>
                        <li>현재 리스크 평가 및 개선 권장사항</li>
                        <li>인증 준비도 점수 및 액션 플랜</li>
                        <li>LRQA 컨설턴트 연결 안내</li>
                    </ul>
                </div>
                
                <p style="color: #6b7280; font-size: 14px; margin-bottom: 25px;">
                    보고서 생성에는 약 10-15분이 소요되며,<br>
                    완료되는 대로 등록하신 이메일로 발송됩니다.
                </p>
                
                <button onclick="closeGapAnalysisModal()" 
                        style="background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 12px 30px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 16px;">
                    확인
                </button>
            </div>
        `;
    }
}

// 🆕 갭분석 에러 처리
function showGapAnalysisError(errorMessage) {
    const modal = document.getElementById('gapAnalysisModal');
    const modalContent = modal?.querySelector('.modal-content');
    
    if (modalContent) {
        modalContent.innerHTML = `
            <div class="modal-header" style="text-align: center;">
                <h3 style="color: #dc2626; margin-bottom: 20px;">
                    ❌ 갭분석 처리 중 오류 발생
                </h3>
            </div>
            <div class="modal-body" style="text-align: center;">
                <div style="background: #fef2f2; padding: 25px; border-radius: 15px; margin-bottom: 25px; border-left: 4px solid #dc2626;">
                    <div style="font-size: 32px; margin-bottom: 15px;">⚠️</div>
                    <p style="color: #991b1b; margin-bottom: 15px; font-weight: 500;">
                        처리 중 오류가 발생했습니다
                    </p>
                    <p style="color: #6b7280; font-size: 14px;">
                        ${errorMessage || '알 수 없는 오류가 발생했습니다.'}
                    </p>
                </div>
                
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button onclick="closeGapAnalysisModal()" 
                            style="background: #6b7280; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer;">
                        닫기
                    </button>
                    <button onclick="retryGapAnalysis()" 
                            style="background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: 600;">
                        다시 시도
                    </button>
                </div>
            </div>
        `;
    }
    
    isGapAnalysisInProgress = false;
}

// 🆕 갭분석 모달 닫기
function closeGapAnalysisModal() {
    const modal = document.getElementById('gapAnalysisModal');
    if (modal) {
        modal.style.display = 'none';
    }
    
    isGapAnalysisInProgress = false;
    
    // 페이지 새로고침 (성공 시에만)
    if (!modal?.querySelector('.modal-content')?.innerHTML.includes('오류')) {
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }
}

// 🆕 갭분석 재시도
function retryGapAnalysis() {
    closeGapAnalysisModal();
    setTimeout(() => {
        startGapAnalysis();
    }, 500);
}

// 폼 필드 이벤트 리스너 설정
function setupFormFieldListeners() {
    // 전화번호 자동 포맷팅
    const phoneFields = document.querySelectorAll('input[type="tel"]');
    phoneFields.forEach(field => {
        field.addEventListener('input', formatPhoneNumber);
    });

    // 사업자등록번호 자동 포맷팅
    const businessRegField = document.getElementById('businessRegNumber');
    if (businessRegField) {
        businessRegField.addEventListener('input', formatBusinessNumber);
    }

    // 실시간 유효성 검사
    const requiredFields = document.querySelectorAll('input[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
    });
}

// 페이지 표시
function showPage(pageNumber) {
    console.log(`Attempting to show page ${pageNumber}`);
    
    // 모든 페이지 숨기기 및 active 클래스 제거
    const pages = document.querySelectorAll('.form-page');
    console.log(`Found ${pages.length} pages`);
    
    pages.forEach((page, index) => {
        page.style.display = 'none';
        page.style.visibility = 'hidden';
        page.classList.remove('active');
        console.log(`Hiding page ${index + 1}`);
    });

    // 현재 페이지 표시
    const currentPageElement = document.getElementById(`page${pageNumber}`);
    console.log(`Page element for page${pageNumber}:`, currentPageElement);
    
    if (currentPageElement) {
        currentPageElement.style.display = 'block';
        currentPageElement.style.visibility = 'visible';
        currentPageElement.style.opacity = '1';
        currentPageElement.classList.add('active');
        
        // 페이지 내용 확인
        const pageContent = currentPageElement.innerHTML;
        console.log(`Page ${pageNumber} content length: ${pageContent.length}`);
        
        console.log(`Successfully displayed page ${pageNumber}`);
        
        // 페이지 높이 확인
        setTimeout(() => {
            const height = currentPageElement.offsetHeight;
            console.log(`Page ${pageNumber} height: ${height}px`);
        }, 100);
    } else {
        console.error(`Page element not found for page${pageNumber}`);
    }

    currentPage = pageNumber;
    updateNavigationButtons();
    
    // 페이지 맨 위로 스크롤
    window.scrollTo(0, 0);
}

// 이전 페이지로 이동
function previousPage() {
    if (currentPage > 1) {
        showPage(currentPage - 1);
    }
}

// 다음 페이지로 이동
function nextPage() {
    console.log(`nextPage called, currentPage: ${currentPage}, totalPages: ${totalPages}`);
    console.log('Call stack:', new Error().stack);
    
    const isValid = validateCurrentPage();
    console.log(`validateCurrentPage returned: ${isValid}`);
    
    if (isValid) {
        if (currentPage < totalPages) {
            console.log(`Moving from page ${currentPage} to page ${currentPage + 1}`);
            showPage(currentPage + 1);
        } else {
            console.log(`Already at last page: ${currentPage}`);
        }
    } else {
        console.log(`Validation failed for page ${currentPage}`);
    }
}

// 현재 페이지 유효성 검사
function validateCurrentPage() {
    const currentPageElement = document.getElementById(`page${currentPage}`);
    if (!currentPageElement) return true;

    const requiredFields = currentPageElement.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // 라디오 버튼 그룹 검사
    const radioGroups = currentPageElement.querySelectorAll('input[type="radio"][required]');
    const groupNames = new Set();
    radioGroups.forEach(radio => {
        groupNames.add(radio.name);
    });

    groupNames.forEach(groupName => {
        const checkedRadio = currentPageElement.querySelector(`input[name="${groupName}"]:checked`);
        if (!checkedRadio) {
            showMessage(`${groupName} 항목을 선택해주세요.`, 'error');
            isValid = false;
        }
    });

    return isValid;
}

// 개별 필드 유효성 검사
function validateField(field) {
    if (typeof field === 'object' && field.target) {
        field = field.target;
    }

    const value = field.value.trim();
    let isValid = true;

    // 필수 필드 검사
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, '이 필드는 필수입니다.');
        isValid = false;
    } else {
        clearFieldError(field);
    }

    // 이메일 형식 검사
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, '올바른 이메일 형식을 입력해주세요.');
            isValid = false;
        }
    }

    // 전화번호 형식 검사
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[\d\-\+\(\)\s]+$/;
        if (!phoneRegex.test(value)) {
            showFieldError(field, '올바른 전화번호 형식을 입력해주세요.');
            isValid = false;
        }
    }

    // URL 형식 검사
    if (field.type === 'url' && value) {
        try {
            new URL(value);
        } catch {
            showFieldError(field, '올바른 URL 형식을 입력해주세요. (예: https://www.company.com)');
            isValid = false;
        }
    }

    return isValid;
}

// 필드 에러 표시
function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#dc2626';
    errorDiv.style.fontSize = '12px';
    errorDiv.style.marginTop = '4px';
    
    field.style.borderColor = '#dc2626';
    field.parentNode.appendChild(errorDiv);
}

// 필드 에러 제거
function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.style.borderColor = '';
}

// 네비게이션 버튼 업데이트
function updateNavigationButtons() {
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const submitBtn = document.querySelector('.submit-btn');
    const gapAnalysisBtn = document.getElementById('gapAnalysisBtn');

    if (prevBtn) {
        prevBtn.disabled = currentPage === 1;
    }

    if (nextBtn && submitBtn && gapAnalysisBtn) {
        if (currentPage === totalPages) {
            // 마지막 페이지에서는 제출 버튼과 갭분석 버튼 모두 표시
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-flex';
            gapAnalysisBtn.style.display = 'inline-flex';
        } else {
            // 다른 페이지에서는 다음 버튼만 표시
            nextBtn.style.display = 'inline-block';
            submitBtn.style.display = 'none';
            gapAnalysisBtn.style.display = 'none';
        }
    }
}

// 전화번호 포맷팅
function formatPhoneNumber(event) {
    let value = event.target.value.replace(/\D/g, '');
    
    if (value.length >= 3) {
        if (value.length <= 7) {
            value = value.replace(/(\d{3})(\d{1,4})/, '$1-$2');
        } else if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{3,4})(\d{4})/, '$1-$2-$3');
        }
    }
    
    event.target.value = value;
}

// 사업자등록번호 포맷팅
function formatBusinessNumber(event) {
    let value = event.target.value.replace(/\D/g, '');
    
    if (value.length >= 3) {
        if (value.length <= 5) {
            value = value.replace(/(\d{3})(\d{1,2})/, '$1-$2');
        } else if (value.length <= 10) {
            value = value.replace(/(\d{3})(\d{2})(\d{1,5})/, '$1-$2-$3');
        }
    }
    
    event.target.value = value;
}

// 폼 데이터 수집 (갭분석 옵션 포함)
function gatherFormData() {
    const formData = {};
    
    // 텍스트 입력 필드
    const textFields = [
        'companyName', 'tradeName', 'headOfficeAddress', 'city', 'province',
        'postalCode', 'country', 'mainPhone', 'mainEmail', 'companyWebsite', 
        'corporateRegNumber', 'businessRegNumber', 'customsOffice', 'contactName', 
        'department', 'contactEmail', 'mobilePhone', 'contactPhone', 'consultantName',
        'consultingOrg'
    ];
    
    textFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            formData[fieldId] = field.value.trim();
        }
    });

    // 라디오 버튼 그룹
    const radioGroups = [
        'addressDifferent', 'groupAffiliate', 'multipleSites', 'includeWorkplaces',
        'lrqaInfo', 'standardIntegration', 'legalIssues', 'existingCert',
        'multiSiteEmployees', 'outsourcedProcess', 'repeatWorkers', 'overtimeActivities',
        'temporaryWorkplace', 'customerSiteService', 'transferToLrqa', 'certExpiring',
        'contactConsent', 'localAudit', 'preliminaryAudit', 'trainingInfo', 'dataConsent'
    ];
    
    radioGroups.forEach(groupName => {
        const checkedRadio = document.querySelector(`input[name="${groupName}"]:checked`);
        formData[groupName] = checkedRadio ? checkedRadio.value : '';
    });

    // 체크박스 그룹 - LRQA 소스
    const lrqaSourceCheckboxes = document.querySelectorAll('input[value="광고/홍보"], input[value="웨비나"], input[value="텔레마케팅"], input[value="추천"], input[value="이메일"], input[value="고객 방문"], input[value="자체 평가"], input[value="도구 웹사이트"], input[value="소셜 미디어"], input[value="이벤트"], input[value="우편물"], input[value="기타"]');
    const selectedSources = Array.from(lrqaSourceCheckboxes).filter(cb => cb.checked).map(cb => cb.value);
    formData.lrqaSource = selectedSources.join(', ');

    // 체크박스 그룹 - ISO 표준
    const isoCheckboxes = document.querySelectorAll('input[name="isoStandards"]:checked');
    const selectedStandards = Array.from(isoCheckboxes).map(cb => cb.value);
    formData.isoStandards = selectedStandards.join(', ');

    // 텍스트 영역
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach((textarea, index) => {
        if (textarea.id) {
            formData[textarea.id] = textarea.value.trim();
        } else {
            formData[`textarea_${index}`] = textarea.value.trim();
        }
    });

    // 직원 수 정보
    const employeeCounts = document.querySelectorAll('.count-item input');
    employeeCounts.forEach(input => {
        if (input.type === 'number') {
            const label = input.parentNode.querySelector('label')?.textContent;
            if (label) {
                formData[`employee_${label.replace(/\s+/g, '_')}`] = input.value;
            }
        }
    });

    // 인증 테이블 정보
    const certTable = document.querySelector('.certification-table tbody');
    if (certTable) {
        const rows = certTable.querySelectorAll('tr');
        const certifications = [];
        rows.forEach((row, index) => {
            const inputs = row.querySelectorAll('input');
            if (inputs.length === 3) {
                certifications.push({
                    standard: inputs[0].value.trim(),
                    certBody: inputs[1].value.trim(),
                    expiryDate: inputs[2].value
                });
            }
        });
        formData.existingCertifications = certifications;
    }

    // 희망 심사 일정
    const auditDate = document.querySelector('input[name="desiredAuditDate"]');
    if (auditDate) {
        formData.desiredAuditDate = auditDate.value;
    }

    return formData;
}

// 폼 제출 (기본)
async function submitForm() {
    try {
        // 최종 유효성 검사
        if (!validateAllPages()) {
            showMessage('모든 필수 항목을 입력해주세요.', 'error');
            return;
        }

        showMessage('신청서를 제출하는 중입니다...', 'info');
        
        const formData = gatherFormData();
        
        // 서버로 데이터 전송
        const response = await fetch('/.netlify/functions/submit-application', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const result = await response.json();
            showMessage('신청서가 성공적으로 제출되었습니다!', 'success');
            
            // 저장된 임시 데이터 삭제
            clearSavedData();
            
            // 폼 초기화
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } else {
            throw new Error('서버 오류가 발생했습니다.');
        }
        
    } catch (error) {
        console.error('Submit error:', error);
        showMessage('제출 중 오류가 발생했습니다. 다시 시도해주세요.', 'error');
    }
}

// 전체 페이지 유효성 검사
function validateAllPages() {
    let isValid = true;
    
    for (let i = 1; i <= totalPages; i++) {
        const page = document.getElementById(`page${i}`);
        if (!page) continue;
        
        const requiredFields = page.querySelectorAll('input[required], textarea[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
            }
        });
    }
    
    return isValid;
}

// 메시지 표시
function showMessage(message, type = 'info') {
    // 기존 메시지 제거
    const existingMessage = document.querySelector('.form-message');
    if (existingMessage) {
        existingMessage.remove();
    }

    // 새 메시지 생성
    const messageDiv = document.createElement('div');
    messageDiv.className = `form-message ${type}`;
    messageDiv.textContent = message;
    
    // 스타일 설정
    messageDiv.style.position = 'fixed';
    messageDiv.style.top = '20px';
    messageDiv.style.right = '20px';
    messageDiv.style.padding = '12px 20px';
    messageDiv.style.borderRadius = '5px';
    messageDiv.style.zIndex = '9999';
    messageDiv.style.maxWidth = '400px';
    messageDiv.style.fontWeight = '500';
    
    switch (type) {
        case 'success':
            messageDiv.style.backgroundColor = '#10b981';
            messageDiv.style.color = 'white';
            break;
        case 'error':
            messageDiv.style.backgroundColor = '#dc2626';
            messageDiv.style.color = 'white';
            break;
        case 'info':
        default:
            messageDiv.style.backgroundColor = '#3b82f6';
            messageDiv.style.color = 'white';
            break;
    }
    
    document.body.appendChild(messageDiv);
    
    // 3초 후 자동 제거
    setTimeout(() => {
        if (messageDiv && messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 3000);
}

// 브라우저 뒤로가기 방지
window.addEventListener('beforeunload', function(event) {
    const formData = gatherFormData();
    const hasData = Object.values(formData).some(value => 
        typeof value === 'string' ? value.trim() !== '' : value !== ''
    );
    
    if (hasData && !isGapAnalysisInProgress) {
        event.preventDefault();
        event.returnValue = '작성 중인 내용이 있습니다. 정말로 페이지를 떠나시겠습니까?';
        return event.returnValue;
    }
});

// 임시저장 버튼 클릭 핸들러
function handleTempSave() {
    const btn = document.getElementById('tempSaveBtn');
    const message = document.getElementById('tempSaveMessage');
    
    // 버튼 상태 변경
    btn.classList.add('saving');
    btn.textContent = '저장 중...';
    btn.disabled = true;
    
    try {
        // 현재 페이지와 폼 데이터 저장
        const saveData = {
            currentPage: currentPage,
            formData: gatherFormData(),
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('lrqa_temp_save', JSON.stringify(saveData));
        
        // 성공 메시지 표시
        message.classList.add('show');
        
        // 3초 후 메시지 숨기기
        setTimeout(() => {
            message.classList.remove('show');
        }, 3000);
        
    } catch (error) {
        console.error('임시저장 오류:', error);
        message.textContent = '저장 실패';
        message.style.background = '#f44336';
        message.classList.add('show');
        
        setTimeout(() => {
            message.classList.remove('show');
            message.textContent = '임시저장 완료!';
            message.style.background = '#4caf50';
        }, 3000);
    } finally {
        // 버튼 상태 복원
        setTimeout(() => {
            btn.classList.remove('saving');
            btn.textContent = '📋 임시저장';
            btn.disabled = false;
        }, 1000);
    }
}

// 자동 저장 기능 (30초마다)
function autoSave() {
    setInterval(() => {
        const saveData = {
            currentPage: currentPage,
            formData: gatherFormData(),
            timestamp: new Date().toISOString(),
            isAutoSave: true
        };
        localStorage.setItem('lrqa_auto_save', JSON.stringify(saveData));
    }, 30000);
}

// 저장된 데이터 복원
function restoreFormData() {
    // 수동 임시저장 데이터 우선 확인
    let savedData = localStorage.getItem('lrqa_temp_save');
    if (!savedData) {
        // 기존 draft 데이터 확인
        savedData = localStorage.getItem('lrqa_form_draft');
    }
    if (!savedData) {
        // 자동저장 데이터 확인
        savedData = localStorage.getItem('lrqa_auto_save');
    }
    
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            let formData;
            
            // 새로운 형식인지 확인
            if (data.formData) {
                formData = data.formData;
                // 페이지 복원
                if (data.currentPage && data.currentPage > 1) {
                    currentPage = data.currentPage;
                    showPage(currentPage);
                }
            } else {
                // 기존 형식
                formData = data;
            }
            
            // 텍스트 필드 복원
            Object.keys(formData).forEach(key => {
                const field = document.getElementById(key);
                if (field && formData[key]) {
                    if (field.type === 'radio') {
                        const radioElements = document.querySelectorAll(`input[name="${field.name}"]`);
                        radioElements.forEach(radio => {
                            if (radio.value === formData[key]) {
                                radio.checked = true;
                            }
                        });
                    } else if (field.type === 'checkbox') {
                        if (formData[key] === field.value || formData[key] === 'on') {
                            field.checked = true;
                        }
                    } else if (typeof formData[key] === 'string') {
                        field.value = formData[key];
                    }
                }
            });
            
            showMessage('이전에 작성하던 내용을 복원했습니다.', 'info');
        } catch (error) {
            console.error('Failed to restore form data:', error);
        }
    }
}

// 저장된 데이터 삭제
function clearSavedData() {
    localStorage.removeItem('lrqa_temp_save');
    localStorage.removeItem('lrqa_auto_save');
    localStorage.removeItem('lrqa_form_draft');
}

// 글로벌 함수로 노출 (HTML에서 호출 가능하도록)
window.closeGapAnalysisModal = closeGapAnalysisModal;
window.retryGapAnalysis = retryGapAnalysis;
