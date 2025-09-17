#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# admin.html 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 신청서 목록 테이블에 견적서 버튼 추가
quotation_button = """
                            <button class="action-btn quote" onclick="generateQuotation('${app['신청일시']}')">견적서</button>
"""

# 기존 액션 버튼들 뒤에 견적서 버튼 추가
content = content.replace(
    '                            <button class="action-btn edit" onclick="editApplication(\'${app[\'신청일시\']}\')">수정</button>\n                        </div>',
    '                            <button class="action-btn edit" onclick="editApplication(\'${app[\'신청일시\']}\')">수정</button>\n' + quotation_button + '                        </div>'
)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("견적서 버튼 추가 완료")
