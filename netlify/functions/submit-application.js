const { google } = require('googleapis');
const nodemailer = require('nodemailer');

// Google Sheets 설정
const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SHEET_NAME = 'ISO_Applications';

// 초기화 시 환경 변수 확인
if (!SHEET_ID) {
  console.error('GOOGLE_SHEET_ID 환경 변수가 설정되지 않았습니다.');
}

// 이메일 설정
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'dal.kim@lrqa.com';
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;

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
  
  // 환경 변수 확인
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

// 시트 헤더 설정
async function setupSheetHeaders(sheets) {
  console.log('=== 시트 헤더 설정 시작 ===');
  
  if (!SHEET_ID) {
    throw new Error('GOOGLE_SHEET_ID가 설정되지 않았습니다.');
  }
  
  console.log('SHEET_ID:', SHEET_ID);
  console.log('SHEET_NAME:', SHEET_NAME);
  
  const headers = [
    // 기본 정보
    '신청일시', '상태',
    // 회사 정보
    '법인명(국문)', '법인명(영문)', '상호명', '본사주소', '도시', '우편번호',
    '대표전화번호', '행정구역', '국가', '대표이메일', '웹사이트',
    '법인등록번호', '사업자등록번호', '과세당국', '모회사/계열사여부',
    '중앙관리시스템여부', '인증포함사업장수', '사업장목록', 'ISO표준',
    '표준적용여부',
    // 연락처 정보
    '담당자명', '부서', '담당자이메일', '담당자전화', '휴대폰번호',
    '컨설턴트명', '컨설팅기관', 'LRQA인지경로', '향후이벤트정보수신',
    // 평가 요구사항
    '인증범위', '다중표준시스템', '희망심사일정', '기타표준',
    // 인증 범위 확인
    '활동내용기재', '규제기관승인여부', '법적의무미해결문제', '기존인증보유여부',
    '기존표준', '기존인증기관', '인증만료일',
    // 직원 현황
    '빈열', '총직원수', '정규직수', '비정규직수', '하청업체직원수', '임시직수',
    '다중사업장직원현황', '외주프로세스여부', '반복작업그룹여부',
    '작업성격설명', '시간외승인활동여부', '계절변동설명',
    // 교대 근무
    '교대근무횟수', '교대근무시간', '교대총직원수', '교대조1', '교대조2',
    '교대조3', '교대조4', '임시사업장여부', '고객사위치서비스',
    // 인증 변경
    '기존인증LRQA이전요청', '공식인정인증여부', '인증기관이전사유',
    '미해결부적합문서', 'LRQA인증기관연락동의', 'LRQA마지막방문일자',
    '첨부문서',
    // ISO 추가 정보
    'ISO14001사업분야', 'ISO14001환경위험', 'ISO45001사업분야', 'ISO45001유해위험',
    // 추가 정보
    '원격심사여부', '예비심사견적수신', '교육과정정보수신', '추가참고정보',
    // 데이터 처리 동의
    '데이터처리동의', '서명', '서명날짜', '마케팅동의'
  ];

  try {
    // 시트의 첫 번째 행 확인
    console.log('시트 첫 번째 행 확인 중...');
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A1:Z1`
    });
    console.log('시트 첫 번째 행 확인 완료');

    // 헤더가 없거나 비어있으면 헤더 추가
    if (!response.data.values || response.data.values.length === 0) {
      console.log('헤더가 없음, 헤더 추가 중...');
      await sheets.spreadsheets.values.update({
        spreadsheetId: SHEET_ID,
        range: `${SHEET_NAME}!A1`,
        valueInputOption: 'RAW',
        resource: {
          values: [headers]
        }
      });
      console.log('헤더 추가 완료');

      // 헤더 스타일 적용
      console.log('헤더 스타일 적용 중...');
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
                      red: 0.26,
                      green: 0.52,
                      blue: 0.96
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
    console.error('=== 헤더 설정 중 오류 발생 ===');
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    throw error;
  }
}

// 데이터 행 추가
async function addApplicationRow(sheets, formData) {
  console.log('=== 데이터 행 추가 시작 ===');
  
  if (!SHEET_ID) {
    throw new Error('GOOGLE_SHEET_ID가 설정되지 않았습니다.');
  }
  
  console.log('데이터 추가 대상 시트:', SHEET_ID);
  console.log('받은 폼 데이터 키:', Object.keys(formData));
  
  const timestamp = new Date().toISOString();
  console.log('타임스탬프:', timestamp);
  
  const rowData = [
    // 기본 정보
    timestamp,
    '신규',
    // 회사 정보
    formData.companyNameKo || '',
    formData.companyNameEn || '',
    formData.tradeName || '',
    formData.headOfficeAddress || '',
    formData.city || '',
    formData.postalCode || '',
    formData.mainPhone || '',
    formData.province || '',
    formData.country || '',
    formData.mainEmail || '',
    formData.website || '',
    formData.corporateRegNumber || '',
    formData.businessRegNumber || '',
    formData.taxAuthority || '',
    formData.groupAffiliation || '',
    formData.centralSystem || '',
    formData.siteCount || '',
    formData.siteList || '',
    formData.isoStandards || '',
    formData.standardApplied || '',
    // 연락처 정보
    formData.contactName || '',
    formData.department || '',
    formData.contactEmail || '',
    formData.contactPhone || '',
    formData.mobilePhone || '',
    formData.consultantName || '',
    formData.consultingOrg || '',
    formData.howKnowLrqa || '',
    formData.futureEvents || '',
    // 평가 요구사항
    formData.certificationScope || '',
    formData.multiStandardSystem || '',
    formData.desiredAuditDate || '',
    formData.otherStandards || '',
    // 인증 범위 확인
    formData.activityDescription || '',
    formData.regulatoryApproval || '',
    formData.legalIssues || '',
    formData.existingCertification || '',
    formData.existingStandard || '',
    formData.existingCertBody || '',
    formData.certExpiryDate || '',
    // 직원 현황
    '', // 빈 열 추가 (데이터 정렬을 위해)
    formData.totalEmployees || '',
    formData.permanentEmployees || '',
    formData.temporaryEmployees || '',
    formData.contractorEmployees || '',
    formData.casualEmployees || '',
    formData.multiSiteEmployees || '',
    formData.outsourcing || '',
    formData.repeatGroup || '',
    formData.workDescription || '',
    formData.overtimeActivities || '',
    formData.seasonalVariation || '',
    // 교대 근무
    formData.shiftCount || '',
    formData.shiftHours || '',
    formData.shiftTotalEmployees || '',
    formData.shift1 || '',
    formData.shift2 || '',
    formData.shift3 || '',
    formData.shift4 || '',
    formData.temporarySite || '',
    formData.customerLocationService || '',
    // 인증 변경
    formData.transferToLrqa || '',
    formData.officialAccreditation || '',
    formData.transferReason || '',
    formData.attachedDocuments || '',
    formData.lrqaContactConsent || '',
    formData.lastLrqaVisit || '',
    formData.attachmentNote || '',
    // ISO 추가 정보
    formData.iso14001Business || '',
    formData.iso14001Risks || '',
    formData.iso45001Business || '',
    formData.iso45001Hazards || '',
    // 추가 정보
    formData.remoteAudit || '',
    formData.preAuditQuote || '',
    formData.trainingInfo || '',
    formData.additionalInfo || '',
    // 데이터 처리 동의
    formData.dataProcessConsent || '',
    formData.signature || '',
    formData.signatureDate || '',
    formData.marketingConsent || ''
  ];

  console.log('Google Sheets API 호출 시도...');
  console.log('Row data length:', rowData.length);
  
  try {
    await sheets.spreadsheets.values.append({
      spreadsheetId: SHEET_ID,
      range: `${SHEET_NAME}!A:Z`,
      valueInputOption: 'RAW',
      resource: {
        values: [rowData]
      }
    });
    console.log('Google Sheets API 호출 성공');
  } catch (error) {
    console.error('Google Sheets API 호출 중 오류:', error);
    throw error;
  }
}

// 이메일 전송
async function sendNotificationEmail(formData) {
  console.log('Email function called with:', {
    SMTP_USER: SMTP_USER ? 'Set' : 'Not set',
    SMTP_PASS: SMTP_PASS ? 'Set' : 'Not set',
    ADMIN_EMAIL: ADMIN_EMAIL
  });
  
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
    // 기본 Gmail 설정
    transportConfig = {
      service: 'gmail',
      auth: {
        user: SMTP_USER,
        pass: SMTP_PASS
      }
    };
  }
  
  const transporter = nodemailer.createTransport(transportConfig);

  // 신청 규격 파악
  const getCertificationStandards = (isoStandards) => {
    if (!isoStandards) return '';
    
    const standards = [];
    const standardsMap = {
      'iso9001': 'ISO 9001 - 품질',
      'iso14001': 'ISO 14001 - 환경', 
      'iso45001': 'ISO 45001 - 안전보건'
    };
    
    if (typeof isoStandards === 'string') {
      // 쉼표로 구분된 문자열인 경우
      const standardArray = isoStandards.split(',').map(s => s.trim());
      standardArray.forEach(standard => {
        if (standardsMap[standard]) {
          standards.push(standardsMap[standard]);
        }
      });
    } else if (Array.isArray(isoStandards)) {
      // 배열인 경우
      isoStandards.forEach(standard => {
        if (standardsMap[standard]) {
          standards.push(standardsMap[standard]);
        }
      });
    }
    
    return standards.join(', ');
  };

  const certificationStandards = getCertificationStandards(formData.isoStandards);
  const subject = `[LRQA] 새로운 ${certificationStandards || 'ISO'} 인증심사 신청서 - ${formData.companyNameKo || formData.companyNameEn}`;
  
  // 현재 시간을 타임스탬프로 사용
  const timestamp = new Date().toISOString();
  
  // 현재 도메인을 동적으로 가져오기
  const getCurrentDomain = () => {
    // Netlify 환경에서 제공하는 URL 정보 사용
    const netlifyUrl = process.env.URL || process.env.DEPLOY_URL;
    if (netlifyUrl) {
      return netlifyUrl.replace('https://', '').replace('http://', '');
    }
    return 'your-domain.netlify.app';
  };

  const currentDomain = getCurrentDomain();
  const adminUrl = `https://${currentDomain}/admin.html`;
  
  const adminBody = `
새로운 ISO 인증심사 신청서가 제출되었습니다.

회사명: ${formData.companyNameKo || formData.companyNameEn}
담당자: ${formData.contactName}
연락처: ${formData.contactPhone}
이메일: ${formData.contactEmail}
신청규격: ${certificationStandards || '미지정'}
인증범위: ${formData.certificationScope}
총 직원수: ${formData.totalEmployees}명
희망 심사 일정: ${formData.desiredAuditDate ? new Date(formData.desiredAuditDate + '-01').toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' }) : '미정'}

전체 내용은 관리자 페이지에서 확인하실 수 있습니다.
관리자 페이지: ${adminUrl}

신청서 제출 시간: ${new Date().toLocaleString('ko-KR')}

감사합니다.
LRQA Korea 자동 시스템
`;

  const confirmSubject = `[LRQA] 인증심사 신청서 접수 확인`;
  const confirmBody = `
안녕하세요, ${formData.contactName}님.

LRQA Korea에서 인증심사 신청서 접수를 확인해드립니다.

신청하신 내용:
- 회사명: ${formData.companyNameKo || formData.companyNameEn}
- 인증범위: ${formData.certificationScope}
- 희망 심사 일정: ${formData.desiredAuditDate ? new Date(formData.desiredAuditDate + '-01').toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' }) : '미정'}

담당자가 검토 후 빠른 시일 내에 연락드리겠습니다.

문의사항이 있으시면 언제든지 연락해 주세요.
이메일: ${ADMIN_EMAIL}
전화: +82 10-5438-3060

감사합니다.
LRQA Korea 팀
`;

  try {
    console.log('Attempting to send admin email to:', ADMIN_EMAIL);
    
    // 관리자에게 알림 이메일 전송
    await transporter.sendMail({
      from: SMTP_USER,
      to: ADMIN_EMAIL,
      subject: subject,
      text: adminBody
    });
    
    console.log('Admin email sent successfully');

    // 신청자에게 확인 이메일 전송
    if (formData.contactEmail) {
      console.log('Attempting to send confirmation email to:', formData.contactEmail);
      await transporter.sendMail({
        from: SMTP_USER,
        to: formData.contactEmail,
        subject: confirmSubject,
        text: confirmBody
      });
      console.log('Confirmation email sent successfully');
    }
  } catch (error) {
    console.error('Error sending email:', error);
    console.error('Error details:', error.message);
    console.error('Error stack:', error.stack);
  }
}

// 메인 핸들러
exports.handler = async (event, context) => {
  console.log('=== submit-application 함수 시작 ===');
  console.log('HTTP Method:', event.httpMethod);
  console.log('Headers:', event.headers);
  console.log('Body length:', event.body ? event.body.length : 0);
  
  // 환경 변수 확인
  console.log('환경 변수 상태:');
  console.log('GOOGLE_SHEET_ID:', process.env.GOOGLE_SHEET_ID ? '설정됨' : '누락');
  console.log('GOOGLE_PROJECT_ID:', process.env.GOOGLE_PROJECT_ID ? '설정됨' : '누락');
  console.log('GOOGLE_CLIENT_EMAIL:', process.env.GOOGLE_CLIENT_EMAIL ? '설정됨' : '누락');
  console.log('GOOGLE_PRIVATE_KEY:', process.env.GOOGLE_PRIVATE_KEY ? '설정됨' : '누락');
  
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
    console.log('필수 필드 검증 시도...');
    console.log('companyNameKo:', formData.companyNameKo);
    console.log('companyNameEn:', formData.companyNameEn);
    console.log('companyName:', formData.companyName);
    
    // companyName 필드가 있으면 companyNameKo로 매핑
    if (formData.companyName && !formData.companyNameKo) {
      formData.companyNameKo = formData.companyName;
      console.log('companyName을 companyNameKo로 매핑:', formData.companyNameKo);
    }
    
    if (!formData.companyNameKo && !formData.companyNameEn && !formData.companyName) {
      console.log('필수 필드 검증 실패 - 회사명 없음');
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ 
          success: false, 
          message: '회사명은 필수 입력 항목입니다.' 
        })
      };
    }
    console.log('필수 필드 검증 완료');

    // Google Sheets API 클라이언트 초기화
    console.log('Google Sheets API 클라이언트 초기화 시도...');
    const sheets = await getGoogleSheetsClient();
    console.log('Google Sheets API 클라이언트 초기화 완료');
    
    // 시트 헤더 설정
    console.log('시트 헤더 설정 시도...');
    await setupSheetHeaders(sheets);
    console.log('시트 헤더 설정 완료');
    
    // 데이터 행 추가
    console.log('데이터 행 추가 시도...');
    await addApplicationRow(sheets, formData);
    console.log('데이터 행 추가 완료');
    
    // 이메일 알림 전송
    console.log('이메일 알림 전송 시도...');
    await sendNotificationEmail(formData);
    console.log('이메일 알림 전송 완료');
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ 
        success: true, 
        message: '신청서가 성공적으로 제출되었습니다.' 
      })
    };
    
  } catch (error) {
    console.error('=== 오류 발생 ===');
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    console.error('Error name:', error.name);
    console.error('전체 오류 객체:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        success: false, 
        message: '신청서 처리 중 오류가 발생했습니다.',
        error: error.message,
        stack: error.stack
      })
    };
  }
}; 