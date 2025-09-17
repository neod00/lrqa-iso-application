#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 모든 깨진 한글 텍스트를 올바른 한글로 교체
replacements = [
    # title 태그
    (r'<title>LRQA 愿由ъ옄 \?쒖뒪\?\?/title>', '<title>LRQA 관리자 시스템</title>'),
    
    # 다크모드 버튼
    (r'<span class="theme-toggle-icon">\?占쏙 옙</span>', '<span class="theme-toggle-icon">🌙</span>'),
    (r'<span class="theme-toggle-text">\?占쏀 겕\?⑤뱶</span>', '<span class="theme-toggle-text">다크모드</span>'),
    
    # CSS 주석들
    (r'/\* 愿由ъ옄 \?占쎌슜 \?占쏙옙\?\?\*/', '/* 관리자 사용 스타일 */'),
    (r'/\* 寃\?\?而⑦듃占\?\?占쏙옙\?\?\*/', '/* 검색 결과 스타일 */'),
    (r'/\* 寃\?\?寃곌낵 \?占쎌씠\?占쎌씠\?\?\*/', '/* 검색 결과 아이템 */'),
    (r'/\* 寃\?\?寃곌낵 \?占쎌쓬 \?占쏙옙\?\?\*/', '/* 검색 결과 하단 스타일 */'),
    (r'/\* \?占쎌씠\?占쎌씠\?\?\?占쏙옙\?\?\*/', '/* 아이템 스타일 */'),
    (r'/\* \?占쎌젙 \?⑤떖 \?占쏙옙\?\?\*/', '/* 설정 탭 스타일 */'),
    (r'/\* \?占쎌껌\?\?蹂닿린 \?⑤떖 \?占쏙옙\?\?\*/', '/* 신청서 목록 탭 스타일 */'),
    (r'/\* \?占쎌껌\?\?蹂닿린\?\?\?占쏙옙\?\?\*/', '/* 신청서 목록 스타일 */'),
    
    # 폰트 패밀리
    (r"font-family: '\?좎껌\?\?, Arial, sans-serif;", "font-family: 'Noto Sans KR', Arial, sans-serif;"),
    (r"content: '\?좎껌\?\?;", "content: '→';"),
    (r"background-image: url\('\?좎껌\?\?\);", "background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTggMTJMMTIgOEw4IDRMMTAgMkw2IDZMMTAgMTBaIiBmaWxsPSIjNjY2NjY2Ii8+Cjwvc3ZnPgo=');"),
    
    # 로그인 섹션
    (r'<!-- 濡쒓렇\?\?\?占쎌뀡 -->', '<!-- 로그인 섹션 -->'),
    (r'<h2 style="text-align: center; margin-bottom: 30px;">LRQA 愿由ъ옄 濡쒓렇\?\?/h2>', '<h2 style="text-align: center; margin-bottom: 30px;">LRQA 관리자 로그인</h2>'),
    (r'placeholder="\?ъ슜\?먮챸"', 'placeholder="사용자명"'),
    
    # 관리자 헤더
    (r'<h1>LRQA 愿由ъ옄 \?占쎌젙</h1>', '<h1>LRQA 관리자 시스템</h1>'),
    (r'<p>ISO \?占쎌쬆\?占쎌궗 \?占쎌껌\?\?愿占\?\?占쎌뒪\?\?/p>', '<p>ISO 인증심사 신청서 관리 시스템</p>'),
    (r'濡쒓렇\?占쎌썐', '로그아웃'),
    
    # 탭 버튼들
    (r'\?占\?占쎈낫\?\?/button>', '대시보드</button>'),
    (r'\?占쎌껌\?\?蹂닿린</button>', '신청서 목록</button>'),
    (r'\?占쎌씠\?\?\?占쎈낫\?占쎄 린</button>', '보고서 보기</button>'),
    
    # 통계 카드들
    (r'占\?\?占쎌껌\?\?/div>', '총 신청서</div>'),
    (r'\?占쎄퇋 \?占쎌껌\?\?/div>', '신규 신청서</div>'),
    (r'\?占쎈떖\?\?\?占쎌껌\?\?/div>', '이번 달 신청서</div>'),
    (r'\?占쎈즺\?\?\?占쎌껌\?\?/div>', '완료된 신청서</div>'),
    
    # 기타 깨진 텍스트들
    (r'신청시', '신청시'),
    (r'신청시', '신청시'),
    (r'신청시', '신청시'),
]

# 각 교체 작업 수행
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("모든 인코딩 문제로 인한 한글 깨짐 수정 완료")
