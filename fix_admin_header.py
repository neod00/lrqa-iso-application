#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# 관리자 헤더 부분의 깨진 한글 텍스트 수정
for i, line in enumerate(lines):
    # h1 태그 수정
    if '<h1>LRQA' in line and '愿由ъ옄' in line:
        lines[i] = '                <h1>LRQA 관리자 시스템</h1>\n'
    
    # p 태그 수정
    elif '<p>ISO' in line and '?占쎌쬆' in line:
        lines[i] = '                <p>ISO 인증심사 신청서 관리 시스템</p>\n'
    
    # 로그아웃 버튼 수정
    elif '濡쒓렇?占쎌썐' in line:
        lines[i] = lines[i].replace('濡쒓렇?占쎌썐', '로그아웃')

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("관리자 헤더 한글 텍스트 수정 완료")
