/**
 * ADJ v2.2 견적 계산 Netlify Function
 * Python ADJ v2.2 엔진과 연동하여 정확한 견적 계산
 */

const { spawn } = require('child_process');
const path = require('path');
const fetch = require('node-fetch');

exports.handler = async (event, context) => {
    // CORS 헤더 설정
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // OPTIONS 요청 처리
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    // POST 요청만 처리
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ 
                success: false, 
                error: 'Method not allowed' 
            })
        };
    }

    try {
        console.log('=== ADJ v2.2 견적 계산 시작 ===');
        
        // 요청 데이터 파싱
        const requestData = JSON.parse(event.body);
        console.log('받은 데이터:', Object.keys(requestData));

        // 핵심두뇌 API 직접 호출 (Python 엔진 대신)
        console.log('핵심두뇌 API 직접 호출 시작');
        
        try {
            // 핵심두뇌 API 엔진 직접 실행
            const result = await runCoreAPIEngine(requestData);
            
            console.log('핵심두뇌 API 계산 완료');
            return {
                statusCode: 200,
                headers,
                body: JSON.stringify(result)
            };

        } catch (error) {
            console.error('핵심두뇌 API 실행 오류:', error);
            throw error;
        }

    } catch (error) {
        console.error('ADJ v2.2 계산 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: error.message,
                message: 'ADJ v2.2 견적 계산 중 오류가 발생했습니다.'
            })
        };
    }
};

/**
 * 핵심두뇌 API 엔진 직접 실행
 */
async function runCoreAPIEngine(requestData) {
    try {
        console.log('핵심두뇌 API 엔진 실행 시작');
        
        // 핵심두뇌 API 서버 URL (Vercel 배포된 API 사용)
        const coreAPIUrl = process.env.CORE_API_URL || 'https://lrqa-iso-application-hqhk5q4qp-dal-kims-projects.vercel.app';
        
        console.log('핵심두뇌 API URL:', coreAPIUrl);
        
        // 핵심두뇌 API 호출
        const response = await fetch(`${coreAPIUrl}/calculate-audit-days`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`핵심두뇌 API 호출 실패: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        console.log('핵심두뇌 API 응답:', result);
        
        return result;
        
    } catch (error) {
        console.error('핵심두뇌 API 호출 오류:', error);
        
        // API 호출 실패 시 기본 응답 반환
        return {
            success: false,
            error: error.message,
            message: '핵심두뇌 API 호출 중 오류가 발생했습니다.'
        };
    }
}
