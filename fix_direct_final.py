#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 파일을 UTF-8로 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 정확한 문자열 교체
content = content.replace('LRQA 관리자 🌙정', 'LRQA 관리자 시스템')
content = content.replace('LRQA 관리자 로그인', 'LRQA 관리자 로그인')
content = content.replace('ISO 🌙증🌙사 🌙청🌙🌙관🌙🌙스🌙🌙', 'ISO 인증심사 신청서 관리 시스템')
content = content.replace('로그인/button>', '로그인</button>')
content = content.replace('로그🌙웃', '로그아웃')
content = content.replace('🌙보🌙🌙', '대시보드')
content = content.replace('🌙청🌙🌙목록', '신청서 목록')
content = content.replace('🌙이🌙🌙🌙보🌙기', '보고서 보기')
content = content.replace('🌙🌙청🌙🌙', '총 신청서')
content = content.replace('🌙규 🌙청🌙🌙', '신규 신청서')
content = content.replace('🌙달🌙🌙🌙청🌙🌙', '이번 달 신청서')
content = content.replace('🌙료🌙🌙🌙청🌙🌙', '완료된 신청서')
content = content.replace('🌙이🌙🌙🌙로고침', '데이터 새로고침')
content = content.replace('🌙용🌙명', '사용자명')
content = content.replace('비🌙번호', '비밀번호')
content = content.replace('🌙크모드', '다크모드')

# 파일을 UTF-8로 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("최종 한글 텍스트 수정 완료")