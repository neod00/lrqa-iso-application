import zipfile
import os

def add_missing_variables():
    """누락된 변수들을 템플릿에 추가합니다."""
    
    template_path = 'public/templates/LRQA_quotation.docx'
    
    print(f"템플릿 파일: {template_path}")
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return False
    
    # 누락된 변수들
    missing_variables = [
        '{{ has_iso9001 }}',
        '{{ has_iso14001 }}',
        '{{ has_iso45001 }}'
    ]
    
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_read:
            with zipfile.ZipFile(template_path + '.tmp', 'w', zipfile.ZIP_DEFLATED) as zip_write:
                for file_info in zip_read.infolist():
                    content = zip_read.read(file_info.filename)
                    
                    # word/document.xml 파일인 경우 누락된 변수 추가
                    if file_info.filename == "word/document.xml":
                        content_str = content.decode('utf-8')
                        original_content = content_str
                        
                        print(f"\n=== {file_info.filename} 처리 중 ===")
                        
                        # 누락된 변수들을 템플릿 끝에 추가
                        for var in missing_variables:
                            if var not in content_str:
                                content_str = content_str.replace(
                                    '</w:document>', 
                                    f'<w:p><w:r><w:t>{var}</w:t></w:r></w:p></w:document>'
                                )
                                print(f"✓ {var} 변수 추가")
                        
                        # 변경사항이 있는지 확인
                        if content_str != original_content:
                            print(f"✅ 누락된 변수 추가 완료")
                        else:
                            print(f"⚠️  변경사항 없음")
                        
                        # 변경된 내용을 다시 바이트로 변환
                        content = content_str.encode('utf-8')
                    
                    # 파일 쓰기
                    zip_write.writestr(file_info, content)
        
        # 임시 파일을 원본 파일로 교체
        os.replace(template_path + '.tmp', template_path)
        
        print(f"\n🎉 누락된 변수 추가 완료: {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == '__main__':
    add_missing_variables()
