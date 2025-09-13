// GapAnalysisEngine.js
class GapAnalysisEngine {
    constructor() {
        this.isAnalyzing = false;
    }

    async generateGapAnalysis(formData, selectedStandards) {
        console.log('Generating gap analysis for:', formData.companyName, 'Standards:', selectedStandards);
        
        if (this.isAnalyzing) {
            throw new Error('갭분석이 이미 진행 중입니다.');
        }
        
        this.isAnalyzing = true;
        
        try {
            // API 호출을 통한 갭분석 실행
            const response = await fetch('/.netlify/functions/run-gap-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ formData, selectedStandards })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Gap analysis result:', result);
            
            if (result.success) {
                // 갭분석 보고서 이메일 발송
                await this.sendGapAnalysisEmail(formData, result.result.report);
                return result.result;
            } else {
                throw new Error(result.message || '갭분석 실행 중 오류가 발생했습니다.');
            }
        } catch (error) {
            console.error('Gap analysis error:', error);
            throw error;
        } finally {
            this.isAnalyzing = false;
        }
    }

    async sendGapAnalysisEmail(formData, reportContent) {
        console.log('Sending gap analysis email to:', formData.contactEmail);
        
        try {
            const response = await fetch('/.netlify/functions/send-gap-analysis-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipientEmail: formData.contactEmail,
                    companyName: formData.companyName,
                    reportContent: reportContent
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Gap analysis email sent result:', result);
            return result;
        } catch (error) {
            console.error('Email sending error:', error);
            // 이메일 발송 실패는 갭분석 전체를 실패시키지 않음
            return { success: false, error: error.message };
        }
    }

    // 갭분석 진행률 시뮬레이션
    simulateProgress(callback) {
        const steps = [
            { progress: 20, message: '신청서 데이터 처리중...' },
            { progress: 40, message: '기업 정보 수집중...' },
            { progress: 60, message: 'AI 리스크 분석중...' },
            { progress: 80, message: '갭분석 보고서 생성중...' },
            { progress: 100, message: '이메일 발송중...' }
        ];

        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                callback(steps[currentStep]);
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 1000);

        return interval;
    }
}

// 전역에서 사용할 수 있도록 설정
window.GapAnalysisEngine = GapAnalysisEngine;
