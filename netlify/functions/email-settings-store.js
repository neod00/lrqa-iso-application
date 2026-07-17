const { google } = require('googleapis');

const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SETTINGS_SHEET = 'ISO_Email_Settings';

const DEFAULT_APPLICANT_SUBJECT = '[LRQA] 인증 심사 신청이 접수되었습니다 - {{회사명}}';
const DEFAULT_APPLICANT_BODY = `안녕하세요, {{담당자명}}님.

LRQA 인증 심사 신청서를 제출해 주셔서 감사합니다.
아래와 같이 신청서가 정상적으로 접수되었습니다.

[신청 내용]
회사명: {{회사명}}
신청 표준: {{신청표준}}
인증 범위: {{인증범위}}
희망 심사 일정: {{희망심사일정}}
사업장 수: {{사업장수}}
총 직원 수: {{총직원수}}
접수 일시: {{접수일시}}

LRQA 담당자가 신청 내용을 검토한 후 빠른 시일 내에
견적 및 다음 절차를 안내해 드리겠습니다.

추가 문의사항은 아래 이메일로 연락해 주세요.
{{문의이메일}}

감사합니다.

LRQA Korea
로이드인증원`;

const DEFAULT_SETTINGS = {
  recipientEmail: process.env.ADMIN_EMAIL || 'dal.kim@lrqa.com',
  applicantSubject: DEFAULT_APPLICANT_SUBJECT,
  applicantBody: DEFAULT_APPLICANT_BODY
};

function createGoogleAuth() {
  if (!SHEET_ID || !process.env.GOOGLE_CLIENT_EMAIL || !process.env.GOOGLE_PRIVATE_KEY) {
    throw new Error('Google Sheets environment variables are not configured.');
  }

  return new google.auth.GoogleAuth({
    credentials: {
      type: 'service_account',
      project_id: process.env.GOOGLE_PROJECT_ID,
      private_key_id: process.env.GOOGLE_PRIVATE_KEY_ID,
      private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
      client_email: process.env.GOOGLE_CLIENT_EMAIL,
      client_id: process.env.GOOGLE_CLIENT_ID,
      auth_uri: 'https://accounts.google.com/o/oauth2/auth',
      token_uri: 'https://oauth2.googleapis.com/token',
      auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs'
    },
    scopes: ['https://www.googleapis.com/auth/spreadsheets']
  });
}

async function getSheetsClient() {
  const auth = createGoogleAuth();
  await auth.getClient();
  return google.sheets({ version: 'v4', auth });
}

async function ensureSettingsSheet(sheets) {
  const metadata = await sheets.spreadsheets.get({
    spreadsheetId: SHEET_ID,
    fields: 'sheets.properties.title'
  });

  const exists = (metadata.data.sheets || []).some(
    (sheet) => sheet.properties && sheet.properties.title === SETTINGS_SHEET
  );
  if (exists) return;

  try {
    await sheets.spreadsheets.batchUpdate({
      spreadsheetId: SHEET_ID,
      resource: {
        requests: [{ addSheet: { properties: { title: SETTINGS_SHEET } } }]
      }
    });
  } catch (error) {
    if (!String(error.message || '').includes('already exists')) throw error;
  }
}

async function getEmailSettings() {
  try {
    const sheets = await getSheetsClient();
    await ensureSettingsSheet(sheets);
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SHEET_ID,
      range: `${SETTINGS_SHEET}!A:B`
    });

    const saved = Object.fromEntries(
      (response.data.values || []).filter((row) => row[0]).map((row) => [row[0], row[1] || ''])
    );

    return {
      recipientEmail: saved.recipientEmail || DEFAULT_SETTINGS.recipientEmail,
      applicantSubject: saved.applicantSubject || DEFAULT_SETTINGS.applicantSubject,
      applicantBody: saved.applicantBody || DEFAULT_SETTINGS.applicantBody
    };
  } catch (error) {
    console.error('Unable to read email settings; using defaults:', error.message);
    return { ...DEFAULT_SETTINGS };
  }
}

async function saveEmailSettings(settings) {
  const values = {
    recipientEmail: String(settings.recipientEmail || '').trim(),
    applicantSubject: String(settings.applicantSubject || '').trim(),
    applicantBody: String(settings.applicantBody || '').trim()
  };

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.recipientEmail)) {
    throw new Error('A valid notification recipient email is required.');
  }
  if (!values.applicantSubject || !values.applicantBody) {
    throw new Error('Applicant email subject and body are required.');
  }

  const sheets = await getSheetsClient();
  await ensureSettingsSheet(sheets);
  await sheets.spreadsheets.values.update({
    spreadsheetId: SHEET_ID,
    range: `${SETTINGS_SHEET}!A1:B3`,
    valueInputOption: 'RAW',
    resource: {
      values: [
        ['recipientEmail', values.recipientEmail],
        ['applicantSubject', values.applicantSubject],
        ['applicantBody', values.applicantBody]
      ]
    }
  });

  return values;
}

module.exports = {
  DEFAULT_SETTINGS,
  getEmailSettings,
  saveEmailSettings
};