"""
자연어 처리 엔진

주요 기능:
- 의도 분류
- 키워드 추출
- 감정 분석
- 문맥 이해
"""

import re
from typing import Dict, List, Tuple

class NLPEngine:
    """자연어 처리 엔진"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.keywords = self._load_keywords()
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """의도 분류 패턴 로드"""
        return {
            'iso_standard': [
                r'iso\s*9001', r'iso\s*14001', r'iso\s*45001',
                r'품질경영', r'환경경영', r'안전보건',
                r'품질관리', r'환경관리', r'안전관리'
            ],
            'certification_process': [
                r'인증\s*프로세스', r'인증\s*과정', r'심사\s*과정',
                r'1단계', r'2단계', r'인증\s*단계',
                r'인증\s*절차', r'심사\s*절차'
            ],
            'pricing': [
                r'비용', r'가격', r'견적', r'요금',
                r'얼마', r'돈', r'비용이'
            ],
            'education': [
                r'교육', r'훈련', r'학습', r'강의',
                r'공개교육', r'온라인교육', r'맞춤형교육'
            ],
            'application': [
                r'신청', r'시작', r'작성', r'제출',
                r'신청서', r'지원'
            ],
            'help': [
                r'도움', r'help', r'질문', r'궁금',
                r'어떻게', r'무엇', r'왜'
            ],
            'greeting': [
                r'안녕', r'hello', r'hi', r'반가워',
                r'처음', r'시작'
            ]
        }
    
    def _load_keywords(self) -> Dict[str, List[str]]:
        """키워드 사전 로드"""
        return {
            'iso_9001': ['9001', '품질', '품질경영', '품질관리', 'quality', 'qms'],
            'iso_14001': ['14001', '환경', '환경경영', '환경관리', 'environment', 'ems'],
            'iso_45001': ['45001', '안전', '보건', '안전보건', 'safety', 'ohsms'],
            'process': ['프로세스', '과정', '단계', '절차', 'process', 'stage'],
            'cost': ['비용', '가격', '견적', '요금', 'cost', 'price', 'pricing'],
            'education': ['교육', '훈련', '학습', '강의', 'education', 'training'],
            'application': ['신청', '시작', '작성', '제출', 'application', 'apply']
        }
    
    def classify_intent(self, message: str) -> Dict[str, any]:
        """
        사용자 메시지의 의도 분류
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            dict: 분류된 의도 정보
        """
        message_lower = message.lower()
        
        # 의도별 점수 계산
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            intent_scores[intent] = score
        
        # 가장 높은 점수의 의도 선택
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent] / len(self.intent_patterns[best_intent])
        else:
            best_intent = 'general'
            confidence = 0.0
        
        # ISO 표준 세부 분류
        standard = None
        if best_intent == 'iso_standard':
            standard = self._identify_iso_standard(message_lower)
        
        return {
            'type': best_intent,
            'standard': standard,
            'confidence': confidence,
            'keywords': self._extract_keywords(message_lower)
        }
    
    def _identify_iso_standard(self, message: str) -> str:
        """ISO 표준 식별"""
        if re.search(r'9001|품질', message):
            return '9001'
        elif re.search(r'14001|환경', message):
            return '14001'
        elif re.search(r'45001|안전|보건', message):
            return '45001'
        else:
            return 'general'
    
    def _extract_keywords(self, message: str) -> List[str]:
        """메시지에서 키워드 추출"""
        keywords = []
        for category, words in self.keywords.items():
            for word in words:
                if word in message:
                    keywords.append(word)
        return list(set(keywords))
    
    def extract_entities(self, message: str) -> Dict[str, List[str]]:
        """
        메시지에서 엔티티 추출
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            dict: 추출된 엔티티들
        """
        entities = {
            'iso_standards': [],
            'numbers': [],
            'companies': [],
            'locations': []
        }
        
        # ISO 표준 추출
        iso_patterns = [
            r'iso\s*(\d{4,5})',
            r'(\d{4,5})\s*표준'
        ]
        for pattern in iso_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            entities['iso_standards'].extend(matches)
        
        # 숫자 추출
        number_pattern = r'\d+'
        entities['numbers'] = re.findall(number_pattern, message)
        
        # 회사명 추출 (간단한 패턴)
        company_patterns = [
            r'([가-힣]+(?:주식회사|유한회사|회사|기업|그룹))',
            r'([A-Za-z]+(?:\s+[A-Za-z]+)*(?:\s+Inc\.?|\s+Corp\.?|\s+Ltd\.?))'
        ]
        for pattern in company_patterns:
            matches = re.findall(pattern, message)
            entities['companies'].extend(matches)
        
        return entities
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        두 텍스트 간의 유사도 계산
        
        Args:
            text1 (str): 첫 번째 텍스트
            text2 (str): 두 번째 텍스트
            
        Returns:
            float: 유사도 (0.0 ~ 1.0)
        """
        # 간단한 Jaccard 유사도 계산
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def preprocess_message(self, message: str) -> str:
        """
        메시지 전처리
        
        Args:
            message (str): 원본 메시지
            
        Returns:
            str: 전처리된 메시지
        """
        # 특수문자 제거 (일부는 유지)
        processed = re.sub(r'[^\w\s가-힣.,!?]', '', message)
        
        # 연속된 공백 제거
        processed = re.sub(r'\s+', ' ', processed)
        
        # 앞뒤 공백 제거
        processed = processed.strip()
        
        return processed
    
    def detect_language(self, message: str) -> str:
        """
        메시지 언어 감지
        
        Args:
            message (str): 사용자 메시지
            
        Returns:
            str: 감지된 언어 ('ko', 'en', 'mixed')
        """
        korean_chars = len(re.findall(r'[가-힣]', message))
        english_chars = len(re.findall(r'[a-zA-Z]', message))
        total_chars = len(re.sub(r'[^가-힣a-zA-Z]', '', message))
        
        if total_chars == 0:
            return 'unknown'
        
        korean_ratio = korean_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if korean_ratio > 0.7:
            return 'ko'
        elif english_ratio > 0.7:
            return 'en'
        else:
            return 'mixed'
    
    def generate_question_variations(self, original_question: str) -> List[str]:
        """
        원본 질문의 변형 생성
        
        Args:
            original_question (str): 원본 질문
            
        Returns:
            list: 질문 변형들
        """
        variations = [original_question]
        
        # 간단한 변형 패턴들
        patterns = [
            (r'무엇', '뭐'),
            (r'어떻게', '어떤 방법으로'),
            (r'왜', '어떤 이유로'),
            (r'언제', '몇 시에'),
            (r'어디서', '어느 곳에서')
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, original_question):
                variation = re.sub(pattern, replacement, original_question)
                variations.append(variation)
        
        return list(set(variations))
