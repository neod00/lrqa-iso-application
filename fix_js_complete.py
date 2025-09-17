#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# JavaScript 부분의 모든 한글 텍스트 수정
replacements = [
    # 주석 수정
    (r'// \?占쎌쬆 \?占쏀깭 \?占쎌씤', '// 인증 상태 확인'),
    (r'// 濡쒓렇\?\?섎━', '// 로그인 처리'),
    (r'// 濡쒓렇\?웃', '// 로그아웃'),
    (r'// \?占쎌쬆 \?占쏀깭 \?占쏀깭', '// 간단한 인증'),
    (r'// \?占쎌쬆 \?占쏀깭 \?占쏀깭.*?방법 \?용\)', '// 간단한 인증 (실제 환경에서는 보안 방법 사용)'),
    (r'// \?占쎌쬆 \?占쏀깭 \?占쏀깭.*?방법 \?용\)', '// 간단한 인증 (실제 환경에서는 보안 방법 사용)'),
    
    # alert 메시지 수정
    (r"alert\('濡쒓렇\?\?\?\?보가 \?바르\? \?습\?다\.'\);", "alert('로그인 정보가 올바르지 않습니다.');"),
    
    # 기타 한글 텍스트 수정
    (r'// \?占쎌쬆 \?\?\? \?占쏀깭', '// 다크 모드 버튼'),
    (r'// \?占쎌쬆 \?占쏀깭 \?占쏀깭', '// 모든 탭 비활성화'),
    (r'// \?\?환', '// 탭 전환'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JavaScript 한글 텍스트 완전 수정 완료")
