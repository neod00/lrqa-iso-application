#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 깨진 한글 문자열들을 올바른 문자열로 교체
replacements = [
    # alert 메시지들
    (r"alert\('신청시'\);", "alert('로그인 정보가 올바르지 않습니다.');"),
    (r"alert\('신청시'\);", "alert('신청서가 성공적으로 저장되었습니다.');"),
    
    # showMessage 함수 호출들
    (r"showMessage\('신청시', 'info'\);", "showMessage('처리 중입니다...', 'info');"),
    (r"showMessage\('신청시', 'error'\);", "showMessage('오류가 발생했습니다.', 'error');"),
    (r"showMessage\('신청시', 'success'\);", "showMessage('성공적으로 처리되었습니다.', 'success');"),
    
    # getElementById 호출들
    (r"getElementById\('신청시'\)", "getElementById('viewContent')"),
    (r"getElementById\('신청시'\)", "getElementById('editContent')"),
    (r"getElementById\('신청시'\)", "getElementById('applicationsTableBody')"),
    
    # window.open 호출들
    (r"window\.open\('신청시', '신청시'\)", "window.open('', '_blank')"),
    (r"window\.open\('신청시', '_blank'\)", "window.open('', '_blank')"),
    
    # 문자열 리터럴들
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
    
    # 깨진 한글이 포함된 모든 문자열 리터럴을 기본값으로 교체
    (r"'[^']*占[^']*'", "'신청시'"),
    (r"'[^']*?[^']*'", "'신청시'"),
    (r"'[^']*?[^']*'", "'신청시'"),
    
    # console.log 메시지들
    (r"console\.log\('신청시',", "console.log('신청서 데이터:',"),
    (r"console\.log\('신청시'\);", "console.log('신청서 처리 완료');"),
    
    # 기타 깨진 문자열들
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
]

# 각 교체 작업 수행
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 추가로 깨진 문자열들을 찾아서 수정
# alert 메시지들
content = re.sub(r"alert\('신청시'\);", "alert('로그인 정보가 올바르지 않습니다.');", content)
content = re.sub(r"alert\('신청시'\);", "alert('신청서가 성공적으로 저장되었습니다.');", content)

# showMessage 함수 호출들
content = re.sub(r"showMessage\('신청시', 'info'\);", "showMessage('처리 중입니다...', 'info');", content)
content = re.sub(r"showMessage\('신청시', 'error'\);", "showMessage('오류가 발생했습니다.', 'error');", content)
content = re.sub(r"showMessage\('신청시', 'success'\);", "showMessage('성공적으로 처리되었습니다.', 'success');", content)

# getElementById 호출들
content = re.sub(r"getElementById\('신청시'\)", "getElementById('viewContent')", content)
content = re.sub(r"getElementById\('신청시'\)", "getElementById('editContent')", content)
content = re.sub(r"getElementById\('신청시'\)", "getElementById('applicationsTableBody')", content)

# window.open 호출들
content = re.sub(r"window\.open\('신청시', '신청시'\)", "window.open('', '_blank')", content)
content = re.sub(r"window\.open\('신청시', '_blank'\)", "window.open('', '_blank')", content)

# console.log 메시지들
content = re.sub(r"console\.log\('신청시',", "console.log('신청서 데이터:',", content)
content = re.sub(r"console\.log\('신청시'\);", "console.log('신청서 처리 완료');", content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("모든 깨진 한글 문자열 수정 완료")
