"""
지식베이스 관리

주요 기능:
- ISO 표준 정보 관리
- FAQ 데이터 관리
- LRQA 프로세스 정보 관리
- 지식 검색 및 매칭
"""

import json
from typing import Dict, List, Any, Optional

class KnowledgeBase:
    """지식베이스 관리 클래스"""
    
    def __init__(self):
        self.iso_standards = self._load_iso_standards()
        self.faq_data = self._load_faq_data()
        self.process_info = self._load_process_info()
        self.lrqa_links = self._load_lrqa_links()
        
        # 다국어 데이터 로드
        self.multilingual_data = {
            'ko': {
                'iso_standards': self.iso_standards,
                'faq_data': self.faq_data,
                'process_info': self.process_info,
                'lrqa_links': self.lrqa_links
            },
            'en': {
                'iso_standards': self._load_iso_standards_en(),
                'faq_data': self._load_faq_data_en(),
                'process_info': self._load_process_info_en(),
                'lrqa_links': self._load_lrqa_links_en()
            }
        }
    
    def _load_iso_standards(self) -> Dict[str, Dict[str, Any]]:
        """ISO 표준 정보 로드"""
        return {
            '9001': {
                'name': '품질경영시스템',
                'full_name': 'ISO 9001:2015 품질경영시스템',
                'description': '고객 만족을 위한 품질 관리 시스템',
                'requirements': [
                    '고객 중심',
                    '지속적 개선',
                    '프로세스 접근법',
                    '리더십',
                    '사람들의 참여',
                    '관계 관리'
                ],
                'benefits': [
                    '품질 향상',
                    '고객 만족도 증가',
                    '비용 절감',
                    '시장 경쟁력 향상',
                    '직원 참여도 증대',
                    '프로세스 효율성 개선'
                ],
                'keywords': ['품질', '고객만족', '지속적개선', '프로세스', '품질관리'],
                'target_industries': ['제조업', '서비스업', '건설업', 'IT', '의료'],
                'implementation_time': '6-12개월',
                'audit_duration': '2-5일 (기업 규모에 따라)'
            },
            '14001': {
                'name': '환경경영시스템',
                'full_name': 'ISO 14001:2015 환경경영시스템',
                'description': '환경 보호를 위한 경영 시스템',
                'requirements': [
                    '환경 정책',
                    '법규 준수',
                    '지속가능성',
                    '환경 목표 설정',
                    '환경 성과 측정',
                    '지속적 개선'
                ],
                'benefits': [
                    '환경 보호',
                    '법규 준수',
                    '이미지 향상',
                    '비용 절감',
                    '환경 리스크 관리',
                    '지속가능한 경영'
                ],
                'keywords': ['환경', '지속가능성', '법규준수', '환경정책', '환경관리'],
                'target_industries': ['제조업', '화학업', '에너지', '건설업', '물류'],
                'implementation_time': '6-12개월',
                'audit_duration': '2-5일 (기업 규모에 따라)'
            },
            '45001': {
                'name': '안전보건경영시스템',
                'full_name': 'ISO 45001:2018 안전보건경영시스템',
                'description': '직장 안전과 직원 건강을 위한 시스템',
                'requirements': [
                    '안전 정책',
                    '위험 관리',
                    '직원 참여',
                    '안전 교육',
                    '사고 예방',
                    '지속적 개선'
                ],
                'benefits': [
                    '사고 감소',
                    '직원 안전',
                    '생산성 향상',
                    '법규 준수',
                    '보험료 절감',
                    '기업 이미지 향상'
                ],
                'keywords': ['안전', '보건', '위험관리', '직원안전', '사고예방'],
                'target_industries': ['제조업', '건설업', '화학업', '광업', '물류'],
                'implementation_time': '6-12개월',
                'audit_duration': '2-5일 (기업 규모에 따라)'
            }
        }
    
    def _load_faq_data(self) -> List[Dict[str, Any]]:
        """FAQ 데이터 로드"""
        return [
            {
                'question': 'ISO 인증이 무엇인가요?',
                'answer': 'ISO 인증은 국제표준화기구에서 제정한 표준에 따라 기업의 경영시스템이 적절히 구축되어 있음을 인정받는 제도입니다. 이를 통해 기업의 신뢰성과 경쟁력을 높일 수 있습니다.',
                'category': 'basic',
                'keywords': ['iso', '인증', '표준', '경영시스템', '신뢰성'],
                'related_standards': ['9001', '14001', '45001']
            },
            {
                'question': 'ISO 9001과 14001의 차이점은 무엇인가요?',
                'answer': 'ISO 9001은 품질경영시스템으로 고객 만족에 중점을 두고, ISO 14001은 환경경영시스템으로 환경 보호에 중점을 둡니다. 9001은 품질 향상, 14001은 환경 성과 개선이 주요 목표입니다.',
                'category': 'comparison',
                'keywords': ['9001', '14001', '품질', '환경', '차이점', '비교'],
                'related_standards': ['9001', '14001']
            },
            {
                'question': 'ISO 45001은 무엇인가요?',
                'answer': 'ISO 45001은 안전보건경영시스템으로 직장에서 직원의 안전과 건강을 보호하기 위한 시스템입니다. 사고 예방, 위험 관리, 직원 참여를 통해 안전한 작업환경을 조성합니다.',
                'category': 'safety',
                'keywords': ['45001', '안전', '보건', '사고예방', '위험관리'],
                'related_standards': ['45001']
            },
            {
                'question': '인증 비용은 얼마나 드나요?',
                'answer': '인증 비용은 기업 규모, 복잡도, 선택한 표준, 사업장 수에 따라 달라집니다. 정확한 견적은 신청서 작성 후 ADJ v2.2 기준에 따라 계산됩니다. 일반적으로 수백만원에서 수천만원 범위입니다.',
                'category': 'cost',
                'keywords': ['비용', '견적', '가격', '요금', '얼마'],
                'related_standards': ['9001', '14001', '45001']
            },
            {
                'question': '인증 과정은 어떻게 되나요?',
                'answer': 'LRQA의 인증 과정은 1) 신청서 제출, 2) 1단계 심사(문서 검토), 3) 2단계 심사(현장 심사), 4) 인증서 발급의 4단계로 구성됩니다. 일반적으로 3-6개월이 소요됩니다.',
                'category': 'process',
                'keywords': ['프로세스', '과정', '심사', '단계', '절차'],
                'related_standards': ['9001', '14001', '45001']
            },
            {
                'question': 'ISO 인증의 이점은 무엇인가요?',
                'answer': 'ISO 인증을 통해 품질 향상, 고객 만족도 증가, 비용 절감, 시장 경쟁력 향상, 직원 참여도 증대, 프로세스 효율성 개선 등의 이점을 얻을 수 있습니다.',
                'category': 'benefits',
                'keywords': ['이점', '효과', '장점', '혜택', '도움'],
                'related_standards': ['9001', '14001', '45001']
            },
            {
                'question': '인증을 받으려면 어떤 준비가 필요한가요?',
                'answer': '인증을 받기 위해서는 1) 필요한 문서 준비(품질매뉴얼, 절차서 등), 2) 시스템 구축 및 운영, 3) 직원 교육, 4) 내부심사 실시 등의 준비가 필요합니다.',
                'category': 'preparation',
                'keywords': ['준비', '필요', '요구사항', '문서', '교육'],
                'related_standards': ['9001', '14001', '45001']
            },
            {
                'question': '통합 인증이 무엇인가요?',
                'answer': '통합 인증은 여러 ISO 표준(예: 9001+14001+45001)을 하나의 시스템으로 통합하여 인증받는 방식입니다. 비용 절감, 관리 효율성 향상, 일관된 경영시스템 구축 등의 장점이 있습니다.',
                'category': 'integration',
                'keywords': ['통합', '통합인증', '여러표준', '효율성'],
                'related_standards': ['9001', '14001', '45001']
            }
        ]
    
    def _load_process_info(self) -> Dict[str, Any]:
        """LRQA 프로세스 정보 로드"""
        return {
            'stages': [
                {
                    'id': 1,
                    'name': '신청서 제출',
                    'description': 'ISO-Guardian을 통한 신청서 작성 및 제출',
                    'duration': '1-2주',
                    'requirements': ['회사 정보', 'ISO 표준 선택', '담당자 정보']
                },
                {
                    'id': 2,
                    'name': '1단계 심사',
                    'description': '문서 검토 및 사전 심사',
                    'duration': '1-2주',
                    'requirements': ['품질매뉴얼', '절차서', '기록서류']
                },
                {
                    'id': 3,
                    'name': '2단계 심사',
                    'description': '현장 심사 및 인증 심사',
                    'duration': '2-5일',
                    'requirements': ['현장 방문', '직원 인터뷰', '시스템 검토']
                },
                {
                    'id': 4,
                    'name': '인증서 발급',
                    'description': '심사 통과 시 인증서 발급',
                    'duration': '1-2주',
                    'requirements': ['심사 결과 검토', '인증서 제작', '발급']
                }
            ],
            'timeline': '일반적으로 3-6개월 소요',
            'requirements': [
                '필요한 문서 준비',
                '시스템 구축 및 운영',
                '직원 교육 실시',
                '내부심사 수행'
            ],
            'cost_factors': [
                '기업 규모 (직원 수)',
                '사업장 수',
                '선택한 ISO 표준',
                '인증 범위',
                '통합 심사 여부'
            ]
        }
    
    def _load_lrqa_links(self) -> Dict[str, List[Dict[str, str]]]:
        """LRQA 링크 정보 로드"""
        return {
            'iso_standards': [
                {
                    'title': 'ISO 9001 상세 정보',
                    'url': 'https://www.lrqa.com/kr/iso9001',
                    'description': '품질경영시스템에 대한 상세 정보'
                },
                {
                    'title': 'ISO 14001 상세 정보',
                    'url': 'https://www.lrqa.com/kr/iso14001',
                    'description': '환경경영시스템에 대한 상세 정보'
                },
                {
                    'title': 'ISO 45001 상세 정보',
                    'url': 'https://www.lrqa.com/kr/iso45001',
                    'description': '안전보건경영시스템에 대한 상세 정보'
                }
            ],
            'process': [
                {
                    'title': '인증 프로세스 상세 안내',
                    'url': 'https://www.lrqa.com/kr/certification-process',
                    'description': 'LRQA의 인증 프로세스 전체 안내'
                },
                {
                    'title': '심사 단계별 설명',
                    'url': 'https://www.lrqa.com/kr/audit-stages',
                    'description': '1단계, 2단계 심사 과정 상세 안내'
                },
                {
                    'title': '인증 일정 안내',
                    'url': 'https://www.lrqa.com/kr/certification-timeline',
                    'description': '인증 소요 기간 및 일정 정보'
                }
            ],
            'education': [
                {
                    'title': '공개교육',
                    'url': 'https://www.lrqa.com/kr/public-training',
                    'description': 'ISO 표준 관련 공개교육 과정'
                },
                {
                    'title': '온라인 교육',
                    'url': 'https://www.lrqa.com/kr/online-training',
                    'description': '온라인 교육 프로그램'
                },
                {
                    'title': '맞춤형 교육',
                    'url': 'https://www.lrqa.com/kr/custom-training',
                    'description': '기업 맞춤형 교육 서비스'
                }
            ],
            'pricing': [
                {
                    'title': '요금 안내',
                    'url': 'https://www.lrqa.com/kr/pricing',
                    'description': 'ISO 인증 비용 안내'
                },
                {
                    'title': '견적 요청',
                    'url': 'https://www.lrqa.com/kr/quote-request',
                    'description': '맞춤형 견적 요청'
                }
            ]
        }
    
    def _load_iso_standards_en(self) -> Dict[str, Dict[str, Any]]:
        """영문 ISO 표준 정보 로드"""
        try:
            with open('data/knowledge_base/iso_standards_en.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_faq_data_en(self) -> List[Dict[str, Any]]:
        """영문 FAQ 데이터 로드"""
        try:
            with open('data/knowledge_base/faq_en.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _load_process_info_en(self) -> Dict[str, Any]:
        """영문 프로세스 정보 로드"""
        try:
            with open('data/knowledge_base/lrqa_process_en.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_lrqa_links_en(self) -> Dict[str, List[Dict[str, str]]]:
        """영문 LRQA 링크 정보 로드"""
        return {
            'iso_standards': [
                {
                    'title': 'ISO 9001 Detailed Information',
                    'url': 'https://www.lrqa.com/en/iso9001',
                    'description': 'Detailed information about Quality Management System'
                },
                {
                    'title': 'ISO 14001 Detailed Information',
                    'url': 'https://www.lrqa.com/en/iso14001',
                    'description': 'Detailed information about Environmental Management System'
                },
                {
                    'title': 'ISO 45001 Detailed Information',
                    'url': 'https://www.lrqa.com/en/iso45001',
                    'description': 'Detailed information about Occupational Health and Safety Management System'
                }
            ],
            'process': [
                {
                    'title': 'Certification Process Guide',
                    'url': 'https://www.lrqa.com/en/certification-process',
                    'description': 'Complete guide to LRQA certification process'
                },
                {
                    'title': 'Audit Stages Explanation',
                    'url': 'https://www.lrqa.com/en/audit-stages',
                    'description': 'Detailed explanation of Stage 1 and Stage 2 audit processes'
                },
                {
                    'title': 'Certification Timeline',
                    'url': 'https://www.lrqa.com/en/certification-timeline',
                    'description': 'Information about certification duration and schedule'
                }
            ],
            'education': [
                {
                    'title': 'Public Training',
                    'url': 'https://www.lrqa.com/en/public-training',
                    'description': 'ISO standards related public training courses'
                },
                {
                    'title': 'Online Training',
                    'url': 'https://www.lrqa.com/en/online-training',
                    'description': 'Online training programs'
                },
                {
                    'title': 'Custom Training',
                    'url': 'https://www.lrqa.com/en/custom-training',
                    'description': 'Company-specific training services'
                }
            ],
            'pricing': [
                {
                    'title': 'Pricing Information',
                    'url': 'https://www.lrqa.com/en/pricing',
                    'description': 'ISO certification cost information'
                },
                {
                    'title': 'Quote Request',
                    'url': 'https://www.lrqa.com/en/quote-request',
                    'description': 'Custom quote request'
                }
            ]
        }
    
    def get_iso_standard_info(self, standard: str, language: str = 'ko') -> Optional[Dict[str, Any]]:
        """ISO 표준 정보 조회"""
        data = self.multilingual_data.get(language, self.multilingual_data['ko'])
        return data['iso_standards'].get(standard)
    
    def get_all_iso_standards(self, language: str = 'ko') -> Dict[str, Dict[str, Any]]:
        """모든 ISO 표준 정보 조회"""
        data = self.multilingual_data.get(language, self.multilingual_data['ko'])
        return data['iso_standards']
    
    def search_faq(self, query: str, category: str = None, language: str = 'ko') -> List[Dict[str, Any]]:
        """FAQ 검색"""
        results = []
        query_lower = query.lower()
        data = self.multilingual_data.get(language, self.multilingual_data['ko'])
        faq_data = data['faq_data']
        
        for faq in faq_data:
            if category and faq['category'] != category:
                continue
            
            # 키워드 매칭
            keyword_match = any(keyword in query_lower for keyword in faq['keywords'])
            question_match = query_lower in faq['question'].lower()
            answer_match = query_lower in faq['answer'].lower()
            
            if keyword_match or question_match or answer_match:
                results.append(faq)
        
        return results
    
    def get_faq_by_category(self, category: str, language: str = 'ko') -> List[Dict[str, Any]]:
        """카테고리별 FAQ 조회"""
        data = self.multilingual_data.get(language, self.multilingual_data['ko'])
        faq_data = data['faq_data']
        return [faq for faq in faq_data if faq['category'] == category]
    
    def get_process_info(self, language: str = 'ko') -> Dict[str, Any]:
        """프로세스 정보 조회"""
        data = self.multilingual_data.get(language, self.multilingual_data['ko'])
        return data['process_info']
    
    def get_lrqa_links(self, category: str = None, language: str = 'ko') -> List[Dict[str, str]]:
        """LRQA 링크 조회"""
        data = self.multilingual_data.get(language, self.multilingual_data['ko'])
        lrqa_links = data['lrqa_links']
        
        if category:
            return lrqa_links.get(category, [])
        else:
            all_links = []
            for links in lrqa_links.values():
                all_links.extend(links)
            return all_links
    
    def find_similar_questions(self, question: str, limit: int = 3) -> List[Dict[str, Any]]:
        """유사한 질문 찾기"""
        question_lower = question.lower()
        scored_faqs = []
        
        for faq in self.faq_data:
            score = 0
            
            # 질문 제목과의 유사도
            if question_lower in faq['question'].lower():
                score += 2
            
            # 키워드 매칭
            keyword_matches = sum(1 for keyword in faq['keywords'] if keyword in question_lower)
            score += keyword_matches * 0.5
            
            # 답변 내용과의 유사도
            if any(word in faq['answer'].lower() for word in question_lower.split()):
                score += 1
            
            if score > 0:
                scored_faqs.append((faq, score))
        
        # 점수순으로 정렬하고 상위 결과 반환
        scored_faqs.sort(key=lambda x: x[1], reverse=True)
        return [faq for faq, score in scored_faqs[:limit]]
    
    def get_related_standards(self, standard: str) -> List[str]:
        """관련 표준 조회"""
        related = []
        for faq in self.faq_data:
            if standard in faq.get('related_standards', []):
                related.extend(faq['related_standards'])
        
        return list(set(related))
    
    def get_implementation_guide(self, standard: str) -> Dict[str, Any]:
        """구현 가이드 조회"""
        standard_info = self.get_iso_standard_info(standard)
        if not standard_info:
            return {}
        
        return {
            'standard': standard,
            'name': standard_info['name'],
            'implementation_time': standard_info['implementation_time'],
            'audit_duration': standard_info['audit_duration'],
            'requirements': standard_info['requirements'],
            'benefits': standard_info['benefits'],
            'target_industries': standard_info['target_industries']
        }
