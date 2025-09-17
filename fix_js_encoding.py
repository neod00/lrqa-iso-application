#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# JavaScript 부분의 한글 텍스트 수정
# 1. 인증 상태 확인 주석 수정
content = re.sub(
    r'// \?증 \?태 \?인',
    '// 인증 상태 확인',
    content
)

# 2. 간단한 인증 주석 수정
content = re.sub(
    r'// 간단\?\?\?\?증.*?방법 \?용\)',
    '// 간단한 인증 (실제 환경에서는 보안 방법 사용)',
    content
)

# 3. 로그아웃 주석 수정
content = re.sub(
    r'// 로그\?웃',
    '// 로그아웃',
    content
)

# 4. alert 메시지 수정
content = re.sub(
    r"alert\('로그\?\?\?\?보가 \?바르\? \?습\?다\.'\);",
    "alert('로그인 정보가 올바르지 않습니다.');",
    content
)

# 5. 기타 한글 텍스트 수정
content = re.sub(
    r'// \?마 \?\?\? 버튼',
    '// 다크 모드 버튼',
    content
)

content = re.sub(
    r'// 모든 \?\?비활\?화',
    '// 모든 탭 비활성화',
    content
)

content = re.sub(
    r'// \?\?환',
    '// 탭 전환',
    content
)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JavaScript 한글 텍스트 수정 완료")
