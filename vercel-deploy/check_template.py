import zipfile

def check_template():
    z = zipfile.ZipFile('public/templates/LRQA_quotation.docx', 'r')
    content = z.read('word/document.xml').decode('utf-8')
    
    print('템플릿 내용에서 {{ }} 검색:')
    print('{{ quotation_date }}' in content)
    print('{{ client_name }}' in content)
    print('{{ has_iso14001 }}' in content)
    
    print('\n템플릿 내용에서 {{ 포함 부분:')
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '{{' in line:
            print(f'라인 {i}: {line.strip()}')
    
    print('\n총 {{ 포함 라인 수:', sum(1 for line in lines if '{{' in line))

if __name__ == '__main__':
    check_template()
