#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 정확한 문자로 수정
replacements = [
    # title 태그
    (r'<title>LRQA 愿由ъ옄 \?占쎌젙</title>', '<title>LRQA 관리자 시스템</title>'),
    
    # 관리자 헤더
    (r'<h1>LRQA 愿由ъ옄 \?占쎌젙</h1>', '<h1>LRQA 관리자 시스템</h1>'),
    (r'<p>ISO \?占쎌쬆\?占쎌궗 \?占쎌껌\?\?愿占\?\?占쎌뒪\?\?/p>', '<p>ISO 인증심사 신청서 관리 시스템</p>'),
    
    # 로그아웃 버튼
    (r'濡쒓렇\?占쎌썐', '로그아웃'),
    
    # 탭 버튼들
    (r'\?占쎌쬆\?占쏀깭\?\?/button>', '대시보드</button>'),
    (r'\?占쎌쬆\?占쏀깭\?\?목록</button>', '신청서 목록</button>'),
    (r'\?占쎌쬆\?占쎌쬆\?\?占쎌쬆\?占쏀깭\?占쎌쬆\?占쏀깭</button>', '보고서 보기</button>'),
    
    # 통계 카드들
    (r'총 \?占쎌쬆\?占쏀깭\?占쎌쬆', '총 신청서'),
    (r'\?占쎌쬆\?占쏀깭 \?占쎌쬆\?占쏀깭\?占쎌쬆', '대기 중 신청서'),
    (r'\?占쎌쬆\?占쏀깭\?占쎌쬆 \?占쎌쬆\?占쏀깭\?占쎌쬆', '완료된 신청서'),
    (r'이번 \?占쎌쬆\?占쏀깭', '이번 달'),
    
    # 버튼 텍스트들
    (r'\?占쎌쬆\?占쏀깭\?占쎌쬆 \?占쎌쬆\?占쏀깭\?占쎌쬆', '신청서 새로고침'),
]

# 각 교체 작업 수행
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("관리자 대시보드 한글 텍스트 정확 수정 완료")
