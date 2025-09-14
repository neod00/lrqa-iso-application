/**
 * Google Cloud Storage 설정 도우미 스크립트
 * 버킷 생성 및 권한 설정을 도와줍니다.
 */

const { Storage } = require('@google-cloud/storage');

async function setupGoogleCloudStorage() {
  try {
    console.log('Google Cloud Storage 설정 시작...');
    
    // Google Cloud Storage 클라이언트 초기화
    const storage = new Storage({
      projectId: process.env.GOOGLE_CLOUD_PROJECT_ID,
      keyFilename: process.env.GOOGLE_CLOUD_KEY_FILE,
    });
    
    const bucketName = process.env.GOOGLE_CLOUD_BUCKET_NAME || 'lrqa-templates';
    
    console.log(`버킷 생성 시도: ${bucketName}`);
    
    // 버킷 생성
    const [bucket] = await storage.createBucket(bucketName, {
      location: 'asia-northeast3', // 서울 리전
      storageClass: 'STANDARD',
    });
    
    console.log(`버킷 생성 완료: ${bucket.name}`);
    
    // 버킷을 공개로 설정 (템플릿 파일 다운로드용)
    await bucket.iam.setPolicy({
      bindings: [
        {
          role: 'roles/storage.objectViewer',
          members: ['allUsers'],
        },
      ],
    });
    
    console.log('버킷 공개 설정 완료');
    
    // 버킷 정보 출력
    const [metadata] = await bucket.getMetadata();
    console.log('버킷 정보:');
    console.log(`- 이름: ${metadata.name}`);
    console.log(`- 위치: ${metadata.location}`);
    console.log(`- 스토리지 클래스: ${metadata.storageClass}`);
    console.log(`- 생성일: ${metadata.timeCreated}`);
    
    console.log('\n✅ Google Cloud Storage 설정 완료!');
    console.log('\n다음 단계:');
    console.log('1. npm run download-template 명령으로 템플릿 다운로드');
    console.log('2. Vercel 환경 변수 설정:');
    console.log(`   - GOOGLE_CLOUD_PROJECT_ID=${process.env.GOOGLE_CLOUD_PROJECT_ID}`);
    console.log(`   - GOOGLE_CLOUD_BUCKET_NAME=${bucketName}`);
    console.log('   - GOOGLE_CLOUD_SERVICE_ACCOUNT_KEY_BASE64=<base64-encoded-key>');
    
  } catch (error) {
    if (error.code === 409) {
      console.log('버킷이 이미 존재합니다.');
    } else {
      console.error('Google Cloud Storage 설정 오류:', error);
      throw error;
    }
  }
}

// 스크립트 실행
if (require.main === module) {
  setupGoogleCloudStorage()
    .then(() => {
      console.log('설정 완료!');
      process.exit(0);
    })
    .catch((error) => {
      console.error('오류 발생:', error);
      process.exit(1);
    });
}

module.exports = { setupGoogleCloudStorage };
