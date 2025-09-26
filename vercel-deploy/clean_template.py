import zipfile
import os
import re

def clean_template():
    """템플릿을 완전히 정리하여 변수들을 올바른 위치에만 배치합니다."""
    
    template_path = 'public/templates/LRQA_quotation.docx'
    
    print(f"템플릿 파일: {template_path}")
    
    if not os.path.exists(template_path):
        print(f"❌ 템플릿 파일을 찾을 수 없습니다: {template_path}")
        return False
    
    try:
        with zipfile.ZipFile(template_path, 'r') as zip_read:
            with zipfile.ZipFile(template_path + '.tmp', 'w', zipfile.ZIP_DEFLATED) as zip_write:
                for file_info in zip_read.infolist():
                    content = zip_read.read(file_info.filename)
                    
                    # word/document.xml 파일인 경우 구조 수정
                    if file_info.filename == "word/document.xml":
                        content_str = content.decode('utf-8')
                        original_content = content_str
                        
                        print(f"\n=== {file_info.filename} 완전 정리 중 ===")
                        
                        # 1. </w:document> 태그 밖의 모든 내용 제거
                        document_end_pattern = r'</w:document>.*$'
                        if re.search(document_end_pattern, content_str, re.DOTALL):
                            content_str = re.sub(document_end_pattern, '</w:document>', content_str, flags=re.DOTALL)
                            print("✅ </w:document> 태그 밖의 내용 제거 완료")
                        
                        # 2. </w:body> 태그 밖의 모든 변수 제거
                        body_end_pattern = r'</w:body>.*?(?=</w:document>)'
                        if re.search(body_end_pattern, content_str, re.DOTALL):
                            content_str = re.sub(body_end_pattern, '</w:body>', content_str, flags=re.DOTALL)
                            print("✅ </w:body> 태그 밖의 변수들 제거 완료")
                        
                        # 3. </w:sectPr> 태그 바로 앞에 변수들 추가 (</w:body> 태그 안에)
                        sectpr_pattern = r'(<w:sectPr[^>]*>.*?</w:sectPr>)'
                        if re.search(sectpr_pattern, content_str, re.DOTALL):
                            # 추가할 변수들
                            variables_to_add = [
                                '{{ quotation_date }}',
                                '{{ quotation_number }}',
                                '{{ client_name }}',
                                '{{ client_address }}',
                                '{{ contact_person }}',
                                '{{ contact_email }}',
                                '{{ contact_phone }}',
                                '{{ standards_text }}',
                                '{{ total_sites }}',
                                '{{ total_employees }}',
                                '{{ total_audit_days }}',
                                '{{ total_cost_with_travel_formatted }}',
                                '{{ travel_expense_formatted }}',
                                '{{ iso14001_surveillance_days }}',
                                '{{ iso14001_stage1_2_days }}',
                                '{{ iso14001_stage1_2_cost_formatted }}',
                                '{{ has_iso9001 }}',
                                '{{ has_iso14001 }}',
                                '{{ has_iso45001 }}'
                            ]
                            
                            # 변수들을 </w:sectPr> 태그 앞에 추가
                            variables_xml = ''
                            for var in variables_to_add:
                                variables_xml += f'<w:p><w:r><w:t>{var}</w:t></w:r></w:p>'
                            
                            content_str = re.sub(
                                sectpr_pattern, 
                                f'{variables_xml}\\1', 
                                content_str,
                                flags=re.DOTALL
                            )
                            print(f"✅ {len(variables_to_add)}개 변수를 </w:body> 태그 안에 추가")
                        
                        # 변경사항이 있는지 확인
                        if content_str != original_content:
                            print(f"✅ 템플릿 완전 정리 완료")
                        else:
                            print(f"⚠️  변경사항 없음")
                        
                        # 변경된 내용을 다시 바이트로 변환
                        content = content_str.encode('utf-8')
                    
                    # 파일 쓰기
                    zip_write.writestr(file_info, content)
        
        # 임시 파일을 원본 파일로 교체
        os.replace(template_path + '.tmp', template_path)
        
        print(f"\n🎉 템플릿 완전 정리 완료: {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == '__main__':
    clean_template()
