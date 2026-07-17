const { getEmailSettings, saveEmailSettings } = require('./email-settings-store');

const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Content-Type': 'application/json; charset=utf-8'
};

function response(statusCode, body) {
  return { statusCode, headers, body: JSON.stringify(body) };
}

function isAuthorized(username, password) {
  const expectedUser = process.env.ADMIN_USERNAME || 'admin';
  const expectedPassword = process.env.ADMIN_PASSWORD || 'lrqa2025';
  return username === expectedUser && password === expectedPassword;
}

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return { statusCode: 204, headers };
  if (event.httpMethod !== 'POST') return response(405, { success: false, message: 'Method not allowed' });

  try {
    const payload = JSON.parse(event.body || '{}');
    if (!isAuthorized(payload.username, payload.password)) {
      return response(401, { success: false, message: '관리자 인증에 실패했습니다.' });
    }

    if (payload.action === 'verify') {
      return response(200, {
        success: true,
        smtpConfigured: Boolean(process.env.SMTP_USER && process.env.SMTP_PASS)
      });
    }

    if (payload.action === 'get') {
      const settings = await getEmailSettings();
      return response(200, {
        success: true,
        settings,
        smtpConfigured: Boolean(process.env.SMTP_USER && process.env.SMTP_PASS)
      });
    }

    if (payload.action === 'save') {
      const settings = await saveEmailSettings(payload.settings || {});
      return response(200, {
        success: true,
        settings,
        smtpConfigured: Boolean(process.env.SMTP_USER && process.env.SMTP_PASS)
      });
    }

    return response(400, { success: false, message: '지원하지 않는 작업입니다.' });
  } catch (error) {
    console.error('Email settings error:', error);
    return response(500, { success: false, message: error.message || '메일 설정 처리 중 오류가 발생했습니다.' });
  }
};