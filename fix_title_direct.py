#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# title 라인 찾아서 수정
for i, line in enumerate(lines):
    if '<title>' in line and 'LRQA' in line:
        lines[i] = '    <title>LRQA 관리자 시스템</title>\n'
        break

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("title 태그 직접 수정 완료")
