# 🤖 ISO-Guardian AI 에이전트 플랫폼

## 📋 프로젝트 개요

ISO-Guardian은 LRQA의 독립성과 공평성을 유지하면서 고객에게 ISO 인증 과정에 대한 교육적 지원과 투명한 프로세스 안내를 제공하는 AI 에이전트 플랫폼입니다.

## 🎯 핵심 가치

- **중립성**: 특정 결과나 서비스 추천 금지
- **교육성**: ISO 표준에 대한 지식 전달에 집중
- **투명성**: LRQA 인증 프로세스 명확한 안내
- **독립성**: LRQA의 독립적 심사 과정 존중

## 🏗️ 시스템 아키텍처

```
ISO-Guardian-Agent/
├── frontend/                 # 프론트엔드
│   ├── index.html           # 메인 페이지
│   ├── css/
│   │   └── styles.css       # 스타일시트
│   └── js/
│       ├── app.js           # 메인 애플리케이션
│       ├── ai-agent.js      # AI 에이전트 로직
│       └── lrqa-links.js    # LRQA 링크 관리
├── backend/                 # 백엔드
│   ├── netlify/
│   │   └── functions/
│   │       ├── ai-chat.js   # AI 채팅 API
│   │       └── lrqa-data.js # LRQA 데이터 API
│   └── python/
│       └── ai_agent/
│           ├── __init__.py
│           ├── nlp_engine.py    # 자연어 처리
│           ├── knowledge_base.py # 지식베이스
│           └── response_generator.py # 응답 생성
├── data/                    # 데이터
│   ├── knowledge_base/
│   │   ├── iso_standards.json
│   │   ├── lrqa_process.json
│   │   └── faq.json
│   └── templates/
│       └── responses.json
└── README.md
```

## 🚀 주요 기능

### 1. 교육적 정보 제공
- ISO 표준 개요 (9001, 14001, 45001)
- 전문 용어 사전
- 인증 과정 단계별 설명
- FAQ 시스템

### 2. LRQA 프로세스 안내
- 인증 프로세스 상세 안내
- 심사 기준 정보 제공
- 일정 및 비용 안내
- LRQA 홈페이지 연동

### 3. 신청서 작성 지원
- 기술적 지원 제공
- 유효성 검사
- 진행 상황 추적
- 기존 신청서 시스템 연결

## 🔧 기술 스택

### 프론트엔드
- HTML5, CSS3, JavaScript (ES6+)
- 반응형 웹 디자인
- RESTful API 통신

### 백엔드
- Netlify Functions (서버리스)
- Python AI 엔진
- JSON 기반 지식베이스

### AI 기능
- 자연어 처리
- 의도 분류
- 응답 생성
- 학습 기능

## 📊 사용자 시나리오

1. **신규 사용자**: AI가 인사말과 기본 안내 제공
2. **질문 답변**: ISO 관련 질문에 교육적 정보 제공
3. **프로세스 안내**: LRQA 인증 프로세스 설명
4. **신청서 연결**: 기존 신청서 시스템으로 연결
5. **LRQA 링크**: 관련 공식 페이지 추천

## 🚫 제한사항

- 컨설팅 역할 금지
- 특정 서비스 추천 금지
- 인증 결과 보장 금지
- 특별한 편의 제공 금지

## 📈 성공 지표

- 사용자 만족도: 4.5/5.0 이상
- 질문 해결율: 90% 이상
- 재방문율: 70% 이상
- 응답 시간: 2초 이내

## 🔗 연결 시스템

- **신청서 작성**: Intergrated-ISO-application-GA
- **갭분석**: ISOMatch
- **견적 요청**: adj_quote_engine
- **LRQA 홈페이지**: 공식 정보 연동

## 📞 지원

- 이메일: dal.kim@lrqa.com
- 전화: +82 10-5438-3060

---

**© 2025 LRQA Korea. 모든 권리 보유.**
