#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 로그인 섹션 수정
# 1. h2 태그 수정
content = re.sub(
    r'<h2 style="text-align: center; margin-bottom: 30px;">LRQA 관리자 로그.*?</h2>',
    '<h2 style="text-align: center; margin-bottom: 30px;">LRQA 관리자 로그인</h2>',
    content
)

# 2. 사용자명 placeholder 수정
content = re.sub(
    r'placeholder="[^"]*용[^"]*명[^"]*"',
    'placeholder="사용자명"',
    content
)

# 3. 비밀번호 placeholder 수정
content = re.sub(
    r'placeholder="[^"]*비[^"]*번호[^"]*"',
    'placeholder="비밀번호"',
    content
)

# 4. 로그인 버튼 수정
content = re.sub(
    r'<button type="submit" class="login-btn">로그.*?</button>',
    '<button type="submit" class="login-btn">로그인</button>',
    content
)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("로그인 섹션 수정 완료")
