"""
응답 생성기

주요 기능:
- 의도별 응답 생성
- LRQA 링크 매칭
- 개인화된 응답 생성
- 응답 품질 관리
"""

from typing import Dict, List, Any, Optional
from .knowledge_base import KnowledgeBase

class ResponseGenerator:
    """응답 생성기 클래스"""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.response_templates = self._load_response_templates()
        self.multilingual_templates = self._load_multilingual_templates()
    
    def _load_response_templates(self) -> Dict[str, str]:
        """응답 템플릿 로드"""
        return {
            'greeting': """안녕하세요! ISO-Guardian입니다. 😊

ISO 인증과 관련된 궁금한 점을 언제든 물어보세요. 저는 교육적 정보와 LRQA 프로세스 안내를 도와드립니다.

다음과 같은 질문을 도와드릴 수 있습니다:
• ISO 표준에 대한 설명
• 인증 프로세스 안내  
• 비용 및 견적 정보
• 교육 프로그램 안내

어떤 것이 궁금하신가요?""",

            'iso_standard': """ISO {standard} ({name})에 대해 설명드리겠습니다.

📋 **정의**: {description}

📝 **주요 요구사항**:
{requirements}

✅ **기대 효과**:
{benefits}

⏰ **구현 기간**: {implementation_time}
🔍 **심사 기간**: {audit_duration}

🎯 **적합한 업종**: {target_industries}""",

            'certification_process': """LRQA의 ISO 인증 프로세스를 안내드리겠습니다.

🔄 **인증 단계**:
{stages}

⏰ **소요 기간**: {timeline}

📋 **준비사항**:
{requirements}

💰 **비용 결정 요소**:
{cost_factors}""",

            'pricing': """ISO 인증 비용에 대해 안내드리겠습니다.

💰 **비용 결정 요소**:
• 기업 규모 (직원 수)
• 사업장 수  
• 선택한 ISO 표준
• 인증 범위
• 통합 심사 여부

정확한 견적을 받으시려면 신청서를 작성해주세요. ADJ v2.2 기준에 따라 정확하게 계산해드립니다.""",

            'education': """ISO 관련 교육에 대해 안내드리겠습니다.

📚 **LRQA 교육 프로그램**:
• 공개교육: 일반인 대상 교육 과정
• 온라인 교육: 언제든 접근 가능한 온라인 학습
• 맞춤형 교육: 기업별 특화 교육

교육을 통해 ISO 표준에 대한 이해를 높이고 인증 준비에 도움이 될 수 있습니다.""",

            'application': """ISO 인증 신청서 작성을 도와드리겠습니다.

📝 **신청서 작성 과정**:
1. 7페이지에 걸친 상세한 정보 입력
2. 실시간 유효성 검사
3. 자동 저장 및 복원
4. 갭분석 옵션 선택

신청서 작성을 시작하시겠습니까? 기존 신청서 시스템으로 연결해드리겠습니다.""",

            'help': """ISO-Guardian 사용법을 안내드리겠습니다.

❓ **주요 기능**:
• ISO 표준에 대한 질문 답변
• LRQA 인증 프로세스 안내
• 신청서 작성 지원
• 견적 요청 연결

💡 **사용 팁**:
• 구체적인 질문을 하시면 더 정확한 답변을 받을 수 있습니다
• 관련 LRQA 링크를 참고하세요
• 궁금한 점이 있으면 언제든 물어보세요!""",

            'general': """"{message}"에 대한 질문을 이해했습니다.

ISO-Guardian은 ISO 인증과 관련된 교육적 정보를 제공합니다.

다음과 같은 질문을 도와드릴 수 있습니다:
• ISO 표준에 대한 설명
• 인증 프로세스 안내
• 비용 및 견적 정보
• 교육 프로그램 안내

더 구체적으로 질문해주시면 정확한 답변을 드리겠습니다!"""
        }
    
    def _load_multilingual_templates(self) -> Dict[str, Dict[str, str]]:
        """다국어 응답 템플릿 로드"""
        return {
            'ko': self.response_templates,  # 기존 한국어 템플릿
            'en': {
                'greeting': """Hello! I'm ISO-Guardian. 😊

Feel free to ask any questions about ISO certification. I provide educational information and LRQA process guidance.

I can help you with:
• ISO standards explanations
• Certification process guidance
• Cost and quote information
• Education program information

What would you like to know?""",

                'iso_standard': """Let me explain ISO {standard} ({name}).

📋 **Definition**: {description}

📝 **Key Requirements**:
{requirements}

✅ **Expected Benefits**:
{benefits}

⏰ **Implementation Period**: {implementation_time}
🔍 **Audit Duration**: {audit_duration}

🎯 **Suitable Industries**: {target_industries}""",

                'certification_process': """Let me guide you through LRQA's ISO certification process.

🔄 **Certification Stages**:
{stages}

⏰ **Timeline**: {timeline}

📋 **Preparation Requirements**:
{requirements}

💰 **Cost Factors**:
{cost_factors}""",

                'pricing': """Let me provide information about ISO certification costs.

💰 **Cost Factors**:
• Company size (number of employees)
• Number of locations
• Selected ISO standards
• Certification scope
• Integrated audit option

For accurate quotes, please complete the application form. We calculate precisely according to ADJ v2.2 standards.""",

                'education': """Let me provide information about ISO-related education.

📚 **LRQA Education Programs**:
• Public Training: General education courses
• Online Training: Accessible online learning anytime
• Custom Training: Company-specific training

Education helps improve understanding of ISO standards and assists with certification preparation.""",

                'application': """Let me help you with ISO certification application.

📝 **Application Process**:
1. Detailed information input across 7 pages
2. Real-time validation
3. Auto-save and restore
4. Gap analysis option selection

Would you like to start the application? I'll connect you to the existing application system.""",

                'help': """Let me guide you on how to use ISO-Guardian.

❓ **Main Features**:
• Answer questions about ISO standards
• Guide LRQA certification process
• Support application writing
• Connect to quote requests

💡 **Usage Tips**:
• Ask specific questions for more accurate answers
• Refer to related LRQA links
• Feel free to ask anytime if you have questions!""",

                'general': """I understand your question about "{message}".

ISO-Guardian provides educational information about ISO certification.

I can help you with:
• ISO standards explanations
• Certification process guidance
• Cost and quote information
• Education program information

Please ask more specifically for accurate answers!"""
            }
        }
    
    def generate_response(self, message: str, intent: Dict[str, Any], 
                         knowledge_base: KnowledgeBase, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        응답 생성
        
        Args:
            message (str): 사용자 메시지
            intent (dict): 분류된 의도
            knowledge_base (KnowledgeBase): 지식베이스
            user_profile (dict): 사용자 프로파일
            
        Returns:
            dict: 생성된 응답
        """
        try:
            intent_type = intent.get('type', 'general')
            confidence = intent.get('confidence', 0.0)
            language = user_profile.get('preferredLanguage', 'ko')
            
            # 의도별 응답 생성
            if intent_type == 'greeting':
                return self._generate_greeting_response(language)
            elif intent_type == 'iso_standard':
                return self._generate_iso_standard_response(intent, knowledge_base, language)
            elif intent_type == 'certification_process':
                return self._generate_process_response(knowledge_base, language)
            elif intent_type == 'pricing':
                return self._generate_pricing_response(language)
            elif intent_type == 'education':
                return self._generate_education_response(language)
            elif intent_type == 'application':
                return self._generate_application_response(language)
            elif intent_type == 'help':
                return self._generate_help_response(language)
            else:
                return self._generate_general_response(message, knowledge_base, language)
                
        except Exception as e:
            return self._generate_error_response(str(e), user_profile.get('preferredLanguage', 'ko'))
    
    def _generate_greeting_response(self, language: str = 'ko') -> Dict[str, Any]:
        """인사 응답 생성"""
        templates = self.multilingual_templates.get(language, self.multilingual_templates['ko'])
        return {
            'success': True,
            'text': templates['greeting'],
            'lrqaLinks': self.knowledge_base.get_lrqa_links(language),
            'intent': 'greeting',
            'confidence': 1.0
        }
    
    def _generate_iso_standard_response(self, intent: Dict[str, Any], 
                                      knowledge_base: KnowledgeBase) -> Dict[str, Any]:
        """ISO 표준 응답 생성"""
        standard = intent.get('standard', 'general')
        
        if standard == 'general':
            return self._generate_iso_general_response()
        
        standard_info = knowledge_base.get_iso_standard_info(standard)
        if not standard_info:
            return self._generate_iso_general_response()
        
        # 응답 텍스트 생성
        text = self.response_templates['iso_standard'].format(
            standard=standard,
            name=standard_info['name'],
            description=standard_info['description'],
            requirements='\n'.join(f'• {req}' for req in standard_info['requirements']),
            benefits='\n'.join(f'• {benefit}' for benefit in standard_info['benefits']),
            implementation_time=standard_info['implementation_time'],
            audit_duration=standard_info['audit_duration'],
            target_industries=', '.join(standard_info['target_industries'])
        )
        
        # 관련 링크 생성
        lrqaLinks = knowledge_base.get_lrqa_links('iso_standards')
        
        return {
            'success': True,
            'text': text,
            'lrqaLinks': lrqaLinks,
            'intent': 'iso_standard',
            'confidence': intent.get('confidence', 0.8),
            'standard': standard
        }
    
    def _generate_iso_general_response(self) -> Dict[str, Any]:
        """ISO 일반 응답 생성"""
        text = """ISO(국제표준화기구)는 전 세계적으로 통용되는 표준을 제정하는 비정부기구입니다.

🏢 **주요 ISO 표준**:
• ISO 9001: 품질경영시스템
• ISO 14001: 환경경영시스템  
• ISO 45001: 안전보건경영시스템

각 표준에 대해 더 자세히 알고 싶으시면 구체적으로 질문해주세요!"""
        
        return {
            'success': True,
            'text': text,
            'lrqaLinks': self.knowledge_base.get_lrqa_links('iso_standards'),
            'intent': 'iso_standard',
            'confidence': 0.7
        }
    
    def _generate_process_response(self, knowledge_base: KnowledgeBase) -> Dict[str, Any]:
        """프로세스 응답 생성"""
        process_info = knowledge_base.get_process_info()
        
        # 단계별 설명 생성
        stages_text = '\n'.join([
            f"{stage['id']}. {stage['name']}: {stage['description']}"
            for stage in process_info['stages']
        ])
        
        # 요구사항 텍스트 생성
        requirements_text = '\n'.join([
            f"• {req}" for req in process_info['requirements']
        ])
        
        # 비용 요소 텍스트 생성
        cost_factors_text = '\n'.join([
            f"• {factor}" for factor in process_info['cost_factors']
        ])
        
        text = self.response_templates['certification_process'].format(
            stages=stages_text,
            timeline=process_info['timeline'],
            requirements=requirements_text,
            cost_factors=cost_factors_text
        )
        
        return {
            'success': True,
            'text': text,
            'lrqaLinks': knowledge_base.get_lrqa_links('process'),
            'intent': 'certification_process',
            'confidence': 0.9
        }
    
    def _generate_pricing_response(self) -> Dict[str, Any]:
        """가격 정보 응답 생성"""
        return {
            'success': True,
            'text': self.response_templates['pricing'],
            'lrqaLinks': self.knowledge_base.get_lrqa_links('pricing'),
            'intent': 'pricing',
            'confidence': 0.8
        }
    
    def _generate_education_response(self) -> Dict[str, Any]:
        """교육 정보 응답 생성"""
        return {
            'success': True,
            'text': self.response_templates['education'],
            'lrqaLinks': self.knowledge_base.get_lrqa_links('education'),
            'intent': 'education',
            'confidence': 0.8
        }
    
    def _generate_application_response(self) -> Dict[str, Any]:
        """신청서 작성 응답 생성"""
        return {
            'success': True,
            'text': self.response_templates['application'],
            'lrqaLinks': [
                {
                    'title': '신청서 작성 시작',
                    'url': '../Intergrated-ISO-application-GA/index.html'
                },
                {
                    'title': '신청 가이드',
                    'url': 'https://www.lrqa.com/kr/application-guide'
                }
            ],
            'intent': 'application',
            'confidence': 0.9
        }
    
    def _generate_help_response(self) -> Dict[str, Any]:
        """도움말 응답 생성"""
        return {
            'success': True,
            'text': self.response_templates['help'],
            'lrqaLinks': [
                {
                    'title': 'LRQA 홈페이지',
                    'url': 'https://www.lrqa.com/kr'
                },
                {
                    'title': '고객 지원',
                    'url': 'https://www.lrqa.com/kr/contact'
                }
            ],
            'intent': 'help',
            'confidence': 1.0
        }
    
    def _generate_general_response(self, message: str, knowledge_base: KnowledgeBase) -> Dict[str, Any]:
        """일반 응답 생성"""
        # FAQ에서 유사한 질문 찾기
        similar_faqs = knowledge_base.find_similar_questions(message, limit=1)
        
        if similar_faqs:
            faq = similar_faqs[0]
            text = f""""{message}"에 대한 질문을 이해했습니다.

{faq['answer']}

더 자세한 정보가 필요하시면 언제든 물어보세요!"""
            
            lrqaLinks = self.knowledge_base.get_lrqa_links()
        else:
            text = self.response_templates['general'].format(message=message)
            lrqaLinks = self.knowledge_base.get_lrqa_links()
        
        return {
            'success': True,
            'text': text,
            'lrqaLinks': lrqaLinks,
            'intent': 'general',
            'confidence': 0.5
        }
    
    def _generate_error_response(self, error_message: str) -> Dict[str, Any]:
        """오류 응답 생성"""
        return {
            'success': False,
            'text': '죄송합니다. 일시적인 오류가 발생했습니다. 다시 시도해주세요.',
            'lrqaLinks': [
                {
                    'title': 'LRQA 홈페이지',
                    'url': 'https://www.lrqa.com/kr'
                }
            ],
            'intent': 'error',
            'confidence': 0.0,
            'error': error_message
        }
    
    def personalize_response(self, response: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """응답 개인화"""
        # 사용자 경험 수준에 따른 응답 조정
        experience_level = user_profile.get('experience_level', 'beginner')
        
        if experience_level == 'beginner' and 'ISO' in response['text']:
            # 초보자용 추가 설명
            response['text'] += '\n\n💡 **초보자를 위한 팁**: ISO는 처음에는 복잡해 보일 수 있지만, 단계별로 접근하면 충분히 이해할 수 있습니다.'
        
        elif experience_level == 'advanced' and response['intent'] == 'iso_standard':
            # 고급자용 추가 정보
            response['text'] += '\n\n🔍 **고급 정보**: 더 구체적인 구현 방법이나 특정 업종별 적용 사례에 대해 질문해주세요.'
        
        # 사용자 관심사 반영
        interests = user_profile.get('interests', [])
        if interests and response['intent'] == 'iso_standard':
            related_standards = self.knowledge_base.get_related_standards(response.get('standard', ''))
            if related_standards:
                response['text'] += f'\n\n🔗 **관련 표준**: {", ".join(related_standards)}도 함께 고려해보시는 것을 추천드립니다.'
        
        return response
    
    def add_contextual_links(self, response: Dict[str, Any], message: str) -> Dict[str, Any]:
        """맥락적 링크 추가"""
        message_lower = message.lower()
        
        # 메시지 내용에 따른 추가 링크
        additional_links = []
        
        if '견적' in message_lower or '비용' in message_lower:
            additional_links.extend(self.knowledge_base.get_lrqa_links('pricing'))
        
        if '교육' in message_lower or '학습' in message_lower:
            additional_links.extend(self.knowledge_base.get_lrqa_links('education'))
        
        if '신청' in message_lower or '시작' in message_lower:
            additional_links.append({
                'title': '신청서 작성 시작',
                'url': '../Intergrated-ISO-application-GA/index.html'
            })
        
        # 중복 제거
        existing_urls = {link['url'] for link in response['lrqaLinks']}
        new_links = [link for link in additional_links if link['url'] not in existing_urls]
        
        response['lrqaLinks'].extend(new_links[:2])  # 최대 2개 추가
        
        return response
