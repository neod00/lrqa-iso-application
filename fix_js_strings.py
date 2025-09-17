#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# JavaScript 문자열 리터럴의 깨진 한글 수정
replacements = [
    # switch 문의 case 값들
    (r"case '\?占쎄퇋':", "case '신규':"),
    (r"case '진행占\?:", "case '진행중':"),
    (r"case '\?占쎈즺':", "case '완료':"),
    
    # 기타 깨진 한글 문자열들
    (r"'신청시'", "'신청시'"),
    (r"'법인명\(한글\)'", "'법인명(한글)'"),
    (r"'법인명\(영문\)'", "'법인명(영문)'"),
    (r"'대표자명'", "'대표자명'"),
    (r"'사업자등록번호'", "'사업자등록번호'"),
    (r"'주소'", "'주소'"),
    (r"'연락처'", "'연락처'"),
    (r"'이메일'", "'이메일'"),
    (r"'신청일'", "'신청일'"),
    (r"'상태'", "'상태'"),
    
    # 깨진 한글이 포함된 문자열들
    (r"'[^']*占[^']*'", "'신청시'"),
    (r"'[^']*?[^']*'", "'신청시'"),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JavaScript 문자열 리터럴 수정 완료")
