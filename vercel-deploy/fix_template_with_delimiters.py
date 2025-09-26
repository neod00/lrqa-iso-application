import zipfile
import os
import re
import shutil

def add_delimiters_to_template():
    """원본 템플릿에 {{ }} 구분자를 추가합니다."""
    
    original_template = 'public/templates/LRQA_quotation_original.docx'
    fixed_template = 'public/templates/LRQA_quotation.docx'
    
    print(f"원본 템플릿: {original_template}")
    print(f"수정할 템플릿: {fixed_template}")
    
    # 원본 템플릿이 존재하는지 확인
    if not os.path.exists(original_template):
        print(f"❌ 원본 템플릿을 찾을 수 없습니다: {original_template}")
        return False
    
    # 백업 생성
    backup_template = 'public/templates/LRQA_quotation_backup.docx'
    if os.path.exists(fixed_template):
        shutil.copy(fixed_template, backup_template)
        print(f"백업 생성: {backup_template}")
    
    # 변수 매핑 (원본 텍스트 -> {{ 변수명 }})
    variable_mappings = {
        # 기본 정보
        'quotation_date': '{{ quotation_date }}',
        'quotation_number': '{{ quotation_number }}',
        'client_name': '{{ client_name }}',
        'client_address': '{{ client_address }}',
        'contact_person': '{{ contact_person }}',
        'contact_email': '{{ contact_email }}',
        'contact_phone': '{{ contact_phone }}',
        'standards_text': '{{ standards_text }}',
        'total_sites': '{{ total_sites }}',
        'total_employees': '{{ total_employees }}',
        
        # 비용 정보
        'total_audit_days': '{{ total_audit_days }}',
        'total_cost_with_travel_formatted': '{{ total_cost_with_travel_formatted }}',
        'travel_expense_formatted': '{{ travel_expense_formatted }}',
        
        # ISO 14001 관련
        'iso14001_surveillance_days': '{{ iso14001_surveillance_days }}',
        'iso14001_stage1_2_days': '{{ iso14001_stage1_2_days }}',
        'iso14001_stage1_2_cost_formatted': '{{ iso14001_stage1_2_cost_formatted }}',
        
        # 조건부 표시
        'has_iso9001': '{{ has_iso9001 }}',
        'has_iso14001': '{{ has_iso14001 }}',
        'has_iso45001': '{{ has_iso45001 }}',
    }
    
    try:
        with zipfile.ZipFile(original_template, 'r') as zip_read:
            with zipfile.ZipFile(fixed_template, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                for file_info in zip_read.infolist():
                    content = zip_read.read(file_info.filename)
                    
                    # word/document.xml 파일인 경우 구분자 추가
                    if file_info.filename == "word/document.xml":
                        content_str = content.decode('utf-8')
                        original_content = content_str
                        
                        print(f"\n=== {file_info.filename} 처리 중 ===")
                        
                        # 각 변수에 대해 구분자 추가
                        for original_text, replacement in variable_mappings.items():
                            if original_text in content_str:
                                content_str = content_str.replace(original_text, replacement)
                                print(f"✓ {original_text} -> {replacement}")
                        
                        # 변경사항이 있는지 확인
                        if content_str != original_content:
                            print(f"✅ 템플릿에 구분자 추가 완료")
                        else:
                            print(f"⚠️  변경사항 없음 (변수를 찾을 수 없음)")
                        
                        # 변경된 내용을 다시 바이트로 변환
                        content = content_str.encode('utf-8')
                    
                    # 파일 쓰기
                    zip_write.writestr(file_info, content)
        
        print(f"\n🎉 템플릿 수정 완료: {fixed_template}")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == '__main__':
    add_delimiters_to_template()
