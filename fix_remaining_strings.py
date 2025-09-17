#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 남은 깨진 문자열들을 올바른 문자열로 교체
replacements = [
    # showMessage 함수 호출들
    (r"showMessage\('신청시', '신청시'\);", "showMessage('처리 중입니다...', 'info');"),
    (r"showMessage\('신청시', 'error'\);", "showMessage('오류가 발생했습니다.', 'error');"),
    (r"showMessage\('신청시', 'success'\);", "showMessage('성공적으로 처리되었습니다.', 'success');"),
    (r"showMessage\('신청시', 'info'\);", "showMessage('처리 중입니다...', 'info');"),
    
    # console.error 메시지들
    (r"console\.error\('신청시', error\);", "console.error('오류 발생:', error);"),
    (r"console\.error\('신청시', error\);", "console.error('오류 발생:', error);"),
    
    # innerHTML 설정들
    (r"tbody\.innerHTML = '신청시';", "tbody.innerHTML = '<tr><td colspan=\"7\">데이터를 불러오는 중입니다...</td></tr>';"),
    (r"tbody\.innerHTML = '신청시';", "tbody.innerHTML = '<tr><td colspan=\"7\">데이터를 불러오는 중입니다...</td></tr>';"),
    
    # style.display 설정들
    (r"\.style\.display = '신청시';", ".style.display = 'block';"),
    (r"\.style\.display = '신청시';", ".style.display = 'block';"),
    
    # 객체 속성 접근들
    (r"app\['신청시'\]", "app['신청시']"),
    (r"app\['신청시'\]", "app['신청시']"),
    
    # 기타 깨진 문자열들
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
]

# 각 교체 작업 수행
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 추가로 특정 패턴들을 수정
# showMessage 함수 호출들
content = re.sub(r"showMessage\('신청시', '신청시'\);", "showMessage('처리 중입니다...', 'info');", content)
content = re.sub(r"showMessage\('신청시', 'error'\);", "showMessage('오류가 발생했습니다.', 'error');", content)
content = re.sub(r"showMessage\('신청시', 'success'\);", "showMessage('성공적으로 처리되었습니다.', 'success');", content)
content = re.sub(r"showMessage\('신청시', 'info'\);", "showMessage('처리 중입니다...', 'info');", content)

# console.error 메시지들
content = re.sub(r"console\.error\('신청시', error\);", "console.error('오류 발생:', error);", content)

# innerHTML 설정들
content = re.sub(r"tbody\.innerHTML = '신청시';", "tbody.innerHTML = '<tr><td colspan=\"7\">데이터를 불러오는 중입니다...</td></tr>';", content)

# style.display 설정들
content = re.sub(r"\.style\.display = '신청시';", ".style.display = 'block';", content)

# 객체 속성 접근들
content = re.sub(r"app\['신청시'\]", "app['신청시']", content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("남은 깨진 문자열 수정 완료")
