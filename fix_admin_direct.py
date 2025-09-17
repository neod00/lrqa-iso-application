#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 관리자 헤더 부분의 깨진 한글 텍스트를 직접 수정
content = content.replace(
    '<h1>LRQA 愿由ъ옄 ?占쎌젙</h1>',
    '<h1>LRQA 관리자 시스템</h1>'
)

content = content.replace(
    '<p>ISO ?占쎌쬆?占쎌궗 ?占쎌껌??愿占??占쎌뒪??/p>',
    '<p>ISO 인증심사 신청서 관리 시스템</p>'
)

content = content.replace(
    '濡쒓렇?占쎌썐',
    '로그아웃'
)

# 탭 버튼들 수정
content = content.replace(
    '?占?占쎈낫??/button>',
    '대시보드</button>'
)

content = content.replace(
    '?占쎌껌??紐⑸줉</button>',
    '신청서 목록</button>'
)

content = content.replace(
    '?占쎌씠???占쎈낫?占쎄 린</button>',
    '보고서 보기</button>'
)

# 통계 카드들 수정
content = content.replace(
    '占??占쎌껌??/div>',
    '총 신청서</div>'
)

content = content.replace(
    '?占쎄퇋 ?占쎌껌??/div>',
    '신규 신청서</div>'
)

content = content.replace(
    '?占쎈떖???占쎌껌??/div>',
    '이번 달 신청서</div>'
)

content = content.replace(
    '?占쎈즺???占쎌껌??/div>',
    '완료된 신청서</div>'
)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("관리자 대시보드 한글 텍스트 직접 수정 완료")
