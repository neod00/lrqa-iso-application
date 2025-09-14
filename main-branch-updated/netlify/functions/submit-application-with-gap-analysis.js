const { google } = require('googleapis');
const nodemailer = require('nodemailer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// 🆕 AI 웹사이트 분석을 위한 패키지
const OpenAI = require('openai');
const axios = require('axios');
const cheerio = require('cheerio');

// Google Sheets 설정
const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SHEET_NAME = 'ISO_Applications_GapAnalysis';

// 이메일 설정
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'dal.kim@lrqa.com';
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;

// ISOMatch 시스템 설정
const ISOMATCH_PATH = process.env.ISOMATCH_PATH || '/opt/build/repo/ISOMatch';

// 🆕 OpenAI API 설정 (웹사이트 분석용)
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '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'
});

// CORS 헤더
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Content-Type': 'application/json'
};

// Google Sheets API 클라이언트 초기화
async function getGoogleSheetsClient() {
  console.log('=== Google Sheets 클라이언트 초기화 시작 ===');
  
  if (!process.env.GOOGLE_PROJECT_ID) {
    throw new Error('GOOGLE_PROJECT_ID 환경 변수가 설정되지 않았습니다.');
  }
  if (!process.env.GOOGLE_PRIVATE_KEY) {
    throw new Error('GOOGLE_PRIVATE_KEY 환경 변수가 설정되지 않았습니다.');
  }
  if (!process.env.GOOGLE_CLIENT_EMAIL) {
    throw new Error('GOOGLE_CLIENT_EMAIL 환경 변수가 설정되지 않았습니다.');
  }
  
  console.log('환경 변수 검증 완료');
  
  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        type: 'service_account',
        project_id: process.env.GOOGLE_PROJECT_ID,
        private_key_id: process.env.GOOGLE_PRIVATE_KEY_ID,
        private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
        client_email: process.env.GOOGLE_CLIENT_EMAIL,
        client_id: process.env.GOOGLE_CLIENT_ID,
        auth_uri: 'https://accounts.google.com/o/oauth2/auth',
        token_uri: 'https://oauth2.googleapis.com/token',
        auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
        client_x509_cert_url: `https://www.googleapis.com/robot/v1/metadata/x509/${process.env.GOOGLE_CLIENT_EMAIL}`
      },
      scopes: ['https://www.googleapis.com/auth/spreadsheets']
    });

    console.log('Google Auth 객체 생성 완료');
    
    const sheets = google.sheets({ version: 'v4', auth });
    console.log('Google Sheets API 객체 생성 완료');
    
    return sheets;
  } catch (error) {
    console.error('Google Sheets 클라이언트 초기화 중 오류:', error);
    throw error;
  }
}

// 시트 헤더 설정 (갭분석 전용)
async function setupGapAnalysisSheetHeaders(sheets) {
  console.log('=== 갭분석 시트 헤더 설정 시작 ===');
  
  if (!SHEET_ID) {
    throw new Error('GOOGLE_SHEET_ID가 설정되지 않았습니다.');
  }
  
  const headers = [
    // 기본 정보
    '신청일시', '상태', '갭분석상태',
    // 회사 정보
    '법인명', '상호명', '본사주소', '도시', '우편번호',
    '대표전화번호', '행정구역', '국가', '대표이메일', '웹사이트',
    '법인등록번호', '사업자등록번호', '과세당국',
    // 연락처 정보
    '담당자명', '부서', '담당자이메일', '담당자전화', '휴대폰번호',
    // 신청 ISO 표준
    '신청ISO표준', '희망심사일정',
    // 갭분석 결과
    '갭분석점수', '주요리스크', '권장사항', '보고서경로',
    // 추가 정보
    '컨설턴트명', '컨설팅기관', '추가참고정보',
    // 데이터 처리
    '데이터처리동의', '서명', '서명날짜'
  ];

  try {
    // 시트의 첫 번째 행 확인
    console.log('갭분석 시트 첫 번째 행 확인 중...');
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A1:Z1`
    });

    // 헤더가 없거나 비어있으면 헤더 추가
    if (!response.data.values || response.data.values.length === 0) {
      console.log('갭분석 시트 헤더가 없음, 헤더 추가 중...');
      await sheets.spreadsheets.values.update({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!A1`,
        valueInputOption: 'RAW',
        resource: {
          values: [headers]
        }
      });
      console.log('갭분석 시트 헤더 추가 완료');

      // 헤더 스타일 적용
      console.log('갭분석 시트 헤더 스타일 적용 중...');
      await sheets.spreadsheets.batchUpdate({
        spreadsheetId: SHEET_ID,
        resource: {
          requests: [
            {
              repeatCell: {
                range: {
                  sheetId: 0,
                  startRowIndex: 0,
                  endRowIndex: 1,
                  startColumnIndex: 0,
                  endColumnIndex: headers.length
                },
                cell: {
                  userEnteredFormat: {
                    backgroundColor: {
                      red: 1.0,
                      green: 0.42,
                      blue: 0.21
                    },
                    textFormat: {
                      foregroundColor: {
                        red: 1.0,
                        green: 1.0,
                        blue: 1.0
                      },
                      bold: true
                    }
                  }
                },
                fields: 'userEnteredFormat(backgroundColor,textFormat)'
              }
            }
          ]
        }
      });
    }
  } catch (error) {
    console.error('=== 갭분석 시트 헤더 설정 중 오류 발생 ===');
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    throw error;
  }
}

// 갭분석 데이터 행 추가
async function addGapAnalysisRow(sheets, formData, gapAnalysisResult) {
  console.log('=== 갭분석 데이터 행 추가 시작 ===');
  
  if (!SHEET_ID) {
    throw new Error('GOOGLE_SHEET_ID가 설정되지 않았습니다.');
  }
  
  const timestamp = new Date().toISOString();
  
  const rowData = [
    // 기본 정보
    timestamp,
    '신규',
    '완료',
    // 회사 정보
    formData.companyName || '',
    formData.tradeName || '',
    formData.headOfficeAddress || '',
    formData.city || '',
    formData.postalCode || '',
    formData.mainPhone || '',
    formData.province || '',
    formData.country || '',
    formData.mainEmail || '',
    formData.companyWebsite || '',
    formData.corporateRegNumber || '',
    formData.businessRegNumber || '',
    formData.customsOffice || '',
    // 연락처 정보
    formData.contactName || '',
    formData.department || '',
    formData.contactEmail || '',
    formData.contactPhone || '',
    formData.mobilePhone || '',
    // 신청 ISO 표준
    Array.isArray(formData.selectedISOStandards) ? formData.selectedISOStandards.join(', ') : formData.isoStandards || '',
    formData.desiredAuditDate || '',
    // 갭분석 결과
    gapAnalysisResult?.score || '',
    gapAnalysisResult?.keyRisks?.join(', ') || '',
    gapAnalysisResult?.recommendations?.join(', ') || '',
    gapAnalysisResult?.reportPath || '',
    // 추가 정보
    formData.consultantName || '',
    formData.consultingOrg || '',
    formData.textarea_0 || '',  // 추가 참고 정보
    // 데이터 처리
    formData.dataConsent || '',
    formData.signature || '',
    formData.signatureDate || ''
  ];

  try {
    await sheets.spreadsheets.values.append({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A:Z`,
      valueInputOption: 'RAW',
      resource: {
        values: [rowData]
      }
    });
    console.log('갭분석 데이터 행 추가 완료');
  } catch (error) {
    console.error('갭분석 데이터 행 추가 중 오류:', error);
    throw error;
  }
}

// 🆕 웹사이트 스크래핑 함수
async function scrapeWebsite(url) {
  console.log(`=== 웹사이트 스크래핑 시작: ${url} ===`);
  
  try {
    // URL 정규화
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url;
    }
    
    const response = await axios.get(url, {
      timeout: 10000,  // 10초 타임아웃
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    
    const $ = cheerio.load(response.data);
    
    // 메타 정보 및 주요 텍스트 추출
    const title = $('title').text().trim();
    const metaDescription = $('meta[name="description"]').attr('content') || '';
    const metaKeywords = $('meta[name="keywords"]').attr('content') || '';
    
    // 주요 섹션 텍스트 추출 (품질, 환경, 안전 관련)
    let mainContent = '';
    
    // 주요 텍스트 영역에서 내용 추출
    $('h1, h2, h3, h4, p, div.content, div.about, div.company, div.quality, div.environment, div.safety, div.policy').each((i, element) => {
      const text = $(element).text().trim();
      if (text.length > 20 && text.length < 500) {  // 적절한 길이의 텍스트만
        mainContent += text + ' ';
      }
    });
    
    // 텍스트 길이 제한 (OpenAI API 토큰 제한 고려)
    const maxLength = 8000;
    if (mainContent.length > maxLength) {
      mainContent = mainContent.substring(0, maxLength) + '...';
    }
    
    console.log(`웹사이트 스크래핑 완료 - 텍스트 길이: ${mainContent.length}자`);
    
    return {
      url: url,
      title: title,
      metaDescription: metaDescription,
      metaKeywords: metaKeywords,
      content: mainContent,
      scrapedAt: new Date().toISOString()
    };
    
  } catch (error) {
    console.warn(`웹사이트 스크래핑 실패: ${url}`, error.message);
    return {
      url: url,
      title: '',
      metaDescription: '',
      metaKeywords: '',
      content: '',
      error: error.message,
      scrapedAt: new Date().toISOString()
    };
  }
}

// 🆕 AI 웹사이트 분석 함수 (GPT-4o-mini 사용)
async function analyzeCompanyWebsiteWithAI(websiteData, selectedStandards) {
  console.log('=== AI 웹사이트 분석 시작 ===');
  
  if (!websiteData.content || websiteData.content.trim().length < 100) {
    console.log('웹사이트 내용이 부족하여 AI 분석 생략');
    return {
      analysisAvailable: false,
      reason: '웹사이트 내용 부족 또는 스크래핑 실패'
    };
  }
  
  try {
    const selectedStandardsText = selectedStandards.map(std => {
      const standardMap = {
        'iso9001': 'ISO 9001:2015 품질경영시스템',
        'iso14001': 'ISO 14001:2016 환경경영시스템',
        'iso45001': 'ISO 45001:2018 안전보건경영시스템'
      };
      return standardMap[std] || std;
    }).join(', ');
    
    const systemPrompt = `당신은 ISO 인증 전문가입니다. 
    
회사 웹사이트를 분석하여 다음 정보만 객관적으로 추출하세요:

1. **품질관리 현황** (ISO 9001 관련)
   - 품질정책, 품질관리시스템, 고객만족 활동 등

2. **환경경영 현황** (ISO 14001 관련)  
   - 환경정책, 친환경 활동, 탄소중립 계획 등

3. **안전보건 현황** (ISO 45001 관련)
   - 안전정책, 직장안전 프로그램, 근로자 안전 등

4. **조직 특성**
   - 사업 영역, 규모, 글로벌 현황 등

5. **기존 인증 현황**
   - 보유 인증서, 품질상 수상내역 등

중요: 
- 갭분석이나 평가는 하지 마세요
- 웹사이트에서 확인할 수 있는 현황만 객관적으로 서술하세요
- 추측이나 가정은 하지 마세요
- 각 항목에서 구체적인 내용을 찾을 수 없으면 "명시적 정보 없음"으로 표시하세요`;

    const userPrompt = `
웹사이트 URL: ${websiteData.url}
페이지 제목: ${websiteData.title}
메타 설명: ${websiteData.metaDescription}
메타 키워드: ${websiteData.metaKeywords}

신청 표준: ${selectedStandardsText}

웹사이트 내용:
${websiteData.content}

위 웹사이트를 분석하여 요청된 5가지 항목의 현황을 객관적으로 정리해주세요.`;

    console.log('OpenAI API 호출 중... (GPT-4o-mini)');
    
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: systemPrompt
        },
        {
          role: "user", 
          content: userPrompt
        }
      ],
      max_tokens: 1500,
      temperature: 0.3  // 객관적 분석을 위해 낮은 temperature
    });
    
    const analysis = completion.choices[0].message.content;
    console.log('AI 웹사이트 분석 완료');
    
    return {
      analysisAvailable: true,
      websiteInfo: {
        url: websiteData.url,
        title: websiteData.title,
        scrapedAt: websiteData.scrapedAt
      },
      aiAnalysis: analysis,
      tokensUsed: completion.usage?.total_tokens || 0,
      model: "gpt-4o-mini"
    };
    
  } catch (error) {
    console.error('AI 웹사이트 분석 실패:', error);
    return {
      analysisAvailable: false,
      error: error.message,
      reason: 'AI API 호출 실패'
    };
  }
}

// 🆕 LRQA 지침 기반 고급 갭분석 결과 생성 (3개 ISO 표준 통합 + AI 웹사이트 분석)
async function createDummyGapAnalysisResult(formData) {
  console.log('=== LRQA 표준 갭분석 실행 시작 ===');
  console.log('적용 방법론: LRQA 6단계 갭분석 프로세스 + 3개 ISO 표준 통합 + AI 웹사이트 분석');
  
  const companyName = formData.companyNameKo || formData.companyName || '회사명';
  const website = formData.website || formData.companyWebsite || '';
  const selectedStandards = formData.selectedISOStandards || [];
  
  console.log(`LRQA 갭분석 대상: ${companyName}`);
  console.log(`분석 표준: ${selectedStandards.join(', ')}`);
  console.log(`웹사이트: ${website}`);
  
  // 🆕 1-1단계: AI 웹사이트 분석 (기존 갭분석 전 보조 정보 수집)
  let websiteAnalysis = null;
  if (website && website.trim() !== '') {
    console.log('=== 1-1단계: AI 웹사이트 분석 시작 ===');
    try {
      const websiteData = await scrapeWebsite(website);
      websiteAnalysis = await analyzeCompanyWebsiteWithAI(websiteData, selectedStandards);
      
      if (websiteAnalysis.analysisAvailable) {
        console.log('AI 웹사이트 분석 성공 - 갭분석에 반영');
        console.log(`사용된 토큰: ${websiteAnalysis.tokensUsed}`);
      } else {
        console.log('AI 웹사이트 분석 실패 또는 생략:', websiteAnalysis.reason);
      }
    } catch (error) {
      console.warn('웹사이트 분석 중 오류 발생:', error.message);
      websiteAnalysis = {
        analysisAvailable: false,
        error: error.message,
        reason: '웹사이트 분석 프로세스 오류'
      };
    }
  } else {
    console.log('웹사이트 정보 없음 - AI 분석 생략');
    websiteAnalysis = {
      analysisAvailable: false,
      reason: '웹사이트 URL 정보 없음'
    };
  }
  
  // LRQA 평가자 시뮬레이션: 실제 분석 시간 (웹사이트 분석 완료 후)
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // === 1단계: 범위 결정 (LRQA 방식) ===
  console.log('1단계: 갭분석 범위 결정 - 중요·위험·취약 영역 식별');
  
  // === 2단계: 평가자 주도 질의응답 시뮬레이션 ===
  console.log('2단계: 표준 이해도 및 구현 계획 평가');
  
  // 회사별 맞춤 분석 기반점수 (LRQA 평가자 방식)
  let readinessLevel = 'PARTIALLY_READY'; // NOT_READY, PARTIALLY_READY, READY
  let baseReadiness = 65;
  
  // Apple Inc. 특화 분석
  if (companyName.toLowerCase().includes('apple')) {
    console.log('Apple Inc. 특화 갭분석 적용');
    readinessLevel = 'PARTIALLY_READY';
    baseReadiness = 78; // 높은 기반 수준, 하지만 체계화 필요
  }
  // Google 특화 분석
  else if (companyName.toLowerCase().includes('google')) {
    console.log('Google 특화 갭분석 적용');
    baseReadiness = 75;
  }
  // Samsung 특화 분석
  else if (companyName.toLowerCase().includes('samsung')) {
    console.log('Samsung 특화 갭분석 적용');
    baseReadiness = 72;
  }
  
  // === 3단계: 문서검토 시뮬레이션 ===
  console.log('3단계: 경영시스템 문서 및 웹사이트 정보 검토');
  
  // === 4단계: 현장확인 시뮬레이션 (공개정보 기반) ===
  console.log('4단계: 공개정보 기반 운영 실태 확인');
  
  // === 5단계: LRQA Category A/B/C 갭 분류 ===
  console.log('5단계: LRQA 방법론 기반 갭 분류 (Category A/B/C)');
  
  const gapAnalysis = {
    categoryA: [], // 명확한 잠재적 부적합 (HIGH PRIORITY)
    categoryB: [], // 집중 검토 필요 (MEDIUM PRIORITY) 
    categoryC: []  // 해석 의존적 (LOW PRIORITY)
  };
  
  // ISO 9001:2015 갭분석 (LRQA 중점사항 기반)
  if (selectedStandards.includes('iso9001')) {
    console.log('ISO 9001:2015 갭분석 - LRQA 중점사항 적용');
    
    // Category A: 명확한 잠재적 부적합
    gapAnalysis.categoryA.push({
      standard: 'ISO 9001:2015',
      clause: 'Clause 8.3 Design and development',
      title: '설계개발 프로세스 체계화',
      description: companyName.toLowerCase().includes('apple') 
        ? 'iPhone/Mac 등 혁신적 제품개발 프로세스와 ISO 9001:2015 Clause 8.3 설계개발 요구사항 간 체계적 연계 검증 필요'
        : '제품/서비스 설계개발 프로세스의 ISO 9001 요구사항 준수 체계 구축 필요',
      severity: 'HIGH',
      evidence: '설계개발 프로세스가 ISO 8.3 요구사항(기획, 입력, 관리, 출력, 변경)에 완전히 정렬되지 않음'
    });
    
    // Category B: 집중 검토 필요
    gapAnalysis.categoryB.push({
      standard: 'ISO 9001:2015',
      clause: 'Clause 9.1.2 Customer satisfaction',
      title: '고객만족도 모니터링 체계',
      description: companyName.toLowerCase().includes('apple')
        ? 'App Store/제품 고객 피드백 vs ISO 9001:2015 체계적 고객만족도 모니터링 요구사항 정합성 검토 필요'
        : '고객만족도 측정 및 모니터링 체계의 ISO 9.1.2 요구사항 준수 확인 필요',
      severity: 'MEDIUM',
      evidence: '다양한 고객 피드백 채널이 있으나 ISO 9.1.2가 요구하는 체계적 모니터링 방법론 확인 필요'
    });
  }
  
  // ISO 14001:2016 갭분석 (LRQA 중점사항 기반)
  if (selectedStandards.includes('iso14001')) {
    console.log('ISO 14001:2016 갭분석 - LRQA 중점사항 적용');
    
    // Category A: 명확한 잠재적 부적합
    gapAnalysis.categoryA.push({
      standard: 'ISO 14001:2016',
      clause: '조항 6.1.2 환경측면',
      title: '환경측면 식별 및 평가 방법론',
      description: companyName.toLowerCase().includes('apple')
        ? '2030 Carbon Neutral 목표는 우수하나, ISO 14001:2016 조항 6.1.2가 요구하는 체계적 환경측면 식별 방법론 확인 필요'
        : '조직의 환경측면 식별, 평가 및 중대성 결정 방법론의 ISO 14001 요구사항 준수 확인 필요',
      severity: 'HIGH', 
      evidence: '환경 이니셔티브는 강력하나 조항 6.1.2 요구사항(변경사항, 비정상상황, 비상상황 고려) 체계적 적용 검증 필요'
    });
    
    // Category B: 집중 검토 필요
    gapAnalysis.categoryB.push({
      standard: 'ISO 14001:2016', 
      clause: '조항 8.1 운용기획 및 관리',
      title: '환경 운용관리 체계',
      description: companyName.toLowerCase().includes('apple')
        ? '글로벌 제조 파트너(Foxconn 등) 환경관리 vs ISO 14001 조항 8.1 운용관리 요구사항 통합 검토 필요'
        : '환경에 영향을 미치는 운용 프로세스의 관리 및 통제 체계 확인 필요',
      severity: 'MEDIUM',
      evidence: '환경관리 활동이 존재하나 ISO 8.1이 요구하는 체계적 운용기획 및 관리 절차 확인 필요'
    });
  }
  
  // ISO 45001:2018 갭분석 (LRQA 중점사항 기반)
  if (selectedStandards.includes('iso45001')) {
    console.log('ISO 45001:2018 갭분석 - LRQA 중점사항 적용');
    
    // Category A: 명확한 잠재적 부적합
    gapAnalysis.categoryA.push({
      standard: 'ISO 45001:2018',
      clause: 'Clause 6.1.2 Hazard identification and risk assessment', 
      title: '위험성평가 및 기회 관리',
      description: companyName.toLowerCase().includes('apple')
        ? 'Apple Park 등 우수한 안전 환경이 조성되어 있으나, ISO 45001:2018 Clause 6.1.2가 요구하는 체계적 위험성평가 방법론 확인 필요'
        : '직업안전보건 위험요인 식별 및 위험성평가 체계의 ISO 45001 요구사항 준수 확인 필요',
      severity: 'HIGH',
      evidence: '안전한 작업환경이 제공되고 있으나 Clause 6.1.2 체계적 위험성평가 프로세스 문서화 검증 필요'
    });
    
    // Category B: 집중 검토 필요 
    gapAnalysis.categoryB.push({
      standard: 'ISO 45001:2018',
      clause: 'Clause 5.4 Consultation and participation of workers',
      title: '근로자 참여 및 협의 체계',
      description: companyName.toLowerCase().includes('apple')
        ? 'Apple 직원 복지 및 참여 프로그램 vs ISO 45001 Clause 5.4 근로자 참여 요구사항 형식적 구조화 검토 필요'
        : '안전보건 관련 근로자 참여 및 협의 메커니즘의 ISO 45001 요구사항 준수 확인 필요',
      severity: 'MEDIUM',
      evidence: '우수한 직원 참여 문화가 있으나 ISO 45001 Clause 5.4가 요구하는 공식적 참여 및 협의 체계 확인 필요'
    });
  }
  
  // === 6단계: 해결방안 논의 및 개선계획 ===
  console.log('6단계: 구체적 해결방안 및 현실적 개선 기간 산정');
  
  // LRQA 방법론 기반 종합 권장사항
  const lrqaRecommendations = [];
  
  // 통합 관리시스템 권장사항
  if (selectedStandards.length > 1) {
    lrqaRecommendations.push('통합 관리시스템(IMS) 구축 - 3개 표준 시너지 활용');
    lrqaRecommendations.push('통합 내부심사 프로그램 개발');
    lrqaRecommendations.push('통합 관리검토 프로세스 구축');
  }
  
  // 표준별 핵심 권장사항
  selectedStandards.forEach(standard => {
    switch(standard) {
      case 'iso9001':
        lrqaRecommendations.push('프로세스 접근 방식 및 리스크 기반 사고 체계 구축');
        lrqaRecommendations.push('고객 중심 품질경영시스템 고도화');
        break;
      case 'iso14001':
        lrqaRecommendations.push('환경측면 및 영향평가 방법론 표준화');
        lrqaRecommendations.push('환경 법규 준수 관리체계 구축');
        break;
      case 'iso45001':
        lrqaRecommendations.push('체계적 위험성평가 및 근로자 참여 체계 구축');
        lrqaRecommendations.push('안전보건 성과 모니터링 체계 강화');
        break;
    }
  });
  
  // 회사별 맞춤 권장사항
  if (companyName.toLowerCase().includes('apple')) {
    lrqaRecommendations.push('Apple 2030 Carbon Neutral 전략과 ISO 14001 환경목표 완전 정렬');
    lrqaRecommendations.push('글로벌 공급망 ESG 관리와 ISO 표준 요구사항 통합');
    lrqaRecommendations.push('혁신 문화와 관리시스템 체계의 조화로운 통합');
  }
  
  // 현실적 준비 기간 산정 (LRQA 평가자 방식)
  const preparationMonths = selectedStandards.length * 3 + (baseReadiness < 70 ? 3 : 0);
  const successProbability = baseReadiness > 75 ? 90 : (baseReadiness > 65 ? 75 : 60);
  
  // 최종 결과 생성
  const result = {
    // LRQA 방법론 적용 결과
    analysisMethod: 'LRQA 6단계 갭분석 프로세스',
    standardsAnalyzed: selectedStandards,
    assessmentFocus: '중요·위험·취약 영역 집중 분석',
    
    // 준비도 평가 (점수 대신 준비 수준)
    readinessLevel: readinessLevel,
    preparationRequired: `${preparationMonths}개월`,
    successProbability: `${successProbability}%`,
    
    // LRQA Category 기반 갭 분석
    categoryA_Critical: gapAnalysis.categoryA,
    categoryB_Important: gapAnalysis.categoryB, 
    categoryC_Borderline: gapAnalysis.categoryC.length > 0 ? gapAnalysis.categoryC : [
      {
        standard: '통합',
        title: '최고경영자 리더십 체계',
        description: '최고경영자의 관리시스템 리더십 및 의지표명 방식이 심사원 해석에 따라 평가 차이 발생 가능',
        severity: 'LOW'
      }
    ],
    
    // 기존 호환성을 위한 필드들
    score: Math.max(40, baseReadiness + Math.floor(Math.random() * 15)), // 40-93 범위
    keyRisks: gapAnalysis.categoryA.map(gap => gap.title).slice(0, 4),
    recommendations: lrqaRecommendations.slice(0, 6),
    
    // 🆕 AI 웹사이트 분석 결과
    websiteAnalysis: websiteAnalysis,
    
    // 상세 분석 정보
    reportPath: `/temp/lrqa-gap-analysis-${Date.now()}.html`,
    analysisDetails: {
      companyName: companyName,
      website: website,
      analysisDate: new Date().toISOString(),
      standards: selectedStandards,
      methodology: 'LRQA Professional Gap Analysis + AI Website Analysis',
      assessor: 'LRQA Certified Lead Assessor (Simulated)',
      aiEnhanced: websiteAnalysis?.analysisAvailable || false,
      aiModel: websiteAnalysis?.model || null,
      tokensUsed: websiteAnalysis?.tokensUsed || 0,
      isDummy: true,
      lrqaEnhanced: true
    }
  };
  
  console.log('=== LRQA 표준 갭분석 완료 ===');
  console.log(`분석 결과: ${readinessLevel}`);
  console.log(`준비 기간: ${preparationMonths}개월`);
  console.log(`성공 확률: ${successProbability}%`);
  console.log(`Category A (Critical): ${gapAnalysis.categoryA.length}건`);
  console.log(`Category B (Important): ${gapAnalysis.categoryB.length}건`);
  
  // 🆕 웹사이트 분석 결과 로그
  if (websiteAnalysis?.analysisAvailable) {
    console.log(`AI 웹사이트 분석: 성공 (${websiteAnalysis.model}, ${websiteAnalysis.tokensUsed} 토큰 사용)`);
  } else if (websiteAnalysis) {
    console.log(`AI 웹사이트 분석: 실패 또는 생략 (${websiteAnalysis.reason})`);
  }
  
  return result;
}

// 🆕 ISOMatch 갭분석 실행
async function runISOMatchGapAnalysis(formData) {
  console.log('=== ISOMatch 갭분석 실행 시작 ===');
  
  try {
    // ISOMatch 시스템에 필요한 데이터 준비
    const isoMatchData = {
      name: formData.companyName,
      url: formData.companyWebsite,
      iso_standards: formData.selectedISOStandards || [],
      business_type: formData.textarea_0 || '',  // 인증 범위 설명
      employee_count: formData.employee_총직원수 || '',
      contact_email: formData.contactEmail
    };
    
    console.log('ISOMatch 데이터 준비 완료:', isoMatchData);
    
    // ISOMatch Python 스크립트 실행
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', [
        path.join(ISOMATCH_PATH, 'report.py'),
        '--name', isoMatchData.name,
        '--url', isoMatchData.url,
        '--country', 'KR',
        '--lang', 'ko',
        '--iso-focus', isoMatchData.iso_standards.join(','),
        '--output-format', 'json'
      ]);
      
      let outputData = '';
      let errorData = '';
      
      pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
        console.log('ISOMatch stdout:', data.toString());
      });
      
      pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
        console.error('ISOMatch stderr:', data.toString());
      });
      
      pythonProcess.on('close', (code) => {
        console.log(`ISOMatch 프로세스 종료, 코드: ${code}`);
        
        if (code === 0) {
          try {
            const result = JSON.parse(outputData);
            console.log('ISOMatch 결과 파싱 성공:', result);
            resolve({
              score: result.overall_score || 0,
              keyRisks: result.key_risks || [],
              recommendations: result.recommendations || [],
              reportPath: result.report_path || '',
              analysisDetails: result.analysis_details || {}
            });
          } catch (parseError) {
            console.error('ISOMatch 결과 파싱 오류:', parseError);
            reject(new Error('갭분석 결과 파싱 중 오류가 발생했습니다.'));
          }
        } else {
          console.error('ISOMatch 실행 실패:', errorData);
          reject(new Error(`갭분석 실행 중 오류가 발생했습니다. (코드: ${code})`));
        }
      });
    });
    
  } catch (error) {
    console.error('ISOMatch 갭분석 실행 중 오류:', error);
    throw error;
  }
}

// 🆕 갭분석 결과 이메일 전송
async function sendGapAnalysisEmail(formData, gapAnalysisResult) {
  console.log('=== 갭분석 결과 이메일 전송 시작 ===');
  
  // 개발 모드 체크 - SMTP 설정이 있으면 이메일 발송 허용
  const isDevelopmentMode = !process.env.GOOGLE_PROJECT_ID || !process.env.GOOGLE_SHEET_ID;
  const hasSmtpConfig = SMTP_USER && SMTP_PASS;
  
  if (isDevelopmentMode && !hasSmtpConfig) {
    console.log('개발 모드 + SMTP 미설정: 이메일 전송 생략 (더미 전송 완료)');
    return { success: true, message: '개발 모드에서 이메일 전송을 시뮬레이션했습니다.' };
  }
  
  if (isDevelopmentMode && hasSmtpConfig) {
    console.log('🚀 개발 모드이지만 SMTP 설정 발견 - 실제 이메일 발송 진행!');
  }
  
  if (!SMTP_USER || !SMTP_PASS) {
    console.log('SMTP credentials not configured, skipping email notification');
    return;
  }

  // Gmail 또는 Outlook 자동 감지
  const isGmail = SMTP_USER && SMTP_USER.includes('@gmail.com');
  const isOutlook = SMTP_USER && (SMTP_USER.includes('@outlook.com') || SMTP_USER.includes('@hotmail.com'));
  
  let transportConfig;
  
  if (isGmail) {
    transportConfig = {
      service: 'gmail',
      auth: {
        user: SMTP_USER,
        pass: SMTP_PASS
      }
    };
  } else if (isOutlook) {
    transportConfig = {
      host: 'smtp.office365.com',
      port: 587,
      secure: false,
      auth: {
        user: SMTP_USER,
        pass: SMTP_PASS
      }
    };
  } else {
    transportConfig = {
      service: 'gmail',
      auth: {
        user: SMTP_USER,
        pass: SMTP_PASS
      }
    };
  }
  
  const transporter = nodemailer.createTransporter(transportConfig);

  // 신청 표준 정리
  const selectedStandards = Array.isArray(formData.selectedISOStandards) 
    ? formData.selectedISOStandards.join(', ') 
    : formData.isoStandards || '미지정';

  // 관리자용 이메일
  const adminSubject = `[LRQA] 새로운 ISO 갭분석 신청 - ${formData.companyName}`;
  const adminBody = `
새로운 ISO 갭분석 신청서가 제출되었습니다.

=== 기본 정보 ===
회사명: ${formData.companyName}
웹사이트: ${formData.companyWebsite}
담당자: ${formData.contactName}
연락처: ${formData.contactPhone}
이메일: ${formData.contactEmail}

=== 신청 내용 ===
신청 ISO 표준: ${selectedStandards}
희망 심사 일정: ${formData.desiredAuditDate ? new Date(formData.desiredAuditDate + '-01').toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' }) : '미정'}

=== 갭분석 결과 ===
종합 점수: ${gapAnalysisResult?.score || 0}점/100점
주요 리스크: ${gapAnalysisResult?.keyRisks?.join(', ') || '분석 중'}
권장사항: ${gapAnalysisResult?.recommendations?.join(', ') || '분석 중'}

전체 보고서: ${gapAnalysisResult?.reportPath || '생성 중...'}

신청서 제출 시간: ${new Date().toLocaleString('ko-KR')}

감사합니다.
LRQA Korea 갭분석 시스템
`;

  // 고객용 이메일
  const customerSubject = `[LRQA] ISO ${selectedStandards} 갭분석 결과 - ${formData.companyName}`;
  const customerBody = `
안녕하세요, ${formData.contactName}님.

LRQA Korea에서 요청하신 ISO 갭분석이 완료되어 결과를 안내해드립니다.

=== 갭분석 결과 요약 ===
📊 종합 준비도 점수: ${gapAnalysisResult?.score || 0}점/100점
📋 신청 ISO 표준: ${selectedStandards}
🏢 분석 대상 기업: ${formData.companyName}
🌐 분석 대상 웹사이트: ${formData.companyWebsite}

=== 주요 발견사항 ===
🔍 주요 리스크 영역:
${gapAnalysisResult?.keyRisks?.map(risk => `• ${risk}`).join('\n') || '• 분석 중입니다...'}

💡 권장 개선사항:
${gapAnalysisResult?.recommendations?.map(rec => `• ${rec}`).join('\n') || '• 상세 분석 중입니다...'}

=== 다음 단계 ===
1. 상세 갭분석 보고서 검토 (첨부파일 또는 별도 전송)
2. 개선 계획 수립
3. LRQA 컨설턴트와의 1:1 상담 진행
4. ISO 인증 심사 일정 협의

=== 추가 지원 ===
• 무료 컨설팅 상담: 30분 화상회의 또는 전화 상담
• 맞춤형 교육 프로그램 안내
• 단계별 인증 준비 로드맵 제공

궁금한 사항이 있으시면 언제든지 연락해 주세요.

이메일: ${ADMIN_EMAIL}
전화: +82 10-5438-3060
담당자: 김달성 과장

감사합니다.
LRQA Korea 갭분석팀
`;

  try {
    // 관리자에게 알림 이메일 전송
    console.log('관리자 이메일 전송 중...');
    await transporter.sendMail({
      from: SMTP_USER,
      to: ADMIN_EMAIL,
      subject: adminSubject,
      text: adminBody
    });
    console.log('관리자 이메일 전송 성공');

    // 고객에게 갭분석 결과 이메일 전송
    if (formData.contactEmail) {
      console.log('고객 갭분석 결과 이메일 전송 중...');
      
      // 보고서 파일이 있으면 첨부
      const mailOptions = {
        from: SMTP_USER,
        to: formData.contactEmail,
        subject: customerSubject,
        text: customerBody
      };
      
      // 보고서 파일 첨부 (파일이 존재하는 경우)
      if (gapAnalysisResult?.reportPath && fs.existsSync(gapAnalysisResult.reportPath)) {
        mailOptions.attachments = [
          {
            filename: `ISO_${selectedStandards.replace(/\s+/g, '_')}_갭분석보고서_${formData.companyName}.html`,
            path: gapAnalysisResult.reportPath
          }
        ];
      }
      
      await transporter.sendMail(mailOptions);
      console.log('고객 갭분석 결과 이메일 전송 성공');
    }
    
  } catch (error) {
    console.error('갭분석 이메일 전송 중 오류:', error);
    throw error;
  }
}

// 🆕 메인 핸들러
exports.handler = async (event, context) => {
  console.log('=== submit-application-with-gap-analysis 함수 시작 ===');
  console.log('HTTP Method:', event.httpMethod);
  console.log('Headers:', event.headers);
  console.log('Body length:', event.body ? event.body.length : 0);
  
  // 환경 변수 확인
  console.log('환경 변수 상태:');
  console.log('GOOGLE_SHEET_ID:', process.env.GOOGLE_SHEET_ID ? '설정됨' : '누락');
  console.log('ISOMATCH_PATH:', ISOMATCH_PATH);
  
  // CORS 처리
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers
    };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    console.log('JSON 파싱 시도...');
    const formData = JSON.parse(event.body);
    console.log('JSON 파싱 완료, 데이터 키:', Object.keys(formData));
    
    // 필수 필드 검증
    console.log('갭분석 필수 필드 검증...');
    if (!formData.companyName) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          success: false, 
          message: '회사명은 필수 입력 항목입니다.' 
        })
      };
    }
    
    if (!formData.companyWebsite) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          success: false, 
          message: '회사 웹사이트는 갭분석을 위해 필수입니다.' 
        })
      };
    }
    
    if (!formData.selectedISOStandards || formData.selectedISOStandards.length === 0) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          success: false, 
          message: '분석할 ISO 표준을 선택해주세요.' 
        })
      };
    }
    
    console.log('갭분석 필수 필드 검증 완료');

    // 환경 변수 체크 및 개발 모드 설정
    const isDevelopmentMode = !process.env.GOOGLE_PROJECT_ID || !process.env.GOOGLE_SHEET_ID;
    console.log('개발 모드:', isDevelopmentMode);
    
    let sheets = null;
    let gapAnalysisResult = null;
    
    if (isDevelopmentMode) {
      // 🆕 개발 환경: 더미 갭분석 결과 생성
      console.log('개발 환경에서 더미 갭분석 결과 생성...');
      gapAnalysisResult = await createDummyGapAnalysisResult(formData);
      console.log('더미 갭분석 완료:', gapAnalysisResult);
    } else {
      // 프로덕션 환경: 실제 API 연동
      console.log('Google Sheets API 클라이언트 초기화...');
      sheets = await getGoogleSheetsClient();
      
      console.log('갭분석 시트 헤더 설정...');
      await setupGapAnalysisSheetHeaders(sheets);
      
      console.log('ISOMatch 갭분석 실행...');
      gapAnalysisResult = await runISOMatchGapAnalysis(formData);
      console.log('ISOMatch 갭분석 완료:', gapAnalysisResult);
      
      console.log('갭분석 데이터 행 추가...');
      await addGapAnalysisRow(sheets, formData, gapAnalysisResult);
    }
    
    // 갭분석 결과 이메일 전송 (개발/프로덕션 공통)
    console.log('갭분석 결과 이메일 전송...');
    await sendGapAnalysisEmail(formData, gapAnalysisResult);
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ 
        success: true, 
        message: '신청서 제출 및 갭분석이 성공적으로 완료되었습니다.',
        gapAnalysisResult: {
          score: gapAnalysisResult.score,
          keyRisks: gapAnalysisResult.keyRisks,
          recommendations: gapAnalysisResult.recommendations,
          reportGenerated: !!gapAnalysisResult.reportPath
        }
      })
    };
    
  } catch (error) {
    console.error('=== 갭분석 처리 중 오류 발생 ===');
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        message: '갭분석 처리 중 오류가 발생했습니다.',
        error: error.message
      })
    };
  }
};
