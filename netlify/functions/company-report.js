const fetch = require('node-fetch');

exports.handler = async (event, context) => {
    // CORS 헤더 설정
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    };

    // OPTIONS 요청 처리 (CORS preflight)
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    try {
        // POST 요청만 처리
        if (event.httpMethod !== 'POST') {
            return {
                statusCode: 405,
                headers,
                body: JSON.stringify({ error: 'Method not allowed' })
            };
        }

        const { companyName } = JSON.parse(event.body);
        
        if (!companyName) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'Company name is required' })
            };
        }

        // 환경변수 디버깅 로그
        console.log('Environment variables check:', {
            OPENAI_API_KEY: process.env.OPENAI_API_KEY ? 'Set (length: ' + process.env.OPENAI_API_KEY.length + ')' : 'Not set',
            NODE_ENV: process.env.NODE_ENV,
            allEnvKeys: Object.keys(process.env).filter(key => key.includes('OPENAI') || key.includes('CHATGPT'))
        });

        // 환경변수에서 API 키 가져오기
        const apiKey = process.env.OPENAI_API_KEY;
        
        if (!apiKey) {
            console.error('OpenAI API key not found in environment variables');
            return {
                statusCode: 500,
                headers,
                body: JSON.stringify({ 
                    error: 'OpenAI API key not configured',
                    debug: {
                        availableKeys: Object.keys(process.env).filter(key => key.includes('OPENAI') || key.includes('CHATGPT')),
                        nodeEnv: process.env.NODE_ENV
                    }
                })
            };
        }

        // ChatGPT API 호출을 위한 프롬프트 구성
        const prompt = `
다음 회사에 대한 종합적인 보고서를 작성해주세요:

회사명: ${companyName}

다음 항목들을 포함하여 HTML 형태로 보고서를 작성해주세요:

1. 회사 개요
   - 회사 소개
   - 주요 사업 분야
   - 설립년도 (알 수 있는 경우)

2. ISO 인증 현황
   - 보유한 ISO 인증 종류
   - 인증 취득 년도
   - 인증 기관
   - 인증 범위

3. 최근 경영 현황
   - 최근 뉴스 및 공시사항
   - 사업 확장 또는 변화
   - 주요 성과나 이슈

4. 시장에서의 위치
   - 업계 내 지위
   - 경쟁사 대비 특징
   - 주요 강점

5. 향후 전망
   - 성장 가능성
   - 주목할 만한 사항

보고서는 한국어로 작성하고, HTML 태그를 사용하여 구조화해주세요. 
각 섹션은 적절한 제목과 내용으로 구성해주세요.
정보가 부족한 경우 "정보 없음" 또는 "확인 필요"로 표시해주세요.
`;

        // ChatGPT API 호출
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'gpt-4o-mini',
                messages: [{
                    role: 'user',
                    content: prompt
                }],
                max_tokens: 4000,
                temperature: 0.7
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('OpenAI API Error:', errorData);
            return {
                statusCode: 500,
                headers,
                body: JSON.stringify({ 
                    error: 'Failed to generate report',
                    details: errorData.error?.message || 'Unknown error'
                })
            };
        }

        const data = await response.json();
        const reportContent = data.choices[0].message.content;

        // HTML 보고서 생성
        const htmlReport = `
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${companyName} - 회사 보고서</title>
    <style>
        body {
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .report-container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .report-header {
            text-align: center;
            border-bottom: 2px solid #7c3aed;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .report-title {
            color: #7c3aed;
            font-size: 2rem;
            margin: 0;
        }
        .report-subtitle {
            color: #666;
            font-size: 1.1rem;
            margin: 10px 0 0 0;
        }
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            color: #7c3aed;
            font-size: 1.3rem;
            border-left: 4px solid #7c3aed;
            padding-left: 15px;
            margin-bottom: 15px;
        }
        .section-content {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #e9ecef;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
        .close-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #7c3aed;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        .close-btn:hover {
            background: #6d28d9;
        }
    </style>
</head>
<body>
    <button class="close-btn" onclick="window.close()">닫기</button>
    <div class="report-container">
        <div class="report-header">
            <h1 class="report-title">${companyName}</h1>
            <p class="report-subtitle">회사 정보 보고서</p>
            <p style="color: #999; font-size: 0.9rem;">생성일: ${new Date().toLocaleDateString('ko-KR')}</p>
        </div>
        <div class="report-content">
            ${reportContent}
        </div>
    </div>
</body>
</html>`;

        return {
            statusCode: 200,
            headers: {
                ...headers,
                'Content-Type': 'text/html'
            },
            body: htmlReport
        };

    } catch (error) {
        console.error('Error generating company report:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ 
                error: 'Internal server error',
                details: error.message 
            })
        };
    }
};
