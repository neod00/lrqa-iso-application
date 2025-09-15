const { google } = require('googleapis');

// Google Sheets 설정
const SHEET_ID = process.env.GOOGLE_SHEET_ID;
const SHEET_NAME = 'ISO_Applications';

// CORS 헤더 설정
const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'text/csv; charset=utf-8'
};

// Google Sheets API 클라이언트 초기화
async function getGoogleSheetsClient() {
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

    const sheets = google.sheets({ version: 'v4', auth });
    return sheets;
}

// 신청서 데이터 가져오기
async function getApplications() {
    const sheets = await getGoogleSheetsClient();
    
    try {
        const response = await sheets.spreadsheets.values.get({
            spreadsheetId: SHEET_ID,
            range: `${SHEET_NAME}!A:Z`
        });

        const rows = response.data.values || [];
        if (rows.length === 0) {
            return [];
        }

        // 첫 번째 행은 헤더이므로 제외
        const headers = rows[0];
        const data = rows.slice(1);

        const applications = data.map(row => {
            const obj = {};
            headers.forEach((header, index) => {
                obj[header] = row[index] || '';
            });
            return obj;
        });

        // 신청일시 기준으로 최신순 정렬
        applications.sort((a, b) => {
            const dateA = new Date(a['신청일시'] || 0);
            const dateB = new Date(b['신청일시'] || 0);
            return dateB - dateA; // 최신순 (내림차순)
        });

        return applications;
    } catch (error) {
        console.error('Error fetching applications:', error);
        throw error;
    }
}

exports.handler = async (event, context) => {
    // OPTIONS 요청 처리
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    if (event.httpMethod !== 'GET') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ error: 'Method not allowed' })
        };
    }

    try {
        // 신청서 데이터 가져오기
        const applications = await getApplications();

        if (applications.length === 0) {
            return {
                statusCode: 200,
                headers: {
                    ...headers,
                    'Content-Disposition': 'attachment; filename="lrqa_applications.csv"'
                },
                body: '신청일시,법인명(국문),법인명(영문),담당자명,담당자전화,담당자이메일,인증범위,상태\n'
            };
        }

        // CSV 헤더 정의
        const headers_csv = [
            '신청일시',
            '법인명(국문)',
            '법인명(영문)',
            '담당자명',
            '담당자전화',
            '담당자이메일',
            '인증범위',
            '상태'
        ];

        // CSV 데이터 생성
        let csvContent = headers_csv.join(',') + '\n';
        
        applications.forEach(app => {
            const row = [
                `"${(app['신청일시'] || '').replace(/"/g, '""')}"`,
                `"${(app['법인명(국문)'] || '').replace(/"/g, '""')}"`,
                `"${(app['법인명(영문)'] || '').replace(/"/g, '""')}"`,
                `"${(app['담당자명'] || '').replace(/"/g, '""')}"`,
                `"${(app['담당자전화'] || '').replace(/"/g, '""')}"`,
                `"${(app['담당자이메일'] || '').replace(/"/g, '""')}"`,
                `"${(app['인증범위'] || '').replace(/"/g, '""')}"`,
                `"${(app['상태'] || '신규').replace(/"/g, '""')}"`
            ];
            csvContent += row.join(',') + '\n';
        });

        // BOM 추가 (한글 깨짐 방지)
        const bom = '\uFEFF';
        const csvWithBom = bom + csvContent;

        return {
            statusCode: 200,
            headers: {
                ...headers,
                'Content-Disposition': 'attachment; filename="lrqa_applications.csv"'
            },
            body: csvWithBom
        };

    } catch (error) {
        console.error('CSV export error:', error);
        return {
            statusCode: 500,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                success: false, 
                message: 'CSV 내보내기 중 오류가 발생했습니다.',
                error: error.message 
            })
        };
    }
};
