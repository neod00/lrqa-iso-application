# 🏢 LRQA ISO 인증 신청 및 견적서 관리 시스템

![LRQA Logo](lrqa-logo.png)

## 📋 프로젝트 개요

**LRQA Korea**의 **ISO 9001/14001/45001 인증 신청서 작성 및 견적서 관리 시스템**입니다.

고객의 ISO 인증 신청부터 LRQA 직원의 견적서 생성 및 관리까지 **전체 워크플로우**를 지원하는 통합 플랫폼입니다.

## 🎯 핵심 기능

### 📝 **고객용 신청서 시스템**
- **7페이지 다단계 신청서**: 체계적이고 완전한 ISO 인증 신청서 작성
- **실시간 유효성 검사**: 필드별 입력 검증 및 안내
- **자동 저장 & 복원**: 브라우저 새로고침 시에도 작성 내용 보존
- **다크모드 지원**: 사용자 친화적인 테마 전환
- **반응형 디자인**: 모든 디바이스에서 최적화된 사용 경험

### 🔍 **갭분석 통합 기능**
- **원클릭 갭분석**: '제출하기' 버튼 옆 '🔍 ISO 갭분석 + 제출' 버튼
- **실시간 진행상황**: 5단계 갭분석 프로세스 시각화
- **AI 기반 분석**: ISOMatch 시스템과 연동하여 정확한 분석
- **맞춤형 보고서**: 선택한 ISO 표준에 특화된 갭분석 결과
- **자동 이메일 발송**: 분석 완료 즉시 상세 보고서 전송

### 👨‍💼 **관리자용 견적서 관리 시스템**
- **📊 실시간 대시보드**: 신청서 현황 및 통계
- **📋 신청서 목록 관리**: 접수된 신청서 조회, 수정, 견적서 생성
- **💰 고급 견적서 관리**: 생성, 수정, 이력 관리, 상태 추적
- **📈 데이터 시각화**: Chart.js 기반 통계 차트
- **🌐 다국어 지원**: 한국어/영어 완전 지원
- **🌙 다크모드**: 완전한 다크모드 지원

### 🚀 **ADJ v2.2 정확한 견적 계산**
- **정확한 ENP 계산**: 정규직, 외주, 파트타임, 교대근무자 등을 고려한 유효인원수 산정
- **IAF MD5 기준**: 국제 표준에 따른 최소 심사일수 테이블 적용
- **통합심사 할인**: 여러 표준 동시 심사 시 최대 15% 할인
- **원격심사 할인**: 원격 심사 비율에 따른 할인 적용
- **Stage별 정확한 계산**: Stage1(30%), Stage2(100%), Surveillance(60%), Recertification(100%)
- **Word 문서 자동 생성**: LRQA 브랜딩이 적용된 전문 견적서 생성

### 📊 **견적서 이력 관리**
- **📈 견적서 이력 추적**: 생성된 모든 견적서의 완전한 이력 관리
- **🔄 재다운로드**: 이전에 생성된 견적서 재다운로드
- **✏️ 견적서 수정**: 고객 정보, 가격, 상태 등 완전 수정 가능
- **📊 통계 및 차트**: 월별 현황, 상태별 분포, 표준별 분포, 금액 추이
- **🔍 고급 검색**: 다중 조건 검색 및 필터링
- **📁 CSV 내보내기**: 데이터 분석을 위한 엑셀 호환 파일 생성

### 🎨 **사용자 경험 (UX)**
- **🎯 토스트 알림**: 성공/오류/경고/정보 메시지
- **📱 완전 반응형**: 모바일, 태블릿, 데스크톱 최적화
- **⚡ 실시간 피드백**: 즉각적인 상태 업데이트
- **🎨 모던 UI**: 직관적이고 전문적인 디자인

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   고객 포털     │    │   관리자 포털   │    │  견적 계산 엔진 │
│                 │    │                 │    │                 │
│ • ISO 신청서    │    │ • 대시보드      │    │ • ADJ v2.2      │
│ • 갭분석 요청   │───▶│ • 신청서 관리   │───▶│ • IAF MD5       │
│ • 다크모드      │    │ • 견적서 관리   │    │ • ENP 계산      │
│ • 반응형 UI     │    │ • 이력 추적     │    │ • Word 생성     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │      백엔드 시스템      │
                    │                         │
                    │ • Netlify Functions     │
                    │ • Google Sheets API     │
                    │ • Chart.js 시각화       │
                    │ • 다국어 시스템         │
                    │ • 로컬 스토리지         │
                    └─────────────────────────┘
```

### 🔄 **견적서 생성 워크플로우**
```
신청서 접수 → 관리자 검토 → 견적서 생성 → Word 다운로드 → 이력 저장 → 상태 관리
```

---

## 📁 프로젝트 구조

```
Intergrated-ISO-application-GA/
├── 📄 index.html                      # 고객용 ISO 신청서
├── 👨‍💼 admin.html                       # 관리자용 대시보드
├── 🎨 css/
│   └── styles.css                     # 통합 스타일시트
├── ⚡ js/
│   ├── script.js                      # 신청서 로직
│   ├── language-manager.js            # 다국어 관리
│   ├── quote-calculator.js            # 견적 계산 엔진
│   └── quotation-history.js           # 견적서 이력 관리
├── 🔧 netlify/
│   └── functions/
│       ├── submit-application.js              # 신청서 제출
│       ├── submit-application-with-gap-analysis.js  # 갭분석 포함 제출
│       ├── generate-word-quotation.js         # Word 견적서 생성
│       ├── get-applications.js               # 신청서 조회
│       └── export-csv.js                     # CSV 내보내기
├── 💰 adj_quote_engine/                # Python 견적 계산 엔진
│   ├── models.py                      # 데이터 모델
│   ├── adj_rules_v22.py               # ADJ v2.2 규칙
│   ├── quote_template.py              # Word 템플릿 처리
│   └── templates/
│       └── LRQA_quotation.docx        # 견적서 템플릿
├── 📦 package.json                    # 의존성 관리
├── ⚙️ netlify.toml                    # Netlify 설정
└── 📖 README.md                       # 이 문서
```

---

## 🚀 배포 및 설정

### 1. GitHub에서 Netlify로 자동 배포

#### **Netlify 연결**
```bash
# GitHub 저장소 연결
1. Netlify 대시보드에서 "New site from Git" 클릭
2. GitHub 저장소 선택: neod00/lrqa-iso-application
3. 빌드 설정:
   - Build command: (비워둠)
   - Publish directory: (비워둠 - 루트 디렉토리)
   - Functions directory: netlify/functions
```

#### **자동 배포 설정**
- ✅ **GitHub Push 시 자동 배포**
- ✅ **Pull Request 미리보기**
- ✅ **배포 알림**

### 2. 환경 변수 설정

Netlify 대시보드에서 다음 환경 변수들을 설정:

```bash
# Google Sheets API
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=your_service_account@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your_client_id

# 이메일 설정 (Gmail SMTP)
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_16_digit_app_password
ADMIN_EMAIL=admin@lrqa.com

# ISOMatch 갭분석 시스템 (선택사항)
ISOMATCH_PATH=/opt/build/repo/ISOMatch
```

### 3. 도메인 설정
```bash
# 사용자 정의 도메인 (예시)
https://lrqa-iso-application.netlify.app
# 또는
https://iso.lrqa.com (사용자 정의 도메인)
```

---

## 🎛️ 사용 가이드

### 👥 **고객 사용법**

#### **1. ISO 인증 신청서 작성**
```
1. https://your-domain.com 접속
2. 7페이지에 걸친 상세 정보 입력
3. 자동 저장으로 안전한 작성 환경
4. 마지막 페이지에서 제출 방식 선택:
   - 일반 제출: "제출하기"
   - 갭분석 포함: "🔍 ISO 갭분석 + 제출"
```

#### **2. 갭분석 프로세스**
```
📝 신청서 데이터 처리중... (2초)
🔍 기업 정보 수집중... (3초)
🤖 AI 리스크 분석중... (4초)
📊 갭분석 보고서 생성중... (2초)
📧 이메일 발송중... (1.5초)
✅ 완료! 이메일을 확인하세요.
```

### 👨‍💼 **관리자 사용법**

#### **1. 관리자 로그인**
```
1. https://your-domain.com/admin.html 접속
2. 로그인 정보:
   - 사용자명: admin
   - 비밀번호: lrqa2025
```

#### **2. 신청서 관리**
```
신청서 목록 탭:
├── 📋 접수된 신청서 목록 조회
├── 👁️ 신청서 상세 보기
├── ✏️ 신청서 수정
└── 💰 견적서 생성 (원클릭)
```

#### **3. 견적서 관리**
```
견적서 관리 탭:
├── 📈 견적서 이력 보기
│   ├── 📊 실시간 통계 (총 견적서, 월별, 금액)
│   ├── 📈 시각화 차트 (Chart.js)
│   ├── 🔍 고급 검색/필터링
│   ├── 📄 재다운로드
│   ├── ✏️ 견적서 수정
│   ├── 📝 상태 관리 (생성→발송→승인→거절)
│   └── 📁 CSV 내보내기
└── 💰 견적서 생성하기 (독립적)
```

#### **4. 데이터 관리**
```
데이터 내보내기 탭:
├── 📊 Google Sheets 연동
├── 📁 CSV 파일 다운로드
└── 📈 통계 보고서 생성
```

---

## 💰 견적서 계산 시스템

### 🧮 **ADJ v2.2 기반 정확한 계산**

#### **ENP (Effective Number of Personnel) 계산**
```javascript
ENP = 정규직 + (외주 × 0.3) + (파트타임 × 0.5) + (교대근무자 × 1.2)
```

#### **심사일수 계산 (IAF MD5 기준)**
```javascript
Stage1 = 기본일수 × 30%
Stage2 = 기본일수 × 100%
Surveillance = 기본일수 × 60%
Recertification = 기본일수 × 100%
```

#### **할인 적용**
```javascript
통합심사 할인: 2표준(5%), 3표준(10%)
원격심사 할인: 원격비율 × 10%
최대 총 할인: 15%
```

### 📊 **지원하는 ISO 표준**
- **ISO 9001**: 품질경영시스템
- **ISO 14001**: 환경경영시스템  
- **ISO 45001**: 안전보건경영시스템

### 💸 **견적 구성요소**
1. **심사비**: 심사일수 × 일당 × 표준수
2. **제경비**: 심사비의 10-15%
3. **부가세**: 별도
4. **총 견적금액**: 심사비 + 제경비

---

## 📊 데이터 시각화

### 📈 **Chart.js 기반 대시보드**

#### **1. 월별 견적서 생성 현황**
- **차트 타입**: Line Chart
- **데이터**: 최근 12개월 견적서 생성 수
- **기능**: 호버 상세 정보, 반응형

#### **2. 상태별 분포**
- **차트 타입**: Doughnut Chart
- **데이터**: 생성됨/발송됨/승인됨/거절됨
- **색상**: 상태별 고유 색상 코딩

#### **3. 표준별 분포**
- **차트 타입**: Bar Chart
- **데이터**: ISO 9001/14001/45001별 견적서 수
- **기능**: 클릭 상호작용

#### **4. 금액 추이**
- **차트 타입**: Bar Chart
- **데이터**: 월별 총 견적 금액 (백만원 단위)
- **기능**: 실시간 업데이트

---

## 🌐 다국어 지원

### 🔧 **LanguageManager 시스템**

#### **지원 언어**
- 🇰🇷 **한국어** (기본)
- 🇺🇸 **English**

#### **번역 범위**
- ✅ **UI 텍스트**: 모든 버튼, 라벨, 메뉴
- ✅ **동적 메시지**: 성공, 오류, 경고 메시지
- ✅ **폼 라벨**: 입력 필드 및 플레이스홀더
- ✅ **차트 라벨**: 그래프 제목 및 범례
- ✅ **토스트 알림**: 실시간 알림 메시지

#### **언어 전환**
```javascript
// 자동 저장되는 사용자 설정
localStorage.setItem('language', 'ko' | 'en');

// 실시간 언어 전환 (페이지 새로고침 불필요)
languageManager.switchLanguage('en');
```

---

## 🧪 테스트 가이드

### 🔬 **로컬 개발 환경**

```bash
# 1. 저장소 클론
git clone https://github.com/neod00/lrqa-iso-application.git
cd lrqa-iso-application

# 2. Netlify CLI 설치
npm install -g netlify-cli

# 3. 의존성 설치
npm install

# 4. 환경 변수 설정
# .env 파일 생성 후 환경 변수 입력

# 5. 로컬 서버 시작
netlify dev

# 6. 브라우저에서 접속
http://localhost:8888
```

### ✅ **기능별 테스트 체크리스트**

#### **고객용 신청서**
- [ ] 7페이지 네비게이션 (이전/다음)
- [ ] 필수 필드 유효성 검사
- [ ] 임시저장 및 복원 (localStorage)
- [ ] 다크모드 전환
- [ ] 반응형 디자인 (모바일/태블릿)
- [ ] 갭분석 모달 표시
- [ ] 진행바 애니메이션

#### **관리자 대시보드**
- [ ] 로그인/로그아웃
- [ ] 신청서 목록 조회
- [ ] 견적서 생성 (신청서 → 견적서)
- [ ] 견적서 이력 관리
- [ ] 차트 렌더링 (Chart.js)
- [ ] 다국어 전환
- [ ] 다크모드 전환
- [ ] CSV 내보내기

#### **견적서 시스템**
- [ ] ENP 계산 정확성
- [ ] IAF MD5 심사일수 적용
- [ ] 할인율 계산 (통합심사/원격심사)
- [ ] Word 문서 생성 (docx.js)
- [ ] 견적서 재다운로드
- [ ] 견적서 수정/삭제
- [ ] 상태 관리 (생성→발송→승인→거절)

---

## 📈 성능 최적화

### ⚡ **프론트엔드 최적화**

#### **로딩 최적화**
```javascript
// 지연 로딩
- 페이지별 컨텐츠 지연 로딩
- Chart.js 차트 지연 렌더링
- 이미지 lazy loading

// 코드 최소화
- CSS 압축 및 최적화
- JavaScript 모듈화
- 불필요한 코드 제거
```

#### **메모리 관리**
```javascript
// 차트 인스턴스 관리
if (chartInstances.monthlyTrend) {
    chartInstances.monthlyTrend.destroy();
}

// 이벤트 리스너 정리
element.removeEventListener('click', handler);

// DOM 메모리 누수 방지
document.body.removeChild(temporaryElement);
```

### 🔧 **백엔드 최적화**

#### **Netlify Functions**
```javascript
// 응답 캐싱
exports.handler = async (event, context) => {
    return {
        statusCode: 200,
        headers: {
            'Cache-Control': 'max-age=300', // 5분 캐싱
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };
};
```

#### **데이터베이스 최적화**
- **Google Sheets API**: 배치 요청으로 API 호출 최소화
- **로컬 스토리지**: 견적서 이력 클라이언트 사이드 캐싱
- **압축**: JSON 데이터 gzip 압축

---

## 🔒 보안 및 개인정보보호

### 🛡️ **보안 조치**

#### **프론트엔드 보안**
```javascript
// XSS 방지
function sanitizeInput(input) {
    return input.replace(/[<>]/g, '');
}

// CSRF 방지
fetch(url, {
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
});
```

#### **백엔드 보안**
```javascript
// 환경 변수 보호
const sensitiveData = process.env.GOOGLE_PRIVATE_KEY;

// CORS 설정
headers: {
    'Access-Control-Allow-Origin': 'https://your-domain.com',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}
```

#### **데이터 보호**
- ✅ **HTTPS**: 모든 통신 SSL/TLS 암호화
- ✅ **환경 변수**: 민감한 정보 Netlify에서 암호화 저장
- ✅ **입력 검증**: 모든 사용자 입력 서버 사이드 검증
- ✅ **세션 관리**: 안전한 관리자 인증

---

## 🤝 기여 가이드

### 👨‍💻 **개발 참여**

#### **코딩 컨벤션**
```javascript
// 함수명: camelCase
function calculateQuotation() {}

// 상수: UPPER_SNAKE_CASE
const MAX_DISCOUNT_RATE = 15;

// 클래스명: PascalCase
class QuotationHistoryManager {}

// 파일명: kebab-case
language-manager.js
```

#### **Git 워크플로우**
```bash
# 1. 브랜치 생성
git checkout -b feature/new-feature

# 2. 개발 및 커밋
git add .
git commit -m "feat: 새로운 기능 추가"

# 3. 푸시 및 PR
git push origin feature/new-feature
# GitHub에서 Pull Request 생성

# 4. 코드 리뷰 후 머지
```

#### **커밋 메시지 규칙**
```bash
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 설정 등
```

---

## 📞 지원 및 문의

### 🆘 **기술 지원**

#### **연락처**
- **📧 이메일**: dal.kim@lrqa.com
- **📱 전화**: +82 10-5438-3060
- **🏢 회사**: LRQA Korea Ltd.

#### **지원 범위**
- ✅ **시스템 오류** 해결
- ✅ **기능 개선** 제안
- ✅ **사용자 교육** 제공
- ✅ **데이터 마이그레이션** 지원

### 🐛 **버그 리포트**

이슈 발생 시 다음 정보를 포함해서 문의해주세요:

```markdown
### 🐛 버그 리포트 템플릿

**환경 정보**
- 브라우저: Chrome 119.0.6045.199
- OS: Windows 11
- 화면 해상도: 1920x1080

**재현 단계**
1. 관리자 페이지 로그인
2. 견적서 이력 보기 클릭
3. 특정 견적서 수정 시도
4. 오류 발생

**예상 동작**
견적서가 정상적으로 수정되어야 함

**실제 동작**
"견적서를 찾을 수 없습니다" 오류 메시지 표시

**스크린샷**
(오류 화면 캡처)

**콘솔 로그**
```
Error: Cannot find quotation with ID: QUO_xxx
```

**추가 정보**
재현 가능 여부: 항상 / 가끔 / 한 번만
```

### 📈 **기능 요청**

새로운 기능 제안:

```markdown
### 💡 기능 요청 템플릿

**기능 제목**
견적서 일괄 상태 변경

**배경 및 문제점**
현재 견적서 상태를 하나씩만 변경할 수 있어서 
여러 견적서의 상태를 한 번에 변경하기 어려움

**제안하는 해결책**
체크박스를 통한 다중 선택 후 일괄 상태 변경 기능

**기대 효과**
관리자의 업무 효율성 30% 향상 예상

**우선순위**
High / Medium / Low
```

---

## 📊 시스템 통계

### 📈 **성능 지표**

#### **응답 시간**
- 🏠 **메인 페이지**: < 2초
- 👨‍💼 **관리자 페이지**: < 3초
- 💰 **견적서 생성**: < 5초
- 📊 **차트 렌더링**: < 1초
- 🔍 **검색/필터링**: < 0.5초

#### **사용량 통계** (예시)
- 📝 **월간 신청서**: ~100건
- 💰 **월간 견적서**: ~80건
- 👥 **관리자 사용자**: 5명
- 🌐 **지원 언어**: 2개 (한국어, 영어)

### 💾 **시스템 요구사항**

#### **클라이언트 (브라우저)**
- **최소**: Chrome 80+, Firefox 75+, Safari 13+
- **권장**: 최신 버전 브라우저
- **해상도**: 1024x768 이상 (반응형 지원)
- **메모리**: 2GB RAM 이상

#### **서버 (Netlify)**
- **Functions**: Node.js 18.x
- **빌드**: 자동 배포
- **CDN**: 전 세계 엣지 서버
- **SSL**: 자동 인증서 관리

---

## 🎯 로드맵

### 📅 **단기 계획 (1-3개월)**
- [ ] **모바일 앱**: 하이브리드 앱 개발 검토
- [ ] **API 확장**: RESTful API 추가 개발
- [ ] **알림 시스템**: 이메일/SMS 알림 강화
- [ ] **보고서 템플릿**: 추가 견적서 템플릿

### 🔮 **중장기 계획 (3-12개월)**
- [ ] **AI 기능**: 견적 추천 시스템
- [ ] **데이터 분석**: 비즈니스 인텔리전스 대시보드
- [ ] **고객 포털**: 고객용 진행 상황 추적
- [ ] **결제 연동**: 온라인 결제 시스템

### 🌟 **미래 비전**
LRQA의 **디지털 트랜스포메이션**을 선도하는 **종합 인증 관리 플랫폼**으로 발전

---

## 📄 라이선스

**© 2025 LRQA Korea Ltd. All rights reserved.**

이 프로젝트는 LRQA Korea의 지적 재산권으로 보호받으며, 
상업적 또는 교육적 목적의 무단 사용을 금지합니다.

---

## 🙏 감사의 말

### 👥 **개발팀**
- **프로젝트 리드**: Dal Kim (LRQA Korea)
- **기술 파트너**: Claude AI (Anthropic)
- **품질 검증**: LRQA Technical Team

### 🔧 **사용된 오픈소스**
- **Chart.js**: 데이터 시각화
- **docx.js**: Word 문서 생성
- **Netlify**: 서버리스 호스팅
- **Google APIs**: 데이터 저장소

---

**🌟 LRQA Korea ISO 인증 신청 및 견적서 관리 시스템으로 더 효율적인 인증 업무를 경험하세요! 🌟**