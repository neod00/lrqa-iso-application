/**
 * 견적서 이력 관리 시스템
 * 견적서 저장, 조회, 수정, 삭제 기능 제공
 */

class QuotationHistoryManager {
    constructor() {
        this.storageKey = 'lrqa_quotation_history';
        this.quotations = this.loadQuotations();
    }

    /**
     * 로컬 스토리지에서 견적서 이력 로드
     */
    loadQuotations() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('견적서 이력 로드 오류:', error);
            return [];
        }
    }

    /**
     * 견적서 이력을 로컬 스토리지에 저장
     */
    saveQuotations() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.quotations));
        } catch (error) {
            console.error('견적서 이력 저장 오류:', error);
        }
    }

    /**
     * 새 견적서 추가
     */
    addQuotation(quotationData) {
        const quotation = {
            id: this.generateId(),
            applicationId: quotationData.application_id || 'Unknown',
            clientName: quotationData.client_name,
            contactPerson: quotationData.contact_person,
            phone: quotationData.phone,
            email: quotationData.email,
            standards: quotationData.standards,
            totalENP: quotationData.total_enp,
            totalAuditDays: quotationData.total_audit_days,
            auditFee: quotationData.audit_fee,
            expenses: quotationData.expenses,
            totalCost: quotationData.total_cost,
            quotationBreakdown: quotationData.quotation_breakdown,
            assumptions: quotationData.assumptions,
            justification: quotationData.justification,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            status: 'generated', // generated, sent, approved, rejected
            downloadCount: 0,
            notes: ''
        };

        this.quotations.unshift(quotation); // 최신 견적서를 맨 앞에 추가
        this.saveQuotations();
        return quotation;
    }

    /**
     * 견적서 목록 조회 (페이징 지원)
     */
    getQuotations(page = 1, limit = 10, filters = {}) {
        let filtered = [...this.quotations];

        // 필터링
        if (filters.clientName) {
            filtered = filtered.filter(q => 
                q.clientName.toLowerCase().includes(filters.clientName.toLowerCase())
            );
        }

        if (filters.standards) {
            filtered = filtered.filter(q => 
                q.standards.some(s => s.toLowerCase().includes(filters.standards.toLowerCase()))
            );
        }

        if (filters.status) {
            filtered = filtered.filter(q => q.status === filters.status);
        }

        if (filters.dateFrom) {
            filtered = filtered.filter(q => new Date(q.createdAt) >= new Date(filters.dateFrom));
        }

        if (filters.dateTo) {
            filtered = filtered.filter(q => new Date(q.createdAt) <= new Date(filters.dateTo));
        }

        // 페이징
        const total = filtered.length;
        const start = (page - 1) * limit;
        const end = start + limit;
        const data = filtered.slice(start, end);

        return {
            data,
            pagination: {
                page,
                limit,
                total,
                pages: Math.ceil(total / limit)
            }
        };
    }

    /**
     * 특정 견적서 조회
     */
    getQuotation(id) {
        return this.quotations.find(q => q.id === id);
    }

    /**
     * 견적서 수정
     */
    updateQuotation(id, updates) {
        const index = this.quotations.findIndex(q => q.id === id);
        if (index !== -1) {
            this.quotations[index] = {
                ...this.quotations[index],
                ...updates,
                updatedAt: new Date().toISOString()
            };
            this.saveQuotations();
            return this.quotations[index];
        }
        return null;
    }

    /**
     * 견적서 삭제
     */
    deleteQuotation(id) {
        const index = this.quotations.findIndex(q => q.id === id);
        if (index !== -1) {
            const deleted = this.quotations.splice(index, 1)[0];
            this.saveQuotations();
            return deleted;
        }
        return null;
    }

    /**
     * 견적서 다운로드 횟수 증가
     */
    incrementDownloadCount(id) {
        const quotation = this.getQuotation(id);
        if (quotation) {
            return this.updateQuotation(id, {
                downloadCount: quotation.downloadCount + 1
            });
        }
        return null;
    }

    /**
     * 견적서 상태 변경
     */
    updateStatus(id, status) {
        return this.updateQuotation(id, { status });
    }

    /**
     * 통계 정보 생성
     */
    getStatistics() {
        const total = this.quotations.length;
        const thisMonth = this.quotations.filter(q => {
            const date = new Date(q.createdAt);
            const now = new Date();
            return date.getMonth() === now.getMonth() && 
                   date.getFullYear() === now.getFullYear();
        }).length;

        const statusCounts = this.quotations.reduce((acc, q) => {
            acc[q.status] = (acc[q.status] || 0) + 1;
            return acc;
        }, {});

        const standardCounts = this.quotations.reduce((acc, q) => {
            q.standards.forEach(standard => {
                acc[standard] = (acc[standard] || 0) + 1;
            });
            return acc;
        }, {});

        const totalValue = this.quotations.reduce((sum, q) => sum + q.totalCost, 0);

        return {
            total,
            thisMonth,
            statusCounts,
            standardCounts,
            totalValue,
            averageValue: total > 0 ? totalValue / total : 0
        };
    }

    /**
     * 견적서 검색
     */
    searchQuotations(searchTerm) {
        const term = searchTerm.toLowerCase();
        return this.quotations.filter(q => 
            q.clientName.toLowerCase().includes(term) ||
            q.contactPerson.toLowerCase().includes(term) ||
            q.standards.some(s => s.toLowerCase().includes(term)) ||
            q.notes.toLowerCase().includes(term)
        );
    }

    /**
     * 견적서 복제
     */
    duplicateQuotation(id) {
        const original = this.getQuotation(id);
        if (original) {
            const duplicate = {
                ...original,
                id: this.generateId(),
                clientName: original.clientName + ' (복사본)',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                status: 'generated',
                downloadCount: 0
            };
            this.quotations.unshift(duplicate);
            this.saveQuotations();
            return duplicate;
        }
        return null;
    }

    /**
     * 견적서 데이터 내보내기 (CSV)
     */
    exportToCSV() {
        const headers = [
            'ID', '생성일', '고객명', '담당자', '연락처', '이메일', 
            '표준', 'ENP', '심사일수', '심사비', '제경비', '총액', '상태', '다운로드수'
        ];

        const rows = this.quotations.map(q => [
            q.id,
            new Date(q.createdAt).toLocaleDateString('ko-KR'),
            q.clientName,
            q.contactPerson,
            q.phone,
            q.email,
            q.standards.join(', '),
            q.totalENP,
            q.totalAuditDays,
            q.auditFee.toLocaleString(),
            q.expenses.toLocaleString(),
            q.totalCost.toLocaleString(),
            this.getStatusText(q.status),
            q.downloadCount
        ]);

        const csvContent = [headers, ...rows]
            .map(row => row.map(field => `"${field}"`).join(','))
            .join('\n');

        return csvContent;
    }

    /**
     * 상태 텍스트 반환
     */
    getStatusText(status) {
        const statusTexts = {
            'generated': '생성됨',
            'sent': '발송됨',
            'approved': '승인됨',
            'rejected': '거절됨'
        };
        return statusTexts[status] || status;
    }

    /**
     * 고유 ID 생성
     */
    generateId() {
        return 'QUO_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
    }

    /**
     * 데이터 초기화 (개발/테스트용)
     */
    clearAll() {
        this.quotations = [];
        this.saveQuotations();
    }
}

// 전역 견적서 이력 관리자 인스턴스
const quotationHistory = new QuotationHistoryManager();
