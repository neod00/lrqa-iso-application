"""
ChatGPT API를 활용한 지능형 비즈니스 인텔리전스 분석 모듈
"""

import json
import datetime as dt
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
import os

@dataclass
class RiskScenario:
    """리스크 시나리오 데이터 클래스"""
    scenario_id: str
    title: str
    description: str
    risk_level: str
    triggers: List[str]
    mitigation_strategies: List[str]
    timeline: str
    confidence: str
    # 확장/옵션 필드
    probability: Optional[str] = None
    impact: Optional[str] = None
    category: Optional[str] = None
    likelihood_num: Optional[int] = None
    impact_num: Optional[int] = None
    horizon: Optional[str] = None
    evidence: Optional[List[str]] = None

@dataclass
class ContextualAnalysis:
    """맥락적 분석 결과 데이터 클래스"""
    hidden_risks: List[str]
    market_context: str
    competitive_analysis: str
    regulatory_implications: str
    investor_sentiment: str
    recommendations: List[str]

class ChatGPTEnhancedAnalyzer:
    """ChatGPT API를 활용한 지능형 리스크 분석기"""
    
    def __init__(self, api_key: str):
        """초기화"""
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.max_tokens = 4000
        
    def analyze_risk_context(self, company_name: str, news_data: List[Dict], 
                           social_data: List[Dict], filings_data: List[Dict], industry: Optional[str] = None) -> ContextualAnalysis:
        """맥락적 리스크 분석 (업종 맞춤)"""
        
        # 데이터 요약 생성
        news_summary = self._summarize_news(news_data)
        social_summary = self._summarize_social_media(social_data)
        filings_summary = self._summarize_filings(filings_data)
        
        domain_focus = industry or "해당 업종"
        prompt = f"""
        당신은 전문적인 {domain_focus} 비즈니스 리스크 분석가입니다. {company_name}에 대한 다음 데이터를 종합적으로 분석하여 
        업종 맥락에서 숨겨진 리스크 요소와 시장 맥락을 파악해주세요.

        **뉴스 데이터 요약:**
        {news_summary}

        **소셜미디어 데이터 요약:**
        {social_summary}

        **공시 데이터 요약:**
        {filings_summary}

        **분석 영역 가이드(참고):**
        - 공급망/조달 및 파트너 리스크
        - 제품/서비스 품질, 출시 지연, 리콜
        - 사이버 보안/데이터 프라이버시
        - 규제/반독점/정책 변화
        - 시장/경쟁/브랜드 평판
        - 인력/문화/거버넌스
        - 환경/ESG 및 지정학 리스크

        다음 형식으로 분석 결과를 제공해주세요:
        {{
            "hidden_risks": ["숨겨진 리스크 요소 1", "숨겨진 리스크 요소 2", ...],
            "market_context": "업종 맥락 및 트렌드 분석",
            "competitive_analysis": "경쟁사 동향 및 시장 포지셔닝 분석",
            "regulatory_implications": "규제 환경 변화 및 영향",
            "investor_sentiment": "투자자 심리 및 시장 신뢰도",
            "recommendations": ["권장사항 1", "권장사항 2", ...]
        }}

        업종 특성을 고려하여 현실적이고 구체적인 분석을 제공해주세요.
        한국어로 답변해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            # 응답 내용 검증
            content = response.choices[0].message.content
            if not content or not content.strip():
                print(f"⚠️ ChatGPT 응답이 비어있습니다: {company_name}")
                raise ValueError("Empty response from ChatGPT")
            
            # JSON 형식 확인 및 파싱
            content = content.strip()
            if not (content.startswith('{') and content.endswith('}')):
                # JSON이 아닌 경우 {} 부분 추출 시도
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    content = content[start_idx:end_idx + 1]
                else:
                    print(f"⚠️ ChatGPT 응답이 JSON 형식이 아닙니다: {content[:200]}...")
                    raise ValueError("Invalid JSON format from ChatGPT")
            
            result = json.loads(content)
            return ContextualAnalysis(**result)
            
        except json.JSONDecodeError as e:
            print(f"📄 JSON 파싱 오류 - ChatGPT 응답: {content[:200] if 'content' in locals() else 'N/A'}...")
            print(f"맥락적 리스크 분석 중 JSON 오류 발생: {e}")
        except Exception as e:
            print(f"맥락적 리스크 분석 중 오류 발생: {e}")
            return self._get_fallback_analysis(company_name, industry)
    
    def generate_risk_scenarios(self, company_name: str, current_data: Dict, industry: Optional[str] = None, sources: Optional[List[Dict[str, str]]] = None) -> List[RiskScenario]:
        """미래 리스크 시나리오 생성 (업종 맞춤, RAG 근거 포함)"""
        
        domain_focus = industry or "해당 업종"
        sources = sources or []
        sources_block = "\n".join([f"- [{s.get('id')}] {s.get('title','')} | {s.get('date','')} | {s.get('url','')}" for s in sources[:20]])
        prompt = f"""
        당신은 전문적인 {domain_focus} 리스크 관리 컨설턴트입니다. {company_name}의 현재 상황과 아래의 출처 데이터를 근거로 
        향후 6개월 내 발생 가능한 {domain_focus} 리스크 시나리오를 5개 생성해주세요. 반드시 아래 출처 중 해당되는 항목의 ID를 evidence로 연결하세요.

        **현재 상황 요약:**
        - 회사명: {company_name}
        - 분석 일시: {dt.datetime.now().strftime('%Y년 %m월 %d일')}
        - 현재 리스크 점수: {current_data.get('risk_score', 'N/A')}
        - 주요 리스크 요소: {', '.join(current_data.get('risk_factors', ['N/A']))}
        
        **출처 데이터(요약 목록):**
        {sources_block if sources_block else '- (출처 없음)'}

        **핵심 리스크 영역(예시):**
        - 공급망/조달, 품질/리콜, 출시 지연
        - 사이버 보안/데이터 유출, 개인정보
        - 규제/반독점/정책, 플랫폼/스토어 정책
        - 시장/경쟁/브랜드 평판, 마케팅/광고 정책
        - 인력/거버넌스, ESG/환경, 지정학/환율

        각 시나리오는 다음 JSON 스키마를 엄격히 따르세요(모든 필수):
        {{
            "scenario_id": "문자열",
            "title": "문자열",
            "description": "문자열",
            "category": "공급망|제품|보안|규제|평판|ESG|시장|거버넌스",
            "likelihood_num": 1-5,
            "impact_num": 1-5,
            "risk_level": "매우 높음|높음|보통|낮음|매우 낮음",
            "horizon": "short|medium|long",
            "triggers": ["문자열", ...],
            "mitigation_strategies": ["문자열", ...],
            "timeline": "문자열",
            "confidence": "높음|보통|낮음",
            "evidence": ["출처 ID", ...]
        }}

        제약:
        - 반드시 위 출처 목록의 ID만 evidence에 넣으세요. 임의 출처 금지.
        - 출처가 전혀 맞지 않으면 시나리오를 생성하지 말고 근거가 있는 대안 시나리오를 생성하세요.
        - JSON 배열만 출력하세요. 설명/코드블록 금지.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.4
            )
            content = response.choices[0].message.content.strip()
            if not content:
                print("ChatGPT API가 빈 응답을 반환했습니다. 기본 시나리오를 사용합니다.")
                return self._get_fallback_scenarios(company_name, industry)
            # JSON 부분만 추출
            if "```json" in content and "```" in content:
                json_start = content.find("```json") + 7
                json_end = content.rfind("```")
                if json_start < json_end:
                    content = content[json_start:json_end].strip()
            try:
                scenarios = json.loads(content)
                return [RiskScenario(**scenario) for scenario in scenarios]
            except json.JSONDecodeError as json_error:
                print(f"JSON 파싱 오류 발생: {json_error}")
                if '[' in content and ']' in content:
                    start_idx = content.find('[')
                    end_idx = content.rfind(']') + 1
                    content = content[start_idx:end_idx]
                    try:
                        scenarios = json.loads(content)
                        return [RiskScenario(**scenario) for scenario in scenarios]
                    except json.JSONDecodeError:
                        print("배열 추출 후에도 JSON 파싱 실패")
                        return self._get_fallback_scenarios(company_name, industry)
                return self._get_fallback_scenarios(company_name, industry)
        except Exception as e:
            print(f"리스크 시나리오 생성 중 오류 발생: {e}")
            return self._get_fallback_scenarios(company_name, industry)
    
    def answer_question(self, company_name: str, question: str, current_data: Dict) -> str:
        """사용자 질문에 대한 지능형 답변"""
        
        prompt = f"""
        당신은 {company_name}의 비즈니스 리스크 분석 전문가입니다. 
        사용자의 질문에 대해 현재 데이터를 바탕으로 전문적이고 실용적인 답변을 제공해주세요.

        **현재 분석 데이터:**
        {json.dumps(current_data, ensure_ascii=False, indent=2)}

        **사용자 질문:**
        {question}

        답변 시 다음을 고려해주세요:
        1. 구체적인 데이터와 근거 제시
        2. 실용적인 조언과 권장사항
        3. 리스크 관리 관점에서의 해석
        4. 한국어로 명확하고 이해하기 쉽게 설명

        답변을 제공해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"질문 답변 중 오류가 발생했습니다: {e}"
    
    def generate_personalized_report(self, company_name: str, user_profile: str, 
                                   analysis_data: Dict) -> str:
        """사용자 프로필에 맞는 맞춤형 보고서 생성"""
        
        prompt = f"""
        당신은 전문적인 비즈니스 인텔리전스 보고서 작성자입니다. 
        {company_name}에 대한 분석 데이터를 바탕으로 {user_profile}에게 맞는 맞춤형 보고서를 작성해주세요.

        **사용자 프로필:**
        {user_profile}

        **분석 데이터:**
        {json.dumps(analysis_data, ensure_ascii=False, indent=2)}

        다음 형식으로 보고서를 작성해주세요:
        1. **실행 요약** - 핵심 내용을 한눈에 파악할 수 있도록
        2. **주요 리스크 요인** - 사용자 관점에서 중요한 리스크 요소
        3. **시장 기회** - 긍정적인 요소와 성장 가능성
        4. **권장사항** - 구체적이고 실행 가능한 조치사항
        5. **향후 전망** - 단기/중기/장기 관점에서의 전망

        {user_profile}의 관점과 필요에 맞게 작성해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"맞춤형 보고서 생성 중 오류가 발생했습니다: {e}"
    
    def _summarize_news(self, news_data: List[Dict]) -> str:
        """뉴스 데이터 요약"""
        if not news_data:
            return "뉴스 데이터가 없습니다."
        
        summary = []
        for i, news in enumerate(news_data[:10]):  # 상위 10개만
            title = news.get('title', '제목 없음')
            summary.append(f"{i+1}. {title}")
        
        return "\n".join(summary)
    
    def _summarize_social_media(self, social_data: List[Dict]) -> str:
        """소셜미디어 데이터 요약"""
        if not social_data:
            return "소셜미디어 데이터가 없습니다."
        
        summary = []
        for i, post in enumerate(social_data[:10]):  # 상위 10개만
            content = post.get('content', '내용 없음')[:100] + "..."
            summary.append(f"{i+1}. {content}")
        
        return "\n".join(summary)
    
    def _summarize_filings(self, filings_data: List[Dict]) -> str:
        """공시 데이터 요약"""
        if not filings_data:
            return "공시 데이터가 없습니다."
        
        summary = []
        for i, filing in enumerate(filings_data[:5]):  # 상위 5개만
            title = filing.get('title', '제목 없음')
            date = filing.get('date', '날짜 없음')
            summary.append(f"{i+1}. {title} ({date})")
        
        return "\n".join(summary)
    
    def _get_fallback_analysis(self, company_name: str = "회사", industry: Optional[str] = None) -> ContextualAnalysis:
        """오류 발생 시 기본 분석 결과 반환 (업종 중립)"""
        focus = industry or "해당 업종"
        return ContextualAnalysis(
            hidden_risks=[
                f"{company_name}의 공급망 차질과 핵심 부품/서비스 조달 리스크",
                f"{company_name}의 데이터 보안/프라이버시 이슈로 인한 규제/평판 리스크",
                f"{company_name}의 출시 지연/품질 이슈로 인한 매출 및 브랜드 리스크",
                f"{company_name}의 반독점/규제 환경 변화에 따른 사업 모델 리스크"
            ],
            market_context=f"{company_name}은(는) {focus} 특성상 기술/시장/규제 변화에 민감합니다. 공급망, 제품 경쟁력, 데이터/프라이버시, 정책 변화가 핵심 요인입니다.",
            competitive_analysis=f"{company_name}의 주요 경쟁사들은 제품/서비스 차별화와 생태계 확장을 통해 경쟁력을 강화하고 있습니다. 플랫폼/스토어 정책과 파트너십 전략이 중요합니다.",
            regulatory_implications=f"데이터, 개인정보, 플랫폼, 반독점, ESG 등 규제 리스크가 점차 확대되고 있습니다. {company_name}은(는) 법규 준수와 투명한 거버넌스 강화가 요구됩니다.",
            investor_sentiment=f"{company_name}에 대한 투자자들의 관심은 높으나, 경기/환율/규제/공급망 변수에 따라 변동성이 확대될 수 있습니다.",
            recommendations=[
                f"핵심 공급망 리스크 식별 및 대체/이원화 전략 추진",
                "제품/서비스 품질 모니터링 강화 및 리콜/CS 대응 매뉴얼 고도화",
                "데이터 보안/프라이버시/규제 대응 체계 강화",
                "생태계/플랫폼 전략 및 파트너십 다변화"
            ]
        )
    
    def _get_fallback_scenarios(self, company_name: str = "회사", industry: Optional[str] = None) -> List[RiskScenario]:
        """오류 발생 시 기본 시나리오 반환 (업종 중립)"""
        return [
            RiskScenario(
                scenario_id="fallback_1",
                title=f"{company_name} 공급망 차질 및 핵심 부품 부족",
                description=f"핵심 부품/서비스 조달 지연으로 출시 일정과 매출이 영향을 받을 수 있습니다.",
                probability="높음",
                impact="높음",
                risk_level="높음",
                triggers=["주요 공급사 생산중단", "물류 병목", "지정학 리스크", "환율 급변"],
                mitigation_strategies=["공급사 이원화", "재고 버퍼 확보", "대체 부품 인증"],
                timeline="3-6개월 내",
                confidence="보통"
            ),
            RiskScenario(
                scenario_id="fallback_2",
                title=f"{company_name} 데이터 유출/사이버 보안 침해",
                description="고객 데이터/지적재산 유출로 규제/평판 리스크가 확대될 수 있습니다.",
                probability="보통",
                impact="매우 높음",
                risk_level="높음",
                triggers=["취약점 미패치", "피싱/사회공학", "서드파티 보안 결함"],
                mitigation_strategies=["제로트러스트 도입", "보안 교육 강화", "서드파티 보안평가"],
                timeline="1-6개월 내",
                confidence="보통"
            ),
            RiskScenario(
                scenario_id="fallback_3",
                title=f"{company_name} 제품 품질 이슈 및 리콜",
                description="품질 결함/안전 문제로 리콜 발생 및 브랜드 신뢰 저하가 우려됩니다.",
                probability="보통",
                impact="높음",
                risk_level="보통",
                triggers=["공정 변경", "신규 부품 통합", "검증 미흡"],
                mitigation_strategies=["사전 검증 강화", "QA 자동화", "리콜 대응 매뉴얼"],
                timeline="3-12개월 내",
                confidence="보통"
            ),
            RiskScenario(
                scenario_id="fallback_4",
                title=f"{company_name} 규제/반독점/정책 변화",
                description="플랫폼/스토어 정책, 개인정보, 반독점 등 규제로 수익모델이 영향을 받을 수 있습니다.",
                probability="보통",
                impact="보통",
                risk_level="보통",
                triggers=["입법/사법 이슈", "규제기관 조사", "정책 가이드 업데이트"],
                mitigation_strategies=["정책 대응 로드맵", "준법감시 강화", "지역별 대안 설계"],
                timeline="6-12개월 내",
                confidence="보통"
            ),
            RiskScenario(
                scenario_id="fallback_5",
                title=f"{company_name} 브랜드 평판/시장 경쟁 심화",
                description="경쟁 심화/부정 이슈로 시장 점유율과 마진이 압박받을 수 있습니다.",
                probability="보통",
                impact="보통",
                risk_level="보통",
                triggers=["경쟁사 신제품", "부정 이슈 바이럴", "가격 경쟁"],
                mitigation_strategies=["차별화 포지셔닝", "위기 커뮤니케이션", "가격/제품 믹스 최적화"],
                timeline="3-9개월 내",
                confidence="보통"
            )
        ]

def interactive_risk_analysis(company_name: str, api_key: str):
    """대화형 리스크 분석 인터페이스"""
    
    analyzer = ChatGPTEnhancedAnalyzer(api_key)
    
    print(f"\n🤖 {company_name} 지능형 리스크 분석 시스템")
    print("=" * 50)
    print("질문을 입력하거나 'quit'를 입력하여 종료하세요.")
    print("예시 질문:")
    print("- 이 회사의 주요 리스크는 무엇인가요?")
    print("- 시장에서의 경쟁력은 어떤가요?")
    print("- 투자자에게 권장사항은 무엇인가요?")
    print("=" * 50)
    
    while True:
        try:
            user_question = input(f"\n💬 {company_name}에 대해 궁금한 점: ")
            
            if user_question.lower() in ['quit', '종료', '끝']:
                print("분석을 종료합니다. 감사합니다!")
                break
            
            if not user_question.strip():
                print("질문을 입력해주세요.")
                continue
            
            print("\n🔍 분석 중...")
            
            # 간단한 더미 데이터로 질문 답변 (실제로는 실제 데이터 사용)
            dummy_data = {
                "company_name": company_name,
                "risk_score": "보통",
                "risk_factors": ["시장 경쟁", "기술 변화", "규제 환경"]
            }
            
            answer = analyzer.answer_question(company_name, user_question, dummy_data)
            
            print(f"\n📊 답변:")
            print("-" * 40)
            print(answer)
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n\n분석이 중단되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # API 키 설정 (환경변수에서 가져오거나 직접 입력)
    API_KEY = "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"
    
    # 테스트 실행
    company_name = "NVIDIA"
    interactive_risk_analysis(company_name, API_KEY)
