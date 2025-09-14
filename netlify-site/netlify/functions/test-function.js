const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE'
};

exports.handler = async (event, context) => {
  // CORS 처리
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers
    };
  }

  const getCurrentDomain = () => {
    const netlifyUrl = process.env.URL || process.env.DEPLOY_URL;
    if (netlifyUrl) {
      return netlifyUrl.replace('https://', '').replace('http://', '');
    }
    return 'your-domain.netlify.app';
  };

  const currentDomain = getCurrentDomain();
  const adminUrl = `https://${currentDomain}/admin.html`;

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({
      success: true,
      data: {
        currentDomain,
        adminUrl,
        environment: {
          URL: process.env.URL,
          DEPLOY_URL: process.env.DEPLOY_URL,
          SITE_URL: process.env.SITE_URL
        }
      }
    })
  };
}; 