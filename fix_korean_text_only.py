#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 한글 텍스트만 수정 (디자인은 그대로 유지)
replacements = [
    # title 태그
    (r'<title>LRQA 관리자 \?쒖뒪\?\?/title>', '<title>LRQA 관리자 시스템</title>'),
    
    # 다크모드 버튼
    (r'<span class="theme-toggle-icon">\?</span>', '<span class="theme-toggle-icon">🌙</span>'),
    (r'<span class="theme-toggle-text">\?크모드</span>', '<span class="theme-toggle-text">다크모드</span>'),
    
    # 로그인 섹션
    (r'<h2 style="text-align: center; margin-bottom: 30px;">LRQA 관리자 로그\?\?/h2>', '<h2 style="text-align: center; margin-bottom: 30px;">LRQA 관리자 로그인</h2>'),
    (r'placeholder="\?ъ슜\?먮챸"', 'placeholder="사용자명"'),
    (r'placeholder="\?밀번호"', 'placeholder="비밀번호"'),
    (r'로그\?\?/button>', '로그인</button>'),
    
    # 관리자 헤더
    (r'<h1>LRQA 관리자 \?정</h1>', '<h1>LRQA 관리자 시스템</h1>'),
    (r'<p>ISO \?증\?사 \?청\?\?관\?\?\?스\?\?/p>', '<p>ISO 인증심사 신청서 관리 시스템</p>'),
    (r'로그\?웃', '로그아웃'),
    
    # 탭 버튼들
    (r'\?보\?\?/button>', '대시보드</button>'),
    (r'\?청\?\?목록</button>', '신청서 목록</button>'),
    (r'\?이\?\?\?\?보\?기</button>', '보고서 보기</button>'),
    
    # 통계 카드들
    (r'\?\?청\?\?/div>', '총 신청서</div>'),
    (r'\?규 \?청\?\?/div>', '신규 신청서</div>'),
    (r'\?달\?\?\?청\?\?/div>', '이번 달 신청서</div>'),
    (r'\?료\?\?\?청\?\?/div>', '완료된 신청서</div>'),
    
    # 기타 텍스트들
    (r'\?이\?\?\?\?로고침', '데이터 새로고침'),
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

print("기존 디자인 유지하면서 한글 텍스트만 수정 완료")
