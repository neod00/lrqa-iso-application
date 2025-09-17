#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# JavaScript 코드의 깨진 부분들을 간단하게 수정
# 로그인 이벤트 리스너 수정
content = re.sub(
    r"document\.getElementById\('viewContent'\)\.addEventListener\('.*?', function\(e\) \{",
    "document.getElementById('loginForm').addEventListener('submit', function(e) {",
    content
)

# getElementById 호출들 수정
content = re.sub(
    r"document\.getElementById\('viewContent'\)\.value",
    "document.getElementById('username').value",
    content
)

# 두 번째 getElementById 호출 수정
content = re.sub(
    r"document\.getElementById\('viewContent'\)\.value",
    "document.getElementById('password').value",
    content
)

# 로그인 조건 수정
content = re.sub(
    r"if \(username === '.*?' && password === '.*?'\) \{",
    "if (username === 'admin' && password === 'lrqa2025') {",
    content
)

# 로그인 성공 시 처리 수정
content = re.sub(
    r"document\.getElementById\('viewContent'\)\.style\.display = 'block';",
    "document.getElementById('loginSection').style.display = 'none';",
    content
)

content = re.sub(
    r"document\.getElementById\('viewContent'\)\.classList\.add\('.*?'\);",
    "document.getElementById('adminContent').classList.add('authenticated');",
    content
)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JavaScript 코드 간단 수정 완료")
