#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# 탭 버튼들의 깨진 한글 텍스트 수정
for i, line in enumerate(lines):
    # 대시보드 탭
    if '?占?占쎈낫??/button>' in line and 'admin-tab active' in line:
        lines[i] = '                <button class="admin-tab active" onclick="showTab(\'dashboard\')">대시보드</button>\n'
    
    # 신청서 목록 탭
    elif '?占쎌껌??紐⑸줉</button>' in line and 'admin-tab' in line:
        lines[i] = '                <button class="admin-tab" onclick="showTab(\'applications\')">신청서 목록</button>\n'
    
    # 보고서 보기 탭
    elif '?占쎌씠???占쎈낫?占쎄 린</button>' in line and 'admin-tab' in line:
        lines[i] = '                <button class="admin-tab" onclick="showTab(\'reports\')">보고서 보기</button>\n'

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("탭 버튼 한글 텍스트 수정 완료")
