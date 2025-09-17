#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# JavaScript 코드의 깨진 부분들을 수정
replacements = [
    # 로그인 이벤트 리스너 수정
    (r"document\.getElementById\('viewContent'\)\.addEventListener\('?좎껌??, function\(e\) \{", 
     "document.getElementById('loginForm').addEventListener('submit', function(e) {"),
    
    # getElementById 호출들 수정
    (r"document\.getElementById\('viewContent'\)\.value", "document.getElementById('username').value"),
    (r"document\.getElementById\('viewContent'\)\.value", "document.getElementById('password').value"),
    
    # 로그인 조건 수정
    (r"if \(username === '\?좎껌?? && password === '\?좎껌??\) \{", 
     "if (username === 'admin' && password === 'lrqa2025') {"),
    
    # 로그인 성공 시 처리 수정
    (r"document\.getElementById\('viewContent'\)\.style\.display = 'block';", 
     "document.getElementById('loginSection').style.display = 'none';"),
    (r"document\.getElementById\('viewContent'\)\.classList\.add\('\?좎껌??\);", 
     "document.getElementById('adminContent').classList.add('authenticated');"),
    
    # 주석 수정
    (r"// 媛꾨떒???占쎌쬆.*?諛⑸쾿 \?占쎌슜\)", 
     "// 간단한 인증 (실제 환경에서는 보안 방법 사용)"),
    
    # 로그아웃 주석 수정
    (r"// 濡쒓렇\?占쎌썐", "// 로그아웃"),
]

# 각 교체 작업 수행
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JavaScript 코드 완전 수정 완료")
