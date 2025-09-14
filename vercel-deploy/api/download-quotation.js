/**
 * 견적서 Word 문서 다운로드 API
 * 생성된 Word 문서를 다운로드할 수 있도록 제공
 */

import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');

  // OPTIONS 요청 처리 (CORS preflight)
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // GET 요청만 허용
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    // 파일명 파라미터 확인
    const { filename } = req.query;
    
    if (!filename) {
      res.status(400).json({ error: 'Filename parameter is required' });
      return;
    }

    // 파일 경로 생성
    const filePath = path.join('/tmp', filename);
    
    // 파일 존재 확인
    if (!fs.existsSync(filePath)) {
      res.status(404).json({ error: 'File not found' });
      return;
    }

    // 파일 읽기
    const fileBuffer = fs.readFileSync(filePath);
    
    // 응답 헤더 설정
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Length', fileBuffer.length);
    
    // 파일 전송
    res.status(200).send(fileBuffer);
    
    console.log(`Word 문서 다운로드: ${filename}`);
    
  } catch (error) {
    console.error('Error downloading file:', error);
    res.status(500).json({
      error: '파일 다운로드 중 오류가 발생했습니다.',
      message: error.message
    });
  }
}

