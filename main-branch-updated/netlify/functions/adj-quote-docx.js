/**
 * ADJ v2.2 Word 문서 생성 Netlify Function
 * Python ADJ v2.2 엔진을 사용하여 Word 문서 생성
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
        console.log('=== ADJ v2.2 Word 문서 생성 시작 ===');
        
        // 요청 데이터 파싱
        const requestData = JSON.parse(event.body);
        console.log('받은 데이터:', Object.keys(requestData));

        // Python 엔진 경로 설정
        const pythonPath = process.env.PYTHON_PATH || 'python';
        const enginePath = path.join(__dirname, '..', '..', 'adj_quote_engine');
        
        console.log('Python 경로:', pythonPath);
        console.log('엔진 경로:', enginePath);

        // 임시 JSON 파일 생성
        const fs = require('fs');
        const os = require('os');
        const tempFile = path.join(os.tmpdir(), `adj_quote_docx_${Date.now()}.json`);
        const outputFile = path.join(os.tmpdir(), `quotation_${Date.now()}.docx`);
        
        try {
            fs.writeFileSync(tempFile, JSON.stringify(requestData, null, 2));
            console.log('임시 파일 생성:', tempFile);

            // Python 엔진 실행
            const result = await runPythonEngine(pythonPath, enginePath, tempFile, outputFile);
            
            // 임시 파일 삭제
            fs.unlinkSync(tempFile);
            
            console.log('ADJ v2.2 Word 문서 생성 완료');
            return {
                statusCode: 200,
                headers,
                body: JSON.stringify(result)
            };

        } catch (error) {
            // 임시 파일 정리
            try {
                if (fs.existsSync(tempFile)) {
                    fs.unlinkSync(tempFile);
                }
                if (fs.existsSync(outputFile)) {
                    fs.unlinkSync(outputFile);
                }
            } catch (cleanupError) {
                console.warn('임시 파일 정리 실패:', cleanupError);
            }
            throw error;
        }

    } catch (error) {
        console.error('ADJ v2.2 Word 문서 생성 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: error.message,
                message: 'ADJ v2.2 Word 문서 생성 중 오류가 발생했습니다.'
            })
        };
    }
};

/**
 * Python ADJ v2.2 엔진으로 Word 문서 생성
 */
function runPythonEngine(pythonPath, enginePath, inputFile, outputFile) {
    return new Promise((resolve, reject) => {
        console.log('Python 엔진 실행 시작 (Word 문서 생성)');
        
        // Python 스크립트 실행
        const pythonProcess = spawn(pythonPath, [
            '-c',
            `
import sys
import os
import json
sys.path.append('${enginePath}')

try:
    from adj_quote_engine.js_integration import js_integration
    
    # JSON 파일 읽기
    with open('${inputFile}', 'r', encoding='utf-8') as f:
        js_data = json.load(f)
    
    # Word 문서 생성
    result = js_integration.generate_word_document(js_data, '${outputFile}')
    
    # 결과 출력
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
except Exception as e:
    error_result = {
        "success": False,
        "error": str(e),
        "message": "Python 엔진 실행 중 오류가 발생했습니다."
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
                    
                    // Word 문서가 생성되었는지 확인
                    if (result.success && os.path.exists('${outputFile}')):
                        result.file_path = '${outputFile}';
                        result.file_size = os.path.getsize('${outputFile}')
                    
                    resolve(result);
                } catch (parseError) {
                    console.error('JSON 파싱 오류:', parseError);
                    console.error('출력 데이터:', outputData);
                    reject(new Error('Python 엔진 출력 파싱 실패'));
                }
            } else {
                console.error('Python 엔진 실행 실패');
                console.error('에러 출력:', errorData);
                reject(new Error(`Python 엔진 실행 실패 (코드: ${code}): ${errorData}`));
            }
        });

        pythonProcess.on('error', (error) => {
            console.error('Python 프로세스 오류:', error);
            reject(new Error(`Python 프로세스 실행 실패: ${error.message}`));
        });

        // 타임아웃 설정 (60초)
        setTimeout(() => {
            pythonProcess.kill();
            reject(new Error('Python 엔진 실행 타임아웃'));
        }, 60000);
    });
}
