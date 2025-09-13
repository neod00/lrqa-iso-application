/**
 * 다국어 지원 시스템
 * 한국어/영어 전환 기능 제공
 */

class LanguageManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'ko';
        this.translations = {
            ko: {
                // 헤더 및 네비게이션
                'header.title': 'LRQA 관리자 설정',
                'header.subtitle': 'ISO 인증심사 신청서 관리 시스템',
                'nav.dashboard': '대시보드',
                'nav.applications': '신청서 목록',
                'nav.quotations': '견적서 관리',
                'nav.export': '데이터 내보내기',
                'nav.form-edit': '폼 편집',
                'button.logout': '로그아웃',
                
                // 로그인
                'login.title': 'LRQA 관리자 로그인',
                'login.username': '사용자명',
                'login.password': '비밀번호',
                'login.button': '로그인',
                'login.error': '로그인 정보가 올바르지 않습니다.',
                
                // 대시보드
                'dashboard.total-applications': '총 신청서',
                'dashboard.new-applications': '신규 신청서',
                'dashboard.monthly-applications': '이달의 신청서',
                'dashboard.completed-applications': '완료된 신청서',
                'dashboard.refresh': '데이터 새로고침',
                'dashboard.loaded': '대시보드가 로드되었습니다.',
                'dashboard.error': '대시보드 로드 중 오류가 발생했습니다.',
                
                // 신청서 목록
                'applications.title': '신청서 목록',
                'applications.refresh': '목록 새로고침',
                'applications.date': '신청일시',
                'applications.company': '회사명',
                'applications.contact': '담당자',
                'applications.phone': '연락처',
                'applications.scope': '인증범위',
                'applications.status': '상태',
                'applications.actions': '작업',
                'applications.view': '보기',
                'applications.edit': '수정',
                'applications.generate-quote': '견적서 생성',
                'applications.no-data': '신청서가 없습니다.',
                'applications.loading': '데이터를 불러오는 중...',
                'applications.loaded': '신청서 목록이 로드되었습니다.',
                'applications.error': '신청서 목록 로드 중 오류가 발생했습니다.',
                
                // 견적서 관리
                'quotations.title': '견적서 관리',
                'quotations.subtitle': 'ISO 9001/14001/45001 견적서 생성',
                'quotations.description': '접수된 신청서를 기반으로 ADJ_v.2.2 기준에 따른 견적서를 생성할 수 있습니다.',
                'quotations.features.title': '주요 기능',
                'quotations.features.calc': 'ADJ_v.2.2 기준 심사일수 자동 계산',
                'quotations.features.complexity': '직원 수, 사업장 수, 업종별 복잡도 고려',
                'quotations.features.word': '전문적인 Word 견적서 자동 생성',
                'quotations.features.save': '견적서 데이터 자동 저장',
                'quotations.criteria.title': '계산 기준',
                'quotations.criteria.base': '기본 심사일수: MD5 기준',
                'quotations.criteria.rate': '심사비: 일당 1,450,000원',
                'quotations.criteria.expense': '제경비: 심사비의 10%',
                'quotations.criteria.additional': '업종별/복잡도별 추가 일수 적용',
                'quotations.generate': '견적서 생성하기',
                'quotations.history': '견적서 이력 보기',
                
                // 데이터 내보내기
                'export.title': '데이터 내보내기',
                'export.description': '신청서 데이터를 다양한 형식으로 내보낼 수 있습니다.',
                'export.csv': 'CSV로 내보내기',
                'export.sheets': 'Google Sheets 열기',
                'export.preparing': 'CSV 파일을 준비 중입니다...',
                'export.success': 'CSV 파일이 다운로드되었습니다.',
                'export.error': 'CSV 내보내기 중 오류가 발생했습니다.',
                
                // 폼 편집
                'form-edit.title': '신청서 폼 편집',
                'form-edit.description': '질문/라벨/설명 텍스트를 수정할 수 있습니다.',
                'form-edit.save': '저장',
                'form-edit.question-id': '질문 ID',
                'form-edit.label': '라벨',
                'form-edit.description': '설명',
                
                // 상태
                'status.new': '신규',
                'status.progress': '진행중',
                'status.completed': '완료',
                
                // 공통 버튼 및 액션
                'button.close': '닫기',
                'button.cancel': '취소',
                'button.save': '저장',
                'button.edit': '수정',
                'button.delete': '삭제',
                'button.view': '보기',
                'button.download': '다운로드',
                'button.refresh': '새로고침',
                
                // 메시지
                'message.success': '성공적으로 완료되었습니다.',
                'message.error': '오류가 발생했습니다.',
                'message.loading': '로딩 중...',
                'message.no-data': '데이터가 없습니다.',
                'message.confirm': '정말로 실행하시겠습니까?',
                
                // 테마 및 설정
                'theme.dark': '다크모드',
                'theme.light': '라이트모드',
                'language.korean': '한국어',
                'language.english': 'English',
                
                // Word 견적서 생성
                'word.generating': '테스트 Word 견적서를 생성 중입니다...',
                'word.success': '테스트 Word 견적서가 생성되었습니다!',
                'word.error': 'Word 견적서 생성 중 오류가 발생했습니다.',
                'word.download-error': 'Word 견적서 생성 실패',
                
                // 견적서 모달
                'quotations.download': 'Word 견적서 다운로드',
                'quotations.summary': '견적서 요약',
                'quotations.client': '고객명',
                'quotations.standards': '표준',
                'quotations.enp': '총 ENP',
                'quotations.audit-days': '총 심사일수',
                'quotations.audit-fee': '심사비',
                'quotations.expenses': '제경비',
                'quotations.total-cost': '총 금액',
                'quotations.breakdown': '표준별 세부내역',
                'quotations.standard': '표준',
                'quotations.complexity': '복잡도',
                'quotations.stage1': 'Stage1',
                'quotations.stage2': 'Stage2',
                'quotations.surveillance': '감시심사',
                'quotations.recertification': '갱신심사',
                'quotations.total-days': '총 일수',
                
                // 견적서 이력 관리
                'history.title': '견적서 이력 관리',
                'history.stats': '통계',
                'history.total': '총 견적서',
                'history.monthly': '이번 달',
                'history.total-value': '총 견적 금액',
                'history.average-value': '평균 견적 금액',
                'history.search': '검색',
                'history.search-placeholder': '고객명, 담당자명 검색...',
                'history.filter-standard': '표준 필터',
                'history.filter-status': '상태 필터',
                'history.filter-date-from': '시작일',
                'history.filter-date-to': '종료일',
                'history.filter-apply': '필터 적용',
                'history.filter-reset': '초기화',
                'history.export-csv': 'CSV 내보내기',
                'history.id': 'ID',
                'history.date': '생성일',
                'history.client': '고객명',
                'history.contact': '담당자',
                'history.standards': '표준',
                'history.enp': 'ENP',
                'history.days': '심사일수',
                'history.cost': '총 금액',
                'history.status': '상태',
                'history.actions': '작업',
                'history.no-data': '이력이 없습니다.',
                'history.status-generated': '생성됨',
                'history.status-sent': '발송됨',
                'history.status-approved': '승인됨',
                'history.status-rejected': '거절됨',
                
                // 차트 관련
                'charts.monthly-trend': '월별 견적서 생성 현황',
                'charts.status-distribution': '상태별 분포',
                'charts.standard-distribution': '표준별 분포',
                'charts.value-trend': '금액 추이',
                
                // 수정 모달
                'edit.title': '견적서 수정',
                'edit.basic-info': '기본 정보',
                'edit.client-name': '고객명',
                'edit.contact-person': '담당자',
                'edit.phone': '연락처',
                'edit.email': '이메일',
                'edit.standards-info': '표준 정보',
                'edit.standards': '표준',
                'edit.pricing-info': '가격 정보',
                'edit.total-enp': '총 ENP',
                'edit.audit-days': '총 심사일수',
                'edit.audit-fee': '심사비 (원)',
                'edit.expenses': '제경비 (원)',
                'edit.total-cost': '총 금액 (원)',
                'edit.additional-info': '추가 정보',
                'edit.status': '상태',
                'edit.notes': '메모',
                'edit.recalculate': '재계산',
                'edit.save': '저장',
            },
            
            en: {
                // Header and Navigation
                'header.title': 'LRQA Admin Settings',
                'header.subtitle': 'ISO Certification Application Management System',
                'nav.dashboard': 'Dashboard',
                'nav.applications': 'Applications',
                'nav.quotations': 'Quotations',
                'nav.export': 'Data Export',
                'nav.form-edit': 'Form Edit',
                'button.logout': 'Logout',
                
                // Login
                'login.title': 'LRQA Admin Login',
                'login.username': 'Username',
                'login.password': 'Password',
                'login.button': 'Login',
                'login.error': 'Invalid login credentials.',
                
                // Dashboard
                'dashboard.total-applications': 'Total Applications',
                'dashboard.new-applications': 'New Applications',
                'dashboard.monthly-applications': 'Monthly Applications',
                'dashboard.completed-applications': 'Completed Applications',
                'dashboard.refresh': 'Refresh Data',
                'dashboard.loaded': 'Dashboard loaded successfully.',
                'dashboard.error': 'Error loading dashboard.',
                
                // Applications
                'applications.title': 'Application List',
                'applications.refresh': 'Refresh List',
                'applications.date': 'Application Date',
                'applications.company': 'Company',
                'applications.contact': 'Contact',
                'applications.phone': 'Phone',
                'applications.scope': 'Certification Scope',
                'applications.status': 'Status',
                'applications.actions': 'Actions',
                'applications.view': 'View',
                'applications.edit': 'Edit',
                'applications.generate-quote': 'Generate Quote',
                'applications.no-data': 'No applications found.',
                'applications.loading': 'Loading data...',
                'applications.loaded': 'Application list loaded successfully.',
                'applications.error': 'Error loading application list.',
                
                // Quotations
                'quotations.title': 'Quotation Management',
                'quotations.subtitle': 'ISO 9001/14001/45001 Quotation Generation',
                'quotations.description': 'Generate quotations based on received applications according to ADJ_v.2.2 standards.',
                'quotations.features.title': 'Key Features',
                'quotations.features.calc': 'Automatic audit day calculation based on ADJ_v.2.2',
                'quotations.features.complexity': 'Consider employee count, sites, and industry complexity',
                'quotations.features.word': 'Professional Word quotation auto-generation',
                'quotations.features.save': 'Automatic quotation data saving',
                'quotations.criteria.title': 'Calculation Criteria',
                'quotations.criteria.base': 'Base audit days: MD5 standard',
                'quotations.criteria.rate': 'Audit fee: 1,450,000 KRW per day',
                'quotations.criteria.expense': 'Expenses: 10% of audit fee',
                'quotations.criteria.additional': 'Additional days by industry/complexity',
                'quotations.generate': 'Generate Quotation',
                'quotations.history': 'View Quotation History',
                
                // Data Export
                'export.title': 'Data Export',
                'export.description': 'Export application data in various formats.',
                'export.csv': 'Export to CSV',
                'export.sheets': 'Open Google Sheets',
                'export.preparing': 'Preparing CSV file...',
                'export.success': 'CSV file downloaded successfully.',
                'export.error': 'Error exporting to CSV.',
                
                // Form Edit
                'form-edit.title': 'Edit Application Form',
                'form-edit.description': 'Modify question/label/description texts.',
                'form-edit.save': 'Save',
                'form-edit.question-id': 'Question ID',
                'form-edit.label': 'Label',
                'form-edit.description': 'Description',
                
                // Status
                'status.new': 'New',
                'status.progress': 'In Progress',
                'status.completed': 'Completed',
                
                // Common Buttons and Actions
                'button.close': 'Close',
                'button.cancel': 'Cancel',
                'button.save': 'Save',
                'button.edit': 'Edit',
                'button.delete': 'Delete',
                'button.view': 'View',
                'button.download': 'Download',
                'button.refresh': 'Refresh',
                
                // Messages
                'message.success': 'Completed successfully.',
                'message.error': 'An error occurred.',
                'message.loading': 'Loading...',
                'message.no-data': 'No data available.',
                'message.confirm': 'Are you sure you want to proceed?',
                
                // Theme and Settings
                'theme.dark': 'Dark Mode',
                'theme.light': 'Light Mode',
                'language.korean': '한국어',
                'language.english': 'English',
                
                // Word Quotation Generation
                'word.generating': 'Generating test Word quotation...',
                'word.success': 'Test Word quotation generated successfully!',
                'word.error': 'Error generating Word quotation.',
                'word.download-error': 'Word quotation generation failed',
                
                // Quotation Modal
                'quotations.download': 'Download Word Quotation',
                'quotations.summary': 'Quotation Summary',
                'quotations.client': 'Client Name',
                'quotations.standards': 'Standards',
                'quotations.enp': 'Total ENP',
                'quotations.audit-days': 'Total Audit Days',
                'quotations.audit-fee': 'Audit Fee',
                'quotations.expenses': 'Expenses',
                'quotations.total-cost': 'Total Cost',
                'quotations.breakdown': 'Standards Breakdown',
                'quotations.standard': 'Standard',
                'quotations.complexity': 'Complexity',
                'quotations.stage1': 'Stage1',
                'quotations.stage2': 'Stage2',
                'quotations.surveillance': 'Surveillance',
                'quotations.recertification': 'Recertification',
                'quotations.total-days': 'Total Days',
                
                // 견적서 이력 관리
                'history.title': 'Quotation History Management',
                'history.stats': 'Statistics',
                'history.total': 'Total Quotations',
                'history.monthly': 'This Month',
                'history.total-value': 'Total Quotation Value',
                'history.average-value': 'Average Quotation Value',
                'history.search': 'Search',
                'history.search-placeholder': 'Search client name, contact person...',
                'history.filter-standard': 'Standard Filter',
                'history.filter-status': 'Status Filter',
                'history.filter-date-from': 'From Date',
                'history.filter-date-to': 'To Date',
                'history.filter-apply': 'Apply Filters',
                'history.filter-reset': 'Reset',
                'history.export-csv': 'Export CSV',
                'history.id': 'ID',
                'history.date': 'Created',
                'history.client': 'Client',
                'history.contact': 'Contact',
                'history.standards': 'Standards',
                'history.enp': 'ENP',
                'history.days': 'Audit Days',
                'history.cost': 'Total Cost',
                'history.status': 'Status',
                'history.actions': 'Actions',
                'history.no-data': 'No history available.',
                'history.status-generated': 'Generated',
                'history.status-sent': 'Sent',
                'history.status-approved': 'Approved',
                'history.status-rejected': 'Rejected',
                
                // 차트 관련
                'charts.monthly-trend': 'Monthly Quotation Trend',
                'charts.status-distribution': 'Status Distribution',
                'charts.standard-distribution': 'Standard Distribution',
                'charts.value-trend': 'Value Trend',
                
                // 수정 모달
                'edit.title': 'Edit Quotation',
                'edit.basic-info': 'Basic Information',
                'edit.client-name': 'Client Name',
                'edit.contact-person': 'Contact Person',
                'edit.phone': 'Phone',
                'edit.email': 'Email',
                'edit.standards-info': 'Standards Information',
                'edit.standards': 'Standards',
                'edit.pricing-info': 'Pricing Information',
                'edit.total-enp': 'Total ENP',
                'edit.audit-days': 'Total Audit Days',
                'edit.audit-fee': 'Audit Fee (KRW)',
                'edit.expenses': 'Expenses (KRW)',
                'edit.total-cost': 'Total Cost (KRW)',
                'edit.additional-info': 'Additional Information',
                'edit.status': 'Status',
                'edit.notes': 'Notes',
                'edit.recalculate': 'Recalculate',
                'edit.save': 'Save',
            }
        };
        
        this.init();
    }
    
    init() {
        this.updatePageLanguage();
        this.createLanguageToggle();
    }
    
    // 언어 전환
    switchLanguage(lang) {
        if (lang && this.translations[lang]) {
            this.currentLanguage = lang;
            localStorage.setItem('language', lang);
            this.updatePageLanguage();
            this.updateLanguageToggle();
        }
    }
    
    // 번역 텍스트 가져오기
    t(key) {
        return this.translations[this.currentLanguage][key] || key;
    }
    
    // 페이지의 모든 텍스트 업데이트
    updatePageLanguage() {
        // data-i18n 속성을 가진 모든 요소 업데이트
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translatedText = this.t(key);
            
            // placeholder 속성 처리
            if (element.hasAttribute('placeholder')) {
                element.placeholder = translatedText;
            } else {
                element.textContent = translatedText;
            }
        });
        
        // title 속성 업데이트
        const titleElements = document.querySelectorAll('[data-i18n-title]');
        titleElements.forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });
    }
    
    // 언어 토글 버튼 생성
    createLanguageToggle() {
        // 기존 언어 토글이 있으면 제거
        const existingToggle = document.getElementById('languageToggle');
        if (existingToggle) {
            existingToggle.remove();
        }
        
        const languageToggle = document.createElement('button');
        languageToggle.id = 'languageToggle';
        languageToggle.className = 'language-toggle';
        languageToggle.innerHTML = `
            <span class="language-toggle-icon">🌐</span>
            <span class="language-toggle-text">${this.currentLanguage === 'ko' ? 'English' : '한국어'}</span>
        `;
        languageToggle.addEventListener('click', () => {
            this.switchLanguage(this.currentLanguage === 'ko' ? 'en' : 'ko');
        });
        
        document.body.appendChild(languageToggle);
    }
    
    // 언어 토글 버튼 업데이트
    updateLanguageToggle() {
        const toggleButton = document.getElementById('languageToggle');
        if (toggleButton) {
            const text = toggleButton.querySelector('.language-toggle-text');
            text.textContent = this.currentLanguage === 'ko' ? 'English' : '한국어';
        }
    }
    
    // 현재 언어 반환
    getCurrentLanguage() {
        return this.currentLanguage;
    }
}

// 전역 언어 관리자 인스턴스
let languageManager;

// DOM 로드 완료 후 초기화
document.addEventListener('DOMContentLoaded', function() {
    languageManager = new LanguageManager();
});

// 편의 함수
function t(key) {
    return languageManager ? languageManager.t(key) : key;
}
