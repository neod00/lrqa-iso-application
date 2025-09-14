/**
 * LRQA 데이터 API
 * 
 * 주요 기능:
 * - LRQA 링크 데이터 제공
 * - 링크 유효성 검사
 * - 링크 클릭 분석 데이터 수집
 * - 지식베이스 데이터 제공
 */

exports.handler = async (event, context) => {
    // CORS 헤더 설정
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // OPTIONS 요청 처리
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    try {
        console.log('=== LRQA 데이터 API 요청 처리 ===');
        
        const { httpMethod, queryStringParameters, body } = event;
        const action = queryStringParameters?.action || 'links';

        let result;

        switch (action) {
            case 'links':
                result = await getLRQALinks(queryStringParameters);
                break;
            case 'validate':
                result = await validateLinks(JSON.parse(body || '{}'));
                break;
            case 'analytics':
                result = await handleAnalytics(JSON.parse(body || '{}'));
                break;
            case 'knowledge':
                result = await getKnowledgeBase(queryStringParameters);
                break;
            default:
                throw new Error(`알 수 없는 액션: ${action}`);
        }

        console.log(`${action} 액션 처리 완료`);
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                data: result
            })
        };

    } catch (error) {
        console.error('LRQA 데이터 API 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: error.message,
                message: 'LRQA 데이터 처리 중 오류가 발생했습니다.'
            })
        };
    }
};

/**
 * LRQA 링크 데이터 가져오기
 */
async function getLRQALinks(params) {
    const { category, keyword, limit = 10 } = params;
    
    // LRQA 링크 데이터베이스
    const linkDatabase = {
        iso_standards: {
            '9001': {
                title: 'ISO 9001 품질경영시스템',
                url: 'https://www.lrqa.com/kr/iso9001',
                description: '품질경영시스템에 대한 상세 정보',
                keywords: ['9001', '품질', '품질경영', 'quality', 'qms'],
                category: 'iso_standard'
            },
            '14001': {
                title: 'ISO 14001 환경경영시스템',
                url: 'https://www.lrqa.com/kr/iso14001',
                description: '환경경영시스템에 대한 상세 정보',
                keywords: ['14001', '환경', '환경경영', 'environment', 'ems'],
                category: 'iso_standard'
            },
            '45001': {
                title: 'ISO 45001 안전보건경영시스템',
                url: 'https://www.lrqa.com/kr/iso45001',
                description: '안전보건경영시스템에 대한 상세 정보',
                keywords: ['45001', '안전', '보건', '안전보건', 'safety', 'ohsms'],
                category: 'iso_standard'
            },
            'general': {
                title: 'ISO 표준 전체 목록',
                url: 'https://www.lrqa.com/kr/iso-standards',
                description: '모든 ISO 표준에 대한 정보',
                keywords: ['iso', '표준', 'standard', '전체', '목록'],
                category: 'iso_standard'
            }
        },
        certification_process: {
            'overview': {
                title: '인증 프로세스 개요',
                url: 'https://www.lrqa.com/kr/certification-process',
                description: 'LRQA의 인증 프로세스 전체 안내',
                keywords: ['프로세스', '과정', '인증', 'process', 'certification'],
                category: 'process'
            },
            'stages': {
                title: '심사 단계별 설명',
                url: 'https://www.lrqa.com/kr/audit-stages',
                description: '1단계, 2단계 심사 과정 상세 안내',
                keywords: ['심사', '단계', '1단계', '2단계', 'audit', 'stage'],
                category: 'process'
            },
            'timeline': {
                title: '인증 일정 안내',
                url: 'https://www.lrqa.com/kr/certification-timeline',
                description: '인증 소요 기간 및 일정 정보',
                keywords: ['일정', '기간', '소요', 'timeline', 'schedule'],
                category: 'process'
            },
            'requirements': {
                title: '인증 요구사항',
                url: 'https://www.lrqa.com/kr/certification-requirements',
                description: '인증을 위한 필수 요구사항 안내',
                keywords: ['요구사항', '필수', '준비', 'requirements', 'prerequisites'],
                category: 'process'
            }
        },
        education: {
            'public_training': {
                title: '공개교육',
                url: 'https://www.lrqa.com/kr/public-training',
                description: 'ISO 표준 관련 공개교육 과정',
                keywords: ['공개교육', '교육', '훈련', 'training', 'public'],
                category: 'education'
            },
            'online_training': {
                title: '온라인 교육',
                url: 'https://www.lrqa.com/kr/online-training',
                description: '온라인 교육 프로그램',
                keywords: ['온라인', '교육', 'e-learning', 'online', 'training'],
                category: 'education'
            },
            'custom_training': {
                title: '맞춤형 교육',
                url: 'https://www.lrqa.com/kr/custom-training',
                description: '기업 맞춤형 교육 서비스',
                keywords: ['맞춤형', '기업', '교육', 'custom', 'corporate'],
                category: 'education'
            }
        },
        pricing: {
            'pricing_guide': {
                title: '요금 안내',
                url: 'https://www.lrqa.com/kr/pricing',
                description: 'ISO 인증 비용 안내',
                keywords: ['비용', '요금', '가격', 'pricing', 'cost'],
                category: 'pricing'
            },
            'quote_request': {
                title: '견적 요청',
                url: 'https://www.lrqa.com/kr/quote-request',
                description: '맞춤형 견적 요청',
                keywords: ['견적', '요청', 'quote', 'request'],
                category: 'pricing'
            },
            'calculator': {
                title: '견적 계산기',
                url: 'https://www.lrqa.com/kr/quote-calculator',
                description: '온라인 견적 계산 도구',
                keywords: ['계산기', '견적', 'calculator', 'estimate'],
                category: 'pricing'
            }
        },
        support: {
            'contact': {
                title: '문의하기',
                url: 'https://www.lrqa.com/kr/contact',
                description: 'LRQA 고객 지원 센터',
                keywords: ['문의', '연락', '지원', 'contact', 'support'],
                category: 'support'
            },
            'faq': {
                title: '자주 묻는 질문',
                url: 'https://www.lrqa.com/kr/faq',
                description: 'FAQ 및 일반적인 질문 답변',
                keywords: ['faq', '질문', '답변', '자주', '묻는'],
                category: 'support'
            },
            'help_center': {
                title: '도움말 센터',
                url: 'https://www.lrqa.com/kr/help',
                description: '종합 도움말 및 가이드',
                keywords: ['도움말', '가이드', 'help', 'guide'],
                category: 'support'
            }
        },
        resources: {
            'homepage': {
                title: 'LRQA 홈페이지',
                url: 'https://www.lrqa.com/kr',
                description: 'LRQA 공식 홈페이지',
                keywords: ['홈페이지', '메인', 'homepage', 'main'],
                category: 'general'
            },
            'news': {
                title: '뉴스 및 공지사항',
                url: 'https://www.lrqa.com/kr/news',
                description: '최신 뉴스 및 공지사항',
                keywords: ['뉴스', '공지', 'news', 'announcement'],
                category: 'general'
            },
            'case_studies': {
                title: '성공 사례',
                url: 'https://www.lrqa.com/kr/case-studies',
                description: '고객 성공 사례 및 후기',
                keywords: ['사례', '성공', '후기', 'case', 'success'],
                category: 'general'
            }
        }
    };

    let links = [];

    // 카테고리별 필터링
    if (category && linkDatabase[category]) {
        links = Object.values(linkDatabase[category]);
    } else {
        // 모든 링크 수집
        for (const cat in linkDatabase) {
            links = links.concat(Object.values(linkDatabase[cat]));
        }
    }

    // 키워드 필터링
    if (keyword) {
        const lowerKeyword = keyword.toLowerCase();
        links = links.filter(link => 
            link.keywords.some(kw => kw.toLowerCase().includes(lowerKeyword)) ||
            link.title.toLowerCase().includes(lowerKeyword) ||
            link.description.toLowerCase().includes(lowerKeyword)
        );
    }

    // 개수 제한
    links = links.slice(0, parseInt(limit));

    return {
        links,
        total: links.length,
        category: category || 'all',
        keyword: keyword || null
    };
}

/**
 * 링크 유효성 검사
 */
async function validateLinks(requestData) {
    const { urls } = requestData;
    const validationResults = [];

    for (const url of urls) {
        try {
            const response = await fetch(url, { 
                method: 'HEAD',
                timeout: 5000 
            });
            
            validationResults.push({
                url,
                isValid: response.ok,
                status: response.status,
                lastChecked: new Date().toISOString()
            });
        } catch (error) {
            validationResults.push({
                url,
                isValid: false,
                error: error.message,
                lastChecked: new Date().toISOString()
            });
        }
    }

    return {
        results: validationResults,
        totalChecked: urls.length,
        validCount: validationResults.filter(r => r.isValid).length
    };
}

/**
 * 분석 데이터 처리
 */
async function handleAnalytics(requestData) {
    const { action, data } = requestData;

    switch (action) {
        case 'track_click':
            return await trackLinkClick(data);
        case 'get_stats':
            return await getAnalyticsStats();
        default:
            throw new Error(`알 수 없는 분석 액션: ${action}`);
    }
}

/**
 * 링크 클릭 추적
 */
async function trackLinkClick(clickData) {
    // 실제 구현에서는 데이터베이스에 저장
    console.log('링크 클릭 추적:', clickData);
    
    return {
        success: true,
        message: '클릭 데이터가 저장되었습니다.',
        timestamp: new Date().toISOString()
    };
}

/**
 * 분석 통계 가져오기
 */
async function getAnalyticsStats() {
    // 실제 구현에서는 데이터베이스에서 통계 조회
    return {
        totalClicks: 0,
        topLinks: [],
        categoryBreakdown: {},
        timeRange: 'last_30_days'
    };
}

/**
 * 지식베이스 데이터 가져오기
 */
async function getKnowledgeBase(params) {
    const { type, standard } = params;

    const knowledgeBase = {
        iso_standards: {
            '9001': {
                name: '품질경영시스템',
                description: '고객 만족을 위한 품질 관리 시스템',
                requirements: ['고객 중심', '지속적 개선', '프로세스 접근법'],
                benefits: ['품질 향상', '고객 만족도 증가', '비용 절감'],
                keywords: ['품질', '고객만족', '지속적개선', '프로세스']
            },
            '14001': {
                name: '환경경영시스템',
                description: '환경 보호를 위한 경영 시스템',
                requirements: ['환경 정책', '법규 준수', '지속가능성'],
                benefits: ['환경 보호', '법규 준수', '이미지 향상'],
                keywords: ['환경', '지속가능성', '법규준수', '환경정책']
            },
            '45001': {
                name: '안전보건경영시스템',
                description: '직장 안전과 직원 건강을 위한 시스템',
                requirements: ['안전 정책', '위험 관리', '직원 참여'],
                benefits: ['사고 감소', '직원 안전', '생산성 향상'],
                keywords: ['안전', '보건', '위험관리', '직원안전']
            }
        },
        faq: [
            {
                question: 'ISO 인증이 무엇인가요?',
                answer: 'ISO 인증은 국제표준화기구에서 제정한 표준에 따라 기업의 경영시스템이 적절히 구축되어 있음을 인정받는 제도입니다.',
                category: 'basic',
                keywords: ['iso', '인증', '표준', '경영시스템']
            },
            {
                question: 'ISO 9001과 14001의 차이점은?',
                answer: 'ISO 9001은 품질경영시스템, ISO 14001은 환경경영시스템입니다. 9001은 고객 만족에, 14001은 환경 보호에 중점을 둡니다.',
                category: 'comparison',
                keywords: ['9001', '14001', '품질', '환경', '차이점']
            },
            {
                question: '인증 비용은 얼마나 드나요?',
                answer: '인증 비용은 기업 규모, 복잡도, 선택한 표준에 따라 달라집니다. 정확한 견적은 신청서 작성 후 제공됩니다.',
                category: 'cost',
                keywords: ['비용', '견적', '가격', '요금']
            }
        ],
        process: {
            stages: [
                { id: 1, name: '신청서 제출', description: 'ISO-Guardian을 통한 신청서 작성' },
                { id: 2, name: '1단계 심사', description: '문서 검토 및 사전 심사' },
                { id: 3, name: '2단계 심사', description: '현장 심사 및 인증 심사' },
                { id: 4, name: '인증서 발급', description: '심사 통과 시 인증서 발급' }
            ],
            timeline: '일반적으로 3-6개월 소요',
            requirements: ['필요한 문서 준비', '시스템 구축', '직원 교육']
        }
    };

    if (type === 'iso_standards') {
        if (standard && knowledgeBase.iso_standards[standard]) {
            return knowledgeBase.iso_standards[standard];
        }
        return knowledgeBase.iso_standards;
    }

    if (type === 'faq') {
        return knowledgeBase.faq;
    }

    if (type === 'process') {
        return knowledgeBase.process;
    }

    return knowledgeBase;
}
