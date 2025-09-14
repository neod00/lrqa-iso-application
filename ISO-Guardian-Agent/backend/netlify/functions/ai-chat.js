/**
 * ISO-Guardian AI 채팅 API
 * 
 * 주요 기능:
 * - 사용자 메시지 처리
 * - AI 응답 생성
 * - LRQA 링크 매칭
 * - 대화 기록 저장
 */

const { spawn } = require('child_process');
const path = require('path');

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
        console.log('=== ISO-Guardian AI 채팅 요청 처리 ===');
        
        // 요청 데이터 파싱
        const requestData = JSON.parse(event.body);
        const { message, conversationHistory, userProfile } = requestData;
        
        console.log('받은 메시지:', message);
        console.log('대화 기록 길이:', conversationHistory?.length || 0);

        // AI 응답 생성
        const aiResponse = await generateAIResponse(message, conversationHistory, userProfile);
        
        console.log('AI 응답 생성 완료');
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                data: aiResponse
            })
        };

    } catch (error) {
        console.error('AI 채팅 처리 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: error.message,
                message: 'AI 채팅 처리 중 오류가 발생했습니다.'
            })
        };
    }
};

/**
 * AI 응답 생성
 */
async function generateAIResponse(message, conversationHistory, userProfile) {
    try {
        // Python AI 엔진 경로 설정
        const pythonPath = process.env.PYTHON_PATH || 'python';
        const aiEnginePath = path.join(__dirname, '..', '..', 'python', 'ai_agent');
        
        console.log('Python 경로:', pythonPath);
        console.log('AI 엔진 경로:', aiEnginePath);

        // 임시 JSON 파일 생성
        const fs = require('fs');
        const os = require('os');
        const tempFile = path.join(os.tmpdir(), `ai_chat_${Date.now()}.json`);
        
        try {
            const requestData = {
                message,
                conversationHistory: conversationHistory || [],
                userProfile: userProfile || {},
                timestamp: new Date().toISOString()
            };

            fs.writeFileSync(tempFile, JSON.stringify(requestData, null, 2));
            console.log('임시 파일 생성:', tempFile);

            // Python AI 엔진 실행
            const result = await runPythonAIEngine(pythonPath, aiEnginePath, tempFile);
            
            // 임시 파일 삭제
            fs.unlinkSync(tempFile);
            
            return result;

        } catch (error) {
            // 임시 파일 정리
            try {
                if (fs.existsSync(tempFile)) {
                    fs.unlinkSync(tempFile);
                }
            } catch (cleanupError) {
                console.warn('임시 파일 정리 실패:', cleanupError);
            }
            throw error;
        }

    } catch (error) {
        console.error('AI 응답 생성 실패:', error);
        
        // 폴백 응답 생성
        return generateFallbackResponse(message);
    }
}

/**
 * Python AI 엔진 실행
 */
function runPythonAIEngine(pythonPath, aiEnginePath, inputFile) {
    return new Promise((resolve, reject) => {
        console.log('Python AI 엔진 실행 시작');
        
        // Python 스크립트 실행
        const pythonProcess = spawn(pythonPath, [
            '-c',
            `
import sys
import os
import json
sys.path.append('${aiEnginePath}')

try:
    from ai_agent import ISOGuardianAI
    
    # JSON 파일 읽기
    with open('${inputFile}', 'r', encoding='utf-8') as f:
        request_data = json.load(f)
    
    # AI 에이전트 초기화
    ai_agent = ISOGuardianAI()
    
    # 응답 생성
    response = ai_agent.process_message(
        request_data['message'],
        request_data.get('conversationHistory', []),
        request_data.get('userProfile', {})
    )
    
    # 결과 출력
    print(json.dumps(response, ensure_ascii=False, indent=2))
    
except Exception as e:
    error_result = {
        "success": False,
        "error": str(e),
        "message": "Python AI 엔진 실행 중 오류가 발생했습니다."
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
    sys.exit(1)
            `
        ], {
            cwd: aiEnginePath,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let outputData = '';
        let errorData = '';

        pythonProcess.stdout.on('data', (data) => {
            outputData += data.toString();
            console.log('Python stdout:', data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
            console.error('Python stderr:', data.toString());
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python 프로세스 종료 코드: ${code}`);
            
            if (code === 0) {
                try {
                    const result = JSON.parse(outputData);
                    resolve(result);
                } catch (parseError) {
                    console.error('JSON 파싱 오류:', parseError);
                    console.error('출력 데이터:', outputData);
                    reject(new Error('Python AI 엔진 출력 파싱 실패'));
                }
            } else {
                console.error('Python AI 엔진 실행 실패');
                console.error('에러 출력:', errorData);
                reject(new Error(`Python AI 엔진 실행 실패 (코드: ${code}): ${errorData}`));
            }
        });

        pythonProcess.on('error', (error) => {
            console.error('Python 프로세스 오류:', error);
            reject(new Error(`Python 프로세스 실행 실패: ${error.message}`));
        });

        // 타임아웃 설정 (30초)
        setTimeout(() => {
            pythonProcess.kill();
            reject(new Error('Python AI 엔진 실행 타임아웃'));
        }, 30000);
    });
}

/**
 * 폴백 응답 생성 (Python 엔진 실패 시)
 */
function generateFallbackResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    // 간단한 키워드 기반 응답
    if (lowerMessage.includes('iso') || lowerMessage.includes('인증')) {
        return {
            success: true,
            text: `"${message}"에 대한 질문을 이해했습니다.\n\n` +
                  `ISO-Guardian은 ISO 인증과 관련된 교육적 정보를 제공합니다.\n\n` +
                  `다음과 같은 질문을 도와드릴 수 있습니다:\n` +
                  `• ISO 표준에 대한 설명\n` +
                  `• 인증 프로세스 안내\n` +
                  `• 비용 및 견적 정보\n` +
                  `• 교육 프로그램 안내\n\n` +
                  `더 구체적으로 질문해주시면 정확한 답변을 드리겠습니다!`,
            lrqaLinks: [
                {
                    title: 'LRQA 홈페이지',
                    url: 'https://www.lrqa.com/kr'
                },
                {
                    title: 'ISO 표준 정보',
                    url: 'https://www.lrqa.com/kr/iso-standards'
                }
            ],
            intent: 'general',
            confidence: 0.5
        };
    }
    
    if (lowerMessage.includes('9001') || lowerMessage.includes('품질')) {
        return {
            success: true,
            text: `ISO 9001 (품질경영시스템)에 대해 설명드리겠습니다.\n\n` +
                  `📋 **정의**: 고객 만족을 위한 품질 관리 시스템\n\n` +
                  `📝 **주요 요구사항**:\n` +
                  `• 고객 중심\n` +
                  `• 지속적 개선\n` +
                  `• 프로세스 접근법\n\n` +
                  `✅ **기대 효과**:\n` +
                  `• 품질 향상\n` +
                  `• 고객 만족도 증가\n` +
                  `• 비용 절감`,
            lrqaLinks: [
                {
                    title: 'ISO 9001 상세 정보',
                    url: 'https://www.lrqa.com/kr/iso9001'
                },
                {
                    title: '품질경영시스템 안내',
                    url: 'https://www.lrqa.com/kr/quality-management'
                }
            ],
            intent: 'iso_standard',
            confidence: 0.8
        };
    }
    
    if (lowerMessage.includes('14001') || lowerMessage.includes('환경')) {
        return {
            success: true,
            text: `ISO 14001 (환경경영시스템)에 대해 설명드리겠습니다.\n\n` +
                  `📋 **정의**: 환경 보호를 위한 경영 시스템\n\n` +
                  `📝 **주요 요구사항**:\n` +
                  `• 환경 정책\n` +
                  `• 법규 준수\n` +
                  `• 지속가능성\n\n` +
                  `✅ **기대 효과**:\n` +
                  `• 환경 보호\n` +
                  `• 법규 준수\n` +
                  `• 이미지 향상`,
            lrqaLinks: [
                {
                    title: 'ISO 14001 상세 정보',
                    url: 'https://www.lrqa.com/kr/iso14001'
                },
                {
                    title: '환경경영시스템 안내',
                    url: 'https://www.lrqa.com/kr/environmental-management'
                }
            ],
            intent: 'iso_standard',
            confidence: 0.8
        };
    }
    
    if (lowerMessage.includes('45001') || lowerMessage.includes('안전') || lowerMessage.includes('보건')) {
        return {
            success: true,
            text: `ISO 45001 (안전보건경영시스템)에 대해 설명드리겠습니다.\n\n` +
                  `📋 **정의**: 직장 안전과 직원 건강을 위한 시스템\n\n` +
                  `📝 **주요 요구사항**:\n` +
                  `• 안전 정책\n` +
                  `• 위험 관리\n` +
                  `• 직원 참여\n\n` +
                  `✅ **기대 효과**:\n` +
                  `• 사고 감소\n` +
                  `• 직원 안전\n` +
                  `• 생산성 향상`,
            lrqaLinks: [
                {
                    title: 'ISO 45001 상세 정보',
                    url: 'https://www.lrqa.com/kr/iso45001'
                },
                {
                    title: '안전보건경영시스템 안내',
                    url: 'https://www.lrqa.com/kr/occupational-health-safety'
                }
            ],
            intent: 'iso_standard',
            confidence: 0.8
        };
    }
    
    if (lowerMessage.includes('프로세스') || lowerMessage.includes('과정')) {
        return {
            success: true,
            text: `LRQA의 ISO 인증 프로세스를 안내드리겠습니다.\n\n` +
                  `🔄 **인증 단계**:\n` +
                  `1. 신청서 제출: ISO-Guardian을 통한 신청서 작성\n` +
                  `2. 1단계 심사: 문서 검토 및 사전 심사\n` +
                  `3. 2단계 심사: 현장 심사 및 인증 심사\n` +
                  `4. 인증서 발급: 심사 통과 시 인증서 발급\n\n` +
                  `⏰ **소요 기간**: 일반적으로 3-6개월 소요\n\n` +
                  `📋 **준비사항**:\n` +
                  `• 필요한 문서 준비\n` +
                  `• 시스템 구축\n` +
                  `• 직원 교육`,
            lrqaLinks: [
                {
                    title: '인증 프로세스 상세 안내',
                    url: 'https://www.lrqa.com/kr/certification-process'
                },
                {
                    title: '심사 단계별 설명',
                    url: 'https://www.lrqa.com/kr/audit-stages'
                },
                {
                    title: '인증 일정 안내',
                    url: 'https://www.lrqa.com/kr/certification-timeline'
                }
            ],
            intent: 'certification_process',
            confidence: 0.9
        };
    }
    
    if (lowerMessage.includes('비용') || lowerMessage.includes('가격') || lowerMessage.includes('견적')) {
        return {
            success: true,
            text: `ISO 인증 비용에 대해 안내드리겠습니다.\n\n` +
                  `💰 **비용 결정 요소**:\n` +
                  `• 기업 규모 (직원 수)\n` +
                  `• 사업장 수\n` +
                  `• 선택한 ISO 표준\n` +
                  `• 인증 범위\n` +
                  `• 통합 심사 여부\n\n` +
                  `정확한 견적을 받으시려면 신청서를 작성해주세요. ` +
                  `ADJ v2.2 기준에 따라 정확하게 계산해드립니다.`,
            lrqaLinks: [
                {
                    title: '요금 안내',
                    url: 'https://www.lrqa.com/kr/pricing'
                },
                {
                    title: '견적 요청',
                    url: 'https://www.lrqa.com/kr/quote-request'
                }
            ],
            intent: 'pricing',
            confidence: 0.8
        };
    }
    
    // 기본 응답
    return {
        success: true,
        text: `"${message}"에 대한 질문을 이해했습니다.\n\n` +
              `ISO-Guardian은 ISO 인증과 관련된 교육적 정보를 제공합니다.\n\n` +
              `다음과 같은 질문을 도와드릴 수 있습니다:\n` +
              `• ISO 표준에 대한 설명\n` +
              `• 인증 프로세스 안내\n` +
              `• 비용 및 견적 정보\n` +
              `• 교육 프로그램 안내\n\n` +
              `더 구체적으로 질문해주시면 정확한 답변을 드리겠습니다!`,
        lrqaLinks: [
            {
                title: 'LRQA 홈페이지',
                url: 'https://www.lrqa.com/kr'
            },
            {
                title: 'ISO 표준 정보',
                url: 'https://www.lrqa.com/kr/iso-standards'
            }
        ],
        intent: 'general',
        confidence: 0.3
    };
}
