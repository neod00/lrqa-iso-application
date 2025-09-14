"""
ISO-Guardian AI 에이전트 패키지

주요 기능:
- 자연어 처리 및 의도 분류
- 지식베이스 기반 응답 생성
- LRQA 링크 매칭
- 학습 및 적응 기능
"""

from .nlp_engine import NLPEngine
from .knowledge_base import KnowledgeBase
from .response_generator import ResponseGenerator

class ISOGuardianAI:
    """ISO-Guardian AI 에이전트 메인 클래스"""
    
    def __init__(self):
        self.nlp_engine = NLPEngine()
        self.knowledge_base = KnowledgeBase()
        self.response_generator = ResponseGenerator()
        self.conversation_history = []
        self.user_profile = {
            'interests': set(),
            'experience_level': 'beginner',
            'preferred_language': 'ko'
        }
    
    def process_message(self, message, conversation_history=None, user_profile=None):
        """
        사용자 메시지 처리
        
        Args:
            message (str): 사용자 메시지
            conversation_history (list): 대화 기록
            user_profile (dict): 사용자 프로파일
            
        Returns:
            dict: AI 응답
        """
        try:
            # 대화 기록 업데이트
            if conversation_history:
                self.conversation_history = conversation_history
            
            # 사용자 프로파일 업데이트
            if user_profile:
                self.user_profile.update(user_profile)
            
            # 의도 분류
            intent = self.nlp_engine.classify_intent(message)
            
            # 응답 생성
            response = self.response_generator.generate_response(
                message, intent, self.knowledge_base, self.user_profile
            )
            
            # 대화 기록에 추가
            self.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': self._get_timestamp()
            })
            
            self.conversation_history.append({
                'role': 'assistant',
                'content': response['text'],
                'timestamp': self._get_timestamp()
            })
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'text': '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
                'lrqaLinks': [],
                'intent': 'error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _get_timestamp(self):
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self):
        """대화 기록 반환"""
        return self.conversation_history
    
    def get_user_profile(self):
        """사용자 프로파일 반환"""
        return {
            **self.user_profile,
            'interests': list(self.user_profile['interests'])
        }
    
    def reset(self):
        """AI 에이전트 상태 리셋"""
        self.conversation_history = []
        self.user_profile = {
            'interests': set(),
            'experience_level': 'beginner',
            'preferred_language': 'ko'
        }
