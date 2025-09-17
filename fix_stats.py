#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# 통계 카드들의 깨진 한글 텍스트 수정
for i, line in enumerate(lines):
    # 총 신청서
    if '占??占쎌껌??/div>' in line and 'stat-label' in line:
        lines[i] = '                        <div class="stat-label">총 신청서</div>\n'
    
    # 신규 신청서
    elif '?占쎄퇋 ?占쎌껌??/div>' in line and 'stat-label' in line:
        lines[i] = '                        <div class="stat-label">신규 신청서</div>\n'
    
    # 이번 달 신청서
    elif '?占쎈떖???占쎌껌??/div>' in line and 'stat-label' in line:
        lines[i] = '                        <div class="stat-label">이번 달 신청서</div>\n'
    
    # 완료된 신청서
    elif '?占쎈즺???占쎌껌??/div>' in line and 'stat-label' in line:
        lines[i] = '                        <div class="stat-label">완료된 신청서</div>\n'

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("통계 카드 한글 텍스트 수정 완료")
