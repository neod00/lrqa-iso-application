/**
 * ADJ v2.2 엔진 상태 확인 Netlify Function
 * Python ADJ v2.2 엔진의 상태를 확인합니다.
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

    // GET 요청만 처리
    if (event.httpMethod !== 'GET') {
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
        console.log('=== ADJ v2.2 엔진 상태 확인 ===');
        
        // Python 엔진 경로 설정
        const pythonPath = process.env.PYTHON_PATH || 'python';
        const enginePath = path.join(__dirname, '..', '..', 'adj_quote_engine');
        
        console.log('Python 경로:', pythonPath);
        console.log('엔진 경로:', enginePath);

        // Python 엔진 상태 확인
        const result = await checkPythonEngine(pythonPath, enginePath);
        
        console.log('ADJ v2.2 엔진 상태 확인 완료');
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(result)
        };

    } catch (error) {
        console.error('ADJ v2.2 엔진 상태 확인 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: error.message,
                message: 'ADJ v2.2 엔진 상태 확인 중 오류가 발생했습니다.'
            })
        };
    }
};

/**
 * Python ADJ v2.2 엔진 상태 확인
 */
function checkPythonEngine(pythonPath, enginePath) {
    return new Promise((resolve, reject) => {
        console.log('Python 엔진 상태 확인 시작');
        
        // Python 스크립트 실행
        const pythonProcess = spawn(pythonPath, [
            '-c',
            `
import sys
import os
sys.path.append('${enginePath}')

try:
    # 기본 모듈 import 테스트
    from adj_quote_engine import QuoteEngine, Organization, Site, StandardType
    from adj_quote_engine.adj_rules_v22 import quote_engine
    from adj_quote_engine.pricing import pricing_calculator
    from adj_quote_engine.quote_docx import docx_exporter
    from adj_quote_engine.js_integration import js_integration
    
    # 간단한 테스트 실행
    test_org = Organization(
        client_name="Test Company",
        sites=[Site(name="Test Site", address="Test Address", standards=[StandardType.ISO9001])],
        standards=[StandardType.ISO9001]
    )
    
    result = quote_engine.calculate_quote(test_org)
    
    status_result = {
        "success": True,
        "status": "online",
        "message": "ADJ v2.2 엔진이 정상적으로 작동합니다.",
        "version": "1.0.0",
        "python_version": sys.version,
        "modules_loaded": True,
        "test_calculation": True
    }
    
    print(json.dumps(status_result, ensure_ascii=False, indent=2))
    
except ImportError as e:
    error_result = {
        "success": False,
        "status": "offline",
        "error": f"모듈 import 실패: {str(e)}",
        "message": "ADJ v2.2 엔진 모듈을 찾을 수 없습니다."
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
    sys.exit(1)
    
except Exception as e:
    error_result = {
        "success": False,
        "status": "error",
        "error": str(e),
        "message": "ADJ v2.2 엔진 테스트 중 오류가 발생했습니다."
    }
    print(json.dumps(error_result, ensure_ascii=False, indent=2))
    sys.exit(1)
            `
        ], {
            cwd: enginePath,
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
                    resolve({
                        success: false,
                        status: 'error',
                        error: 'Python 엔진 출력 파싱 실패',
                        message: 'Python 엔진 상태 확인 중 오류가 발생했습니다.'
                    });
                }
            } else {
                console.error('Python 엔진 상태 확인 실패');
                console.error('에러 출력:', errorData);
                resolve({
                    success: false,
                    status: 'offline',
                    error: `Python 엔진 실행 실패 (코드: ${code})`,
                    message: 'ADJ v2.2 엔진을 사용할 수 없습니다.',
                    details: errorData
                });
            }
        });

        pythonProcess.on('error', (error) => {
            console.error('Python 프로세스 오류:', error);
            resolve({
                success: false,
                status: 'offline',
                error: `Python 프로세스 실행 실패: ${error.message}`,
                message: 'ADJ v2.2 엔진을 실행할 수 없습니다.'
            });
        });

        // 타임아웃 설정 (10초)
        setTimeout(() => {
            pythonProcess.kill();
            resolve({
                success: false,
                status: 'timeout',
                error: 'Python 엔진 상태 확인 타임아웃',
                message: 'ADJ v2.2 엔진 응답이 지연되고 있습니다.'
            });
        }, 10000);
    });
}
