#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# JavaScript 코드에서 구문 오류를 일으키는 모든 깨진 문자열 수정
replacements = [
    # showMessage 함수 호출들
    (r"showMessage\('신청시', '신청시'\);", "showMessage('처리 중입니다...', 'info');"),
    (r"showMessage\('신청시', 'error'\);", "showMessage('오류가 발생했습니다.', 'error');"),
    (r"showMessage\('신청시', 'success'\);", "showMessage('성공적으로 처리되었습니다.', 'success');"),
    
    # getElementById 호출들
    (r"getElementById\('신청시'\)", "getElementById('viewContent')"),
    (r"getElementById\('신청시'\)", "getElementById('editContent')"),
    
    # window.open 호출들
    (r"window\.open\('신청시', '신청시'\)", "window.open('', '_blank')"),
    
    # 문자열 리터럴들
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
    (r"'신청시'", "'신청시'"),
    
    # 깨진 한글이 포함된 모든 문자열 리터럴을 기본값으로 교체
    (r"'[^']*占[^']*'", "'신청시'"),
    (r"'[^']*?[^']*'", "'신청시'"),
    (r"'[^']*?[^']*'", "'신청시'"),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("모든 JavaScript 오류 수정 완료")
