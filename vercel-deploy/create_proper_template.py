import zipfile
import os
import re
import shutil

def create_proper_template():
    """올바른 구분자가 포함된 템플릿을 생성합니다."""
    
    # 원본 템플릿에서 시작
    original_template = 'public/templates/LRQA_quotation_original.docx'
    new_template = 'public/templates/LRQA_quotation.docx'
    
    print(f"원본 템플릿: {original_template}")
    print(f"새 템플릿: {new_template}")
    
    if not os.path.exists(original_template):
        print(f"❌ 원본 템플릿을 찾을 수 없습니다: {original_template}")
        return False
    
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
            with zipfile.ZipFile(new_template, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                for file_info in zip_read.infolist():
                    content = zip_read.read(file_info.filename)
                    
                    # word/document.xml 파일인 경우 구분자 추가
                    if file_info.filename == "word/document.xml":
                        content_str = content.decode('utf-8')
                        original_content = content_str
                        
                        print(f"\n=== {file_info.filename} 처리 중 ===")
                        
                        # 템플릿 내용을 확인하고 변수 추가
                        # 먼저 템플릿에 변수 자리표시자를 추가
                        template_variables = [
                            'quotation_date', 'quotation_number', 'client_name', 
                            'client_address', 'contact_person', 'contact_email', 
                            'contact_phone', 'standards_text', 'total_sites', 
                            'total_employees', 'total_audit_days', 
                            'total_cost_with_travel_formatted', 'travel_expense_formatted',
                            'iso14001_surveillance_days', 'iso14001_stage1_2_days', 
                            'iso14001_stage1_2_cost_formatted', 'has_iso9001', 
                            'has_iso14001', 'has_iso45001'
                        ]
                        
                        # 각 변수에 대해 템플릿에 추가
                        for var in template_variables:
                            if var not in content_str:
                                # 변수를 템플릿에 추가 (간단한 형태로)
                                content_str = content_str.replace(
                                    '</w:document>', 
                                    f'<w:p><w:r><w:t>{{{{ {var} }}}}</w:t></w:r></w:p></w:document>'
                                )
                                print(f"✓ {var} 변수 추가")
                        
                        # 변경사항이 있는지 확인
                        if content_str != original_content:
                            print(f"✅ 템플릿에 변수 추가 완료")
                        else:
                            print(f"⚠️  변경사항 없음")
                        
                        # 변경된 내용을 다시 바이트로 변환
                        content = content_str.encode('utf-8')
                    
                    # 파일 쓰기
                    zip_write.writestr(file_info, content)
        
        print(f"\n🎉 템플릿 생성 완료: {new_template}")
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == '__main__':
    create_proper_template()
