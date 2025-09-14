/**
 * Google Docs 템플릿을 Word 형식으로 다운로드하는 스크립트
 * Google Docs API를 사용하여 템플릿을 다운로드하고 Google Cloud Storage에 업로드
 */

const { Storage } = require('@google-cloud/storage');
const fs = require('fs');
const path = require('path');

// Google Docs ID (URL에서 추출)
const GOOGLE_DOCS_ID = '1a3Wxddq7EYm0bLiy_tTSI5FuBPQW_HsNnRORQWcVfbY';

async function downloadTemplateFromGoogleDocs() {
  try {
    console.log('Google Docs 템플릿 다운로드 시작...');
    
    // Google Cloud Storage 클라이언트 초기화
    const storage = new Storage({
      projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
      keyFilename: process.env.GOOGLE_CLOUD_KEY_FILE,
    });
    
    const bucketName = process.env.GOOGLE_CLOUD_BUCKET_NAME || 'lrqa-templates';
    const fileName = 'LRQA_quotation.docx';
    
    // Google Docs에서 Word 형식으로 다운로드
    const exportUrl = `https://docs.google.com/document/d/${GOOGLE_DOCS_ID}/export?format=docx`;
    
    console.log(`다운로드 URL: ${exportUrl}`);
    
    // 파일 다운로드
    const response = await fetch(exportUrl);
    if (!response.ok) {
      throw new Error(`다운로드 실패: ${response.status} ${response.statusText}`);
    }
    
    const fileBuffer = await response.arrayBuffer();
    console.log(`다운로드 완료: ${fileBuffer.byteLength} bytes`);
    
    // Google Cloud Storage에 업로드
    const bucket = storage.bucket(bucketName);
    const file = bucket.file(fileName);
    
    await file.save(Buffer.from(fileBuffer), {
      metadata: {
        contentType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      },
    });
    
    console.log(`Google Cloud Storage에 업로드 완료: ${bucketName}/${fileName}`);
    
    // 로컬에도 저장 (백업)
    const localPath = path.join(__dirname, '..', 'public', 'templates', fileName);
    fs.mkdirSync(path.dirname(localPath), { recursive: true });
    fs.writeFileSync(localPath, Buffer.from(fileBuffer));
    console.log(`로컬 저장 완료: ${localPath}`);
    
  } catch (error) {
    console.error('템플릿 다운로드 오류:', error);
    throw error;
  }
}

// 스크립트 실행
if (require.main === module) {
  downloadTemplateFromGoogleDocs()
    .then(() => {
      console.log('템플릿 다운로드 완료!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('오류 발생:', error);
      process.exit(1);
    });
}

module.exports = { downloadTemplateFromGoogleDocs };
